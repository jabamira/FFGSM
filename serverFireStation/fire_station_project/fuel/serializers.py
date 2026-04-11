from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
    operating_hours = serializers.SerializerMethodField()
    technical_maintenance_norm = serializers.SerializerMethodField()
    hours_until_maintenance = serializers.SerializerMethodField()
    maintenance_info = serializers.SerializerMethodField()

    class Meta:
        model = PassengerCar
        fields = '__all__'

    def get_odometer_fuel_records(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_odometer') == 'true':
            records = obj.odometer_fuel_records.all()
            return OdometerFuelPassengerCarSerializer(records, many=True).data
        return None

    def get_operating_hours(self, obj):
        """Получить текущие операционные часы машины"""
        operating_hours = OperatingHoursCars.objects.filter(passenger_car=obj).order_by('-date').first()
        if operating_hours:
            return float(operating_hours.operating_hours)
        return 0.0

    def get_technical_maintenance_norm(self, obj):
        """Получить норму технического обслуживания (часы)"""
        norm = NormsTechnicalMaintenance.objects.filter(passenger_car=obj).order_by('-date').first()
        if norm:
            return float(norm.norm)
        return 0.0

    def get_hours_until_maintenance(self, obj):
        """Вычислить часы до следующего ТО"""
        operating_hours_obj = OperatingHoursCars.objects.filter(passenger_car=obj).order_by('-date').first()
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
        operating_hours_obj = OperatingHoursCars.objects.filter(passenger_car=obj).order_by('-date').first()
        
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
        maintenance_at = float(norm_obj.norm)
        interval = maintenance_at - current_hours
        
        # Часы проведения предыдущего ТО и интервал между ТО
        previous_hours = float(last_maintenance.operating_hours) if last_maintenance else 0.0
        norm_interval_value = maintenance_at - previous_hours
        
        return {
            'maintenance_type': norm_obj.maintenance_type,
            'interval': interval,  # Часов ДО следующего ТО
            'norm_interval_value': norm_interval_value,  # Интервал между ТО (часов в норме)
            'previous_maintenance_hours': previous_hours,  # На каких часах было ТО
            'current_hours': current_hours,
            'next_maintenance_at': maintenance_at,  # Абсолютное значение часов
            'last_maintenance_date': last_maintenance.date.isoformat() if last_maintenance else None,
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
        ]
    
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
    
    def to_representation(self, instance):
        """
        Опционально инклюдить инфо о машине если проскан доп параметр
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
    class Meta:
        model = PassengerCarWaybillRecord
        fields = '__all__'
        read_only_fields = [
            'fuel_before_departure',
            'odometer_before',
            'odometer_after',
            'distance_total_km',
            'fuel_used_city',
            'fuel_used_area',
            'fuel_on_return',
            'fuel_used_normal',
        ]


# ---------- ПОЖАРНЫЕ ----------

class FireTruckSerializer(FriendlyModelSerializer):
    odometer_fuel_records = serializers.SerializerMethodField()
    operating_hours = serializers.SerializerMethodField()
    technical_maintenance_norm = serializers.SerializerMethodField()
    hours_until_maintenance = serializers.SerializerMethodField()
    maintenance_info = serializers.SerializerMethodField()

    class Meta:
        model = FireTruck
        fields = '__all__'

    def get_odometer_fuel_records(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_odometer') == 'true':
            records = obj.odometer_fuel_records.all()
            return OdometerFuelFireTruckSerializer(records, many=True).data
        return None

    def get_operating_hours(self, obj):
        """Получить текущие операционные часы машины"""
        operating_hours = OperatingHoursCars.objects.filter(fire_truck=obj).order_by('-date').first()
        if operating_hours:
            return float(operating_hours.operating_hours)
        return 0.0

    def get_technical_maintenance_norm(self, obj):
        """Получить норму технического обслуживания (часы)"""
        norm = NormsTechnicalMaintenance.objects.filter(fire_truck=obj).order_by('-date').first()
        if norm:
            return float(norm.norm)
        return 0.0

    def get_hours_until_maintenance(self, obj):
        """Вычислить часы до следующего ТО"""
        operating_hours_obj = OperatingHoursCars.objects.filter(fire_truck=obj).order_by('-date').first()
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
        operating_hours_obj = OperatingHoursCars.objects.filter(fire_truck=obj).order_by('-date').first()
        
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
        maintenance_at = float(norm_obj.norm)
        interval = maintenance_at - current_hours
        
        # Часы проведения предыдущего ТО и интервал между ТО
        previous_hours = float(last_maintenance.operating_hours) if last_maintenance else 0.0
        norm_interval_value = maintenance_at - previous_hours
        
        return {
            'maintenance_type': norm_obj.maintenance_type,
            'interval': interval,  # Часов ДО следующего ТО
            'norm_interval_value': norm_interval_value,  # Интервал между ТО (часов в норме)
            'previous_maintenance_hours': previous_hours,  # На каких часах было ТО
            'current_hours': current_hours,
            'next_maintenance_at': maintenance_at,  # Абсолютное значение часов
            'last_maintenance_date': last_maintenance.date.isoformat() if last_maintenance else None,
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
        ]
    
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
    
    def to_representation(self, instance):
        """
        Опционально инклюдить инфо о машине если проскан доп параметр
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
        ]
    
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
        read_only_fields = ['number', 'operating_hours']