from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import logging

from .models import (
    Role, Permission, User,
    PassengerCar, NormsPassengerCars, PassengerCarWaybill,
    PassengerCarWaybillRecord, OdometerFuelPassengerCar,
    FireTruck, NormsFireTruck, FireTruckWaybill,
    FireTruckWaybillRecord, OdometerFuelFireTruck,

    OperatingHoursCars,
    NormsOperatingHoursPassengerCar,
    NormsOperatingHoursFireTruck,
    TechnicalMaintenance,
    NormsTechnicalMaintenance,
)

logger = logging.getLogger(__name__)


class FriendlyModelSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор с дружелюбными русскими сообщениями.
    """
    def get_fields(self):
        fields = super().get_fields()

        for field_name, field in fields.items():
            field.error_messages.setdefault('required', 'Поле обязательно для заполнения.')
            field.error_messages.setdefault('blank', 'Поле обязательно для заполнения.')
            field.error_messages.setdefault('null', 'Поле обязательно для заполнения.')
            field.error_messages.setdefault('invalid', 'Введите корректное значение.')

            max_length = getattr(field, 'max_length', None)
            if max_length:
                field.error_messages['max_length'] = f'Длина поля ограничена {max_length} символами.'

            for validator in field.validators:
                if isinstance(validator, UniqueValidator):
                    validator.message = 'Запись с таким значением уже существует.'
                elif isinstance(validator, MaxLengthValidator):
                    validator.message = f'Длина поля ограничена {validator.limit_value} символами.'
                elif isinstance(validator, MinValueValidator):
                    validator.message = f'Значение не должно быть меньше {validator.limit_value}.'
                elif isinstance(validator, MaxValueValidator):
                    validator.message = f'Значение не должно превышать {validator.limit_value}.'

        return fields


# ---------- БАЗОВЫЕ СУЩНОСТИ ----------

class RoleSerializer(FriendlyModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class PermissionSerializer(FriendlyModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(FriendlyModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Пароль обязателен только при создании (когда instance=None)
        if self.instance is not None:
            self.fields['password'].required = False

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


# ---------- ЛЕГКОВЫЕ ----------

class PassengerCarSerializer(FriendlyModelSerializer):
    odometer_fuel_records = serializers.SerializerMethodField()
    technical_maintenance_norm = serializers.SerializerMethodField()
    hours_until_maintenance = serializers.SerializerMethodField()
    maintenance_info = serializers.SerializerMethodField()
    all_maintenance_info = serializers.SerializerMethodField()

    class Meta:
        model = PassengerCar
        fields = '__all__'

    def get_odometer_fuel_records(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_odometer') == 'true':
            records = obj.odometer_fuel_records.all()
            return OdometerFuelPassengerCarSerializer(records, many=True).data
        return None

    def get_technical_maintenance_norm(self, obj):
        """Получить норму технического обслуживания (часы)"""
        norm = NormsTechnicalMaintenance.objects.filter(passenger_car=obj).order_by('-date').first()
        if norm:
            return float(norm.norm)
        return 0.0

    def get_hours_until_maintenance(self, obj):
        """Вычислить часы до следующего ТО"""
        operating_hours_obj = OperatingHoursCars.objects.filter(passenger_car=obj, fire_truck__isnull=True).order_by('-id').first()
        norm_obj = NormsTechnicalMaintenance.objects.filter(passenger_car=obj).order_by('-date').first()
        
        if operating_hours_obj and norm_obj:
            operating_hours = float(operating_hours_obj.operating_hours)
            norm = float(norm_obj.norm)
            hours_until = norm - operating_hours
            return hours_until  # Может быть отрицательным если ТО уже должна была пройти
        return None

    def get_maintenance_info(self, obj):
        """Получить полную информацию о техническом обслуживании"""
        # Берем ПОСЛЕДНЮЮ СОЗДАННУЮ норму
        norm_obj = NormsTechnicalMaintenance.objects.filter(passenger_car=obj).order_by('-date').first()
        # Берем ПОСЛЕДНЮЮ запись из OperatingHoursCars для этой машины
        # Используем -id (а не -date) чтобы взять последнюю ДОБАВЛЕННУЮ запись
        operating_hours_obj = OperatingHoursCars.objects.filter(passenger_car=obj, fire_truck__isnull=True).order_by('-id').first()
        
        # Проверяем, что норма существует и имеет положительное значение
        if not norm_obj or norm_obj.norm <= 0:
            return {
                'maintenance_type': None,
                'interval': None,
                'norm_interval_value': None,
                'previous_maintenance_hours': None,
                'current_hours': float(operating_hours_obj.operating_hours) if operating_hours_obj else 0.0,
                'next_maintenance_at': None,
                'last_maintenance_date': None,
                'error': 'Норма технического обслуживания не установлена для этой машины'
            }
        
        last_maintenance = TechnicalMaintenance.objects.filter(
            passenger_car=obj, 
            maintenance_type=norm_obj.maintenance_type
        ).order_by('-date').first()
        
        current_hours = float(operating_hours_obj.operating_hours) if operating_hours_obj else 0.0
        interval_value = float(norm_obj.norm)  # Это интервал между ТО (например, 100 часов)
        
        # Часы проведения предыдущего ТО
        previous_hours = float(last_maintenance.operating_hours) if last_maintenance else 0.0
        
        # Следующее ТО должно быть на: previous_hours + интервал
        next_maintenance_at = previous_hours + interval_value
        
        # Часов осталось до следующего ТО
        hours_until_maintenance = next_maintenance_at - current_hours
        
        return {
            'maintenance_type': norm_obj.maintenance_type,
            'interval': hours_until_maintenance,  # Часов ДО следующего ТО (может быть отрицательным если уже пора)
            'norm_interval_value': interval_value,  # Интервал из нормы (пример: каждые 100 часов)
            'previous_maintenance_hours': previous_hours,  # На каких часах было ТО
            'current_hours': current_hours,
            'next_maintenance_at': next_maintenance_at,  # Абсолютное значение часов когда нужно ТО
            'last_maintenance_date': last_maintenance.date.isoformat() if last_maintenance else None,
        }

    def get_all_maintenance_info(self, obj):
        """Получить информацию по ВСЕМ видам ТО для этой машины"""
        logger.warning('\n' + '='*80)
        logger.warning(f'[PassengerCarSerializer.get_all_maintenance_info] НАЧАЛО')
        logger.warning(f'obj (машина) = {obj} (id={obj.id})')
        logger.warning('='*80)
        
        request = self.context.get('request')
        if not request or request.query_params.get('include_all_maintenance_info') != 'true':
            logger.warning('[get_all_maintenance_info] include_all_maintenance_info != true, возвращаем None')
            return None
        
        # Получить все нормы (уникальные по maintenance_type)
        all_norms = NormsTechnicalMaintenance.objects.filter(
            passenger_car=obj
        ).order_by('maintenance_type', '-date').distinct('maintenance_type')
        
        logger.warning(f'[get_all_maintenance_info] Найдено норм: {all_norms.count()}')
        
        if not all_norms:
            logger.warning('[get_all_maintenance_info] ❌ НЕТ НОРМ! Возвращаем ошибку')
            return {
                'error': 'Нет установленных норм технического обслуживания',
                'items': []
            }
        
        maintenance_items = []
        for norm_obj in all_norms:
            logger.warning(f'[get_all_maintenance_info] Обрабатываем норму: {norm_obj.maintenance_type}, norm={norm_obj.norm}')
            
            if norm_obj.norm <= 0:
                logger.warning(f'  ⚠️ norm <= 0, пропускаем')
                continue
                
            # Получить последнее ТО этого типа
            last_maintenance = TechnicalMaintenance.objects.filter(
                passenger_car=obj,
                maintenance_type=norm_obj.maintenance_type
            ).order_by('-date', '-id').first()
            
            if last_maintenance:
                logger.warning(f'  📋 Последнее ТО: дата={last_maintenance.date}, operating_hours={last_maintenance.operating_hours}')
            else:
                logger.warning(f'  ℹ️ Ещё не было ТО этого типа')
            
            interval_value = float(norm_obj.norm)
            last_hours = float(last_maintenance.operating_hours) if last_maintenance else 0.0
            
            logger.warning(f'  → last_hours={last_hours}, interval={interval_value}')
            
            maintenance_items.append({
                'maintenance_type': norm_obj.maintenance_type,
                'norm_interval_value': interval_value,
                'last_maintenance_hours': last_hours,
                'last_maintenance_date': last_maintenance.date.isoformat() if last_maintenance else None,
            })
        
        logger.warning(f'[get_all_maintenance_info] ГОТОВО. Возвращаем {len(maintenance_items)} видов ТО')
        logger.warning('='*80 + '\n')
        
        return {
            'items': maintenance_items,
            'error': None
        }


class NormsPassengerCarsSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsPassengerCars
        fields = '__all__'


class OdometerFuelPassengerCarSerializer(FriendlyModelSerializer):
    class Meta:
        model = OdometerFuelPassengerCar
        fields = '__all__'


class PassengerCarWaybillSerializer(FriendlyModelSerializer):
    driver_full_name = serializers.SerializerMethodField()
    car_name = serializers.SerializerMethodField()
    car_number = serializers.SerializerMethodField()
    car_brand = serializers.SerializerMethodField()
    car_model = serializers.SerializerMethodField()
    vehicleType = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    total_operating_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = PassengerCarWaybill
        fields = '__all__'
        read_only_fields = [
            'number',
            'upon_issuance',
            'total_spent',
            'total_received',
            'required_by_norm',
            'availability_upon_delivery',
            'savings',
            'overrun',
            'driver_full_name',
            'car_name',
            'car_number',
            'car_brand',
            'car_model',
            'vehicleType',
            'records',
            'total_operating_hours',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если это редактирование существующего путевого листа и он не editable - заблокировать date
        # (Skip if many=True, since self.instance will be a queryset)
        if self.instance and hasattr(self.instance, 'is_editable'):
            if not self.instance.is_editable():
                self.fields['date'].read_only = True
    
    def get_driver_full_name(self, obj):
        if obj.driver:
            return f"{obj.driver.surname} {obj.driver.name} {obj.driver.last_name}".strip()
        return None
    
    def get_car_name(self, obj):
        if obj.car:
            return f"{obj.car.brand} {obj.car.model}".strip()
        return 'Легковой автомобиль'
    
    def get_car_number(self, obj):
        if obj.car:
            return obj.car.number
        return 'Без номера'
    
    def get_car_brand(self, obj):
        if obj.car:
            return obj.car.brand
        return None
    
    def get_car_model(self, obj):
        if obj.car:
            return obj.car.model
        return None
    
    def get_vehicleType(self, obj):
        return 'passenger_car'
    
    def get_records(self, obj):
        """Получить записи путевого листа с operating_hours"""
        request = self.context.get('request')
        include_records = request.query_params.get('include_records', 'false').lower() == 'true' if request else False
        
        if include_records:
            records = obj.records.all().order_by('-id')
            return PassengerCarWaybillRecordSerializer(records, many=True, context=self.context).data
        return None
    
    def get_total_operating_hours(self, obj):
        """Получить сумму моточасов со всех записей путевого листа"""
        from django.db.models import Sum
        total = (
            PassengerCarWaybillRecord.objects
            .filter(passenger_car_waybill=obj)
            .select_related('operating_hours_record')
            .aggregate(
                total_hours=Sum('operating_hours_record__operating_hours')
            )['total_hours']
        ) or 0
        return float(total)
    
    def to_representation(self, instance):
        """
        Опционально инклюдить инфо о машине и записи если проскан доп параметр
        """
        data = super().to_representation(instance)
        
        request = self.context.get('request')
        include_car = request.query_params.get('include_car', 'false').lower() == 'true' if request else False
        
        if not include_car:
            # Удаляем поля о машине если параметр не указан
            data.pop('car_name', None)
            data.pop('car_number', None)
            data.pop('car_brand', None)
            data.pop('car_model', None)
            data.pop('vehicleType', None)
        
        # Удаляем records если они None (параметр не был передан)
        if data.get('records') is None:
            data.pop('records', None)
        
        return data

    def validate(self, data):
        """
        Проверяем, что нет уже существующего путевого листа 
        для этой машины, водителя и даты
        """
        car = data.get('car')
        driver = data.get('driver')
        date = data.get('date')
        
        if car and driver and date:
            # Для обновления исключаем текущий объект
            query = PassengerCarWaybill.objects.filter(
                car=car,
                driver=driver,
                date=date,
                deleted_at__isnull=True
            )
            
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                driver_full_name = f"{driver.surname} {driver.name} {driver.last_name}".strip()
                raise serializers.ValidationError(
                    f"Путевой лист для машины {car.number}, "
                    f"водителя {driver_full_name} "
                    f"и даты {date.strftime('%d.%m.%Y')} уже существует."
                )
        
        return data


class PassengerCarWaybillRecordSerializer(FriendlyModelSerializer):
    operating_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = PassengerCarWaybillRecord
        fields = '__all__'
        read_only_fields = [
            'fuel_before_departure',
            'odometer_before',
            'distance_total_km',
            'fuel_used_city',
            'fuel_used_area',
            'fuel_on_return',
            'fuel_used_normal',
            'operating_hours',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если это редактирование существующей записи, проверяем, editable ли она
        if self.instance:
            # Проверяем через родительский путевой лист
            if hasattr(self.instance, 'passenger_car_waybill'):
                waybill = self.instance.passenger_car_waybill
                if not waybill.is_editable():
                    # Запретить редактирование полей расчётов
                    self.fields['fuel_refueled'].read_only = True
                    self.fields['fuel_used'].read_only = True
                    self.fields['odometer_after'].read_only = True
                    self.fields['distance_city_km'].read_only = True
                    self.fields['distance_area_km'].read_only = True
    
    def get_operating_hours(self, obj):
        """Получить часы из связанной OperatingHoursCars записи"""
        if obj.operating_hours_record:
            return float(obj.operating_hours_record.operating_hours)
        return 0.0


# ---------- ПОЖАРНЫЕ ----------

class FireTruckSerializer(FriendlyModelSerializer):
    odometer_fuel_records = serializers.SerializerMethodField()
    technical_maintenance_norm = serializers.SerializerMethodField()
    hours_until_maintenance = serializers.SerializerMethodField()
    maintenance_info = serializers.SerializerMethodField()
    all_maintenance_info = serializers.SerializerMethodField()

    class Meta:
        model = FireTruck
        fields = '__all__'

    def get_odometer_fuel_records(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_odometer') == 'true':
            records = obj.odometer_fuel_records.all()
            return OdometerFuelFireTruckSerializer(records, many=True).data
        return None

    def get_technical_maintenance_norm(self, obj):
        """Получить норму технического обслуживания (часы)"""
        norm = NormsTechnicalMaintenance.objects.filter(fire_truck=obj).order_by('-date').first()
        if norm:
            return float(norm.norm)
        return 0.0

    def get_hours_until_maintenance(self, obj):
        """Вычислить часы до следующего ТО"""
        operating_hours_obj = OperatingHoursCars.objects.filter(fire_truck=obj, passenger_car__isnull=True).order_by('-id').first()
        norm_obj = NormsTechnicalMaintenance.objects.filter(fire_truck=obj).order_by('-date').first()
        
        if operating_hours_obj and norm_obj:
            operating_hours = float(operating_hours_obj.operating_hours)
            norm = float(norm_obj.norm)
            hours_until = norm - operating_hours
            return hours_until  # Может быть отрицательным если ТО уже должна была пройти
        return None

    def get_maintenance_info(self, obj):
        """Получить полную информацию о техническом обслуживании"""
        # Берем ПОСЛЕДНЮЮ СОЗДАННУЮ норму
        norm_obj = NormsTechnicalMaintenance.objects.filter(fire_truck=obj).order_by('-date').first()
        # Берем ПОСЛЕДНЮЮ запись из OperatingHoursCars для этой машины (по ID - последняя добавленная)
        operating_hours_obj = OperatingHoursCars.objects.filter(fire_truck=obj, passenger_car__isnull=True).order_by('-id').first()
        
        # Проверяем, что норма существует и имеет положительное значение
        if not norm_obj or norm_obj.norm <= 0:
            return {
                'maintenance_type': None,
                'interval': None,
                'norm_interval_value': None,
                'previous_maintenance_hours': None,
                'current_hours': float(operating_hours_obj.operating_hours) if operating_hours_obj else 0.0,
                'next_maintenance_at': None,
                'last_maintenance_date': None,
                'error': 'Норма технического обслуживания не установлена для этой машины'
            }
        
        last_maintenance = TechnicalMaintenance.objects.filter(
            fire_truck=obj, 
            maintenance_type=norm_obj.maintenance_type
        ).order_by('-date').first()
        
        current_hours = float(operating_hours_obj.operating_hours) if operating_hours_obj else 0.0
        interval_value = float(norm_obj.norm)  # Это интервал между ТО (например, 100 часов)
        
        # Часы проведения предыдущего ТО
        previous_hours = float(last_maintenance.operating_hours) if last_maintenance else 0.0
        
        # Следующее ТО должно быть на: previous_hours + интервал
        next_maintenance_at = previous_hours + interval_value
        
        # Часов осталось до следующего ТО
        hours_until_maintenance = next_maintenance_at - current_hours
        
        return {
            'maintenance_type': norm_obj.maintenance_type,
            'interval': hours_until_maintenance,  # Часов ДО следующего ТО (может быть отрицательным если уже пора)
            'norm_interval_value': interval_value,  # Интервал из нормы (пример: каждые 100 часов)
            'previous_maintenance_hours': previous_hours,  # На каких часах было ТО
            'current_hours': current_hours,
            'next_maintenance_at': next_maintenance_at,  # Абсолютное значение часов когда нужно ТО
            'last_maintenance_date': last_maintenance.date.isoformat() if last_maintenance else None,
        }

    def get_all_maintenance_info(self, obj):
        """Получить информацию по ВСЕМ видам ТО для этой машины"""
        request = self.context.get('request')
        if not request or request.query_params.get('include_all_maintenance_info') != 'true':
            return None
        
        # Получить все нормы (уникальные по maintenance_type)
        all_norms = NormsTechnicalMaintenance.objects.filter(
            fire_truck=obj
        ).order_by('maintenance_type', '-date').distinct('maintenance_type')
        
        if not all_norms:
            return {
                'error': 'Нет установленных норм технического обслуживания',
                'items': []
            }
        
        maintenance_items = []
        for norm_obj in all_norms:
            if norm_obj.norm <= 0:
                continue
                
            # Получить последнее ТО этого типа
            last_maintenance = TechnicalMaintenance.objects.filter(
                fire_truck=obj,
                maintenance_type=norm_obj.maintenance_type
            ).order_by('-date', '-id').first()
            
            interval_value = float(norm_obj.norm)
            last_hours = float(last_maintenance.operating_hours) if last_maintenance else 0.0
            
            maintenance_items.append({
                'maintenance_type': norm_obj.maintenance_type,
                'norm_interval_value': interval_value,
                'last_maintenance_hours': last_hours,
                'last_maintenance_date': last_maintenance.date.isoformat() if last_maintenance else None,
            })
        
        return {
            'items': maintenance_items,
            'error': None
        }


class NormsFireTruckSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsFireTruck
        fields = '__all__'


class OdometerFuelFireTruckSerializer(FriendlyModelSerializer):
    class Meta:
        model = OdometerFuelFireTruck
        fields = '__all__'


class FireTruckWaybillSerializer(FriendlyModelSerializer):
    driver_full_name = serializers.SerializerMethodField()
    car_name = serializers.SerializerMethodField()
    car_number = serializers.SerializerMethodField()
    car_brand = serializers.SerializerMethodField()
    car_model = serializers.SerializerMethodField()
    vehicleType = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    total_operating_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = FireTruckWaybill
        fields = '__all__'
        read_only_fields = [
            'number',
            'upon_issuance',
            'total_spent',
            'total_received',
            'required_by_norm',
            'availability_upon_delivery',
            'savings',
            'overrun',
            'driver_full_name',
            'car_name',
            'car_number',
            'car_brand',
            'car_model',
            'vehicleType',
            'records',
            'total_operating_hours',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если это редактирование существующего путевого листа и он не editable - заблокировать date
        # (Skip if many=True, since self.instance will be a queryset)
        if self.instance and hasattr(self.instance, 'is_editable'):
            if not self.instance.is_editable():
                self.fields['date'].read_only = True
    
    def get_driver_full_name(self, obj):
        if obj.driver:
            return f"{obj.driver.surname} {obj.driver.name} {obj.driver.last_name}".strip()
        return None
    
    def get_car_name(self, obj):
        if obj.car:
            return f"{obj.car.brand} {obj.car.model}".strip()
        return 'Пожарный автомобиль'
    
    def get_car_number(self, obj):
        if obj.car:
            return obj.car.number
        return 'Без номера'
    
    def get_car_brand(self, obj):
        if obj.car:
            return obj.car.brand
        return None
    
    def get_car_model(self, obj):
        if obj.car:
            return obj.car.model
        return None
    
    def get_vehicleType(self, obj):
        return 'fire_truck'
    
    def get_records(self, obj):
        """Получить записи путевого листа с operating_hours"""
        request = self.context.get('request')
        include_records = request.query_params.get('include_records', 'false').lower() == 'true' if request else False
        
        if include_records:
            records = obj.records.all().order_by('-id')
            return FireTruckWaybillRecordSerializer(records, many=True, context=self.context).data
        return None
    
    def get_total_operating_hours(self, obj):
        """Получить сумму моточасов со всех записей путевого листа"""
        from django.db.models import Sum
        total = (
            FireTruckWaybillRecord.objects
            .filter(fire_truck_waybill=obj)
            .select_related('operating_hours_record')
            .aggregate(
                total_hours=Sum('operating_hours_record__operating_hours')
            )['total_hours']
        ) or 0
        return float(total)
    
    def to_representation(self, instance):
        """
        Опционально инклюдить инфо о машине и записи если проскан доп параметр
        """
        data = super().to_representation(instance)
        
        request = self.context.get('request')
        include_car = request.query_params.get('include_car', 'false').lower() == 'true' if request else False
        
        if not include_car:
            # Удаляем поля о машине если параметр не указан
            data.pop('car_name', None)
            data.pop('car_number', None)
            data.pop('car_brand', None)
            data.pop('car_model', None)
            data.pop('vehicleType', None)
        
        # Удаляем records если они None (параметр не был передан)
        if data.get('records') is None:
            data.pop('records', None)
        
        return data

    def validate(self, data):
        """
        Проверяем, что нет уже существующего путевого листа 
        для этой машины, водителя и даты
        """
        car = data.get('car')
        driver = data.get('driver')
        date = data.get('date')
        
        if car and driver and date:
            # Для обновления исключаем текущий объект
            query = FireTruckWaybill.objects.filter(
                car=car,
                driver=driver,
                date=date,
                deleted_at__isnull=True
            )
            
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                driver_full_name = f"{driver.surname} {driver.name} {driver.last_name}".strip()
                raise serializers.ValidationError(
                    f"Путевой лист для машины {car.number}, "
                    f"водителя {driver_full_name} "
                    f"и даты {date.strftime('%d.%m.%Y')} уже существует."
                )
        
        return data


class FireTruckWaybillRecordSerializer(FriendlyModelSerializer):
    operating_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = FireTruckWaybillRecord
        fields = '__all__'
        read_only_fields = [
            'fuel_before_departure',
            'odometer_before',
            'distance_km',
            'fuel_on_return',
            'fuel_used_by_distance',
            'fuel_used_with_pump',
            'fuel_used_without_pump',
            'fuel_used_normal',
            'operating_hours',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если это редактирование существующей записи, проверяем, editable ли она
        if self.instance:
            # Проверяем через родительский путевой лист
            if hasattr(self.instance, 'fire_truck_waybill'):
                waybill = self.instance.fire_truck_waybill
                if not waybill.is_editable():
                    # Запретить редактирование полей расчётов
                    self.fields['fuel_refueled'].read_only = True
                    self.fields['fuel_used'].read_only = True
                    self.fields['odometer_after'].read_only = True
                    self.fields['time_with_pump'].read_only = True
                    self.fields['time_without_pump'].read_only = True
    
    def get_operating_hours(self, obj):
        """Получить часы из связанной OperatingHoursCars записи"""
        if obj.operating_hours_record:
            return float(obj.operating_hours_record.operating_hours)
        return 0.0
    
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'\n\n========== [Serializer] CREATE validated_data ==========')
        for key, value in validated_data.items():
            logger.warning(f'{key}: {value} (type: {type(value).__name__})')
        logger.warning(f'=============================================\n')
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'\n\n========== [Serializer] UPDATE validated_data ==========')
        for key, value in validated_data.items():
            logger.warning(f'{key}: {value} (type: {type(value).__name__})')
        logger.warning(f'=============================================\n')
        return super().update(instance, validated_data)


# ---------- МОТОЧАСЫ / ТО ----------

class OperatingHoursCarsSerializer(FriendlyModelSerializer):
    class Meta:
        model = OperatingHoursCars
        fields = '__all__'


class NormsOperatingHoursPassengerCarSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsOperatingHoursPassengerCar
        fields = '__all__'


class NormsOperatingHoursFireTruckSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsOperatingHoursFireTruck
        fields = '__all__'


class NormsTechnicalMaintenanceSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsTechnicalMaintenance
        fields = '__all__'


class TechnicalMaintenanceSerializer(FriendlyModelSerializer):
    class Meta:
        model = TechnicalMaintenance
        fields = '__all__'
        read_only_fields = ['number']