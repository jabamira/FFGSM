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

    class Meta:
        model = PassengerCar
        fields = '__all__'

    def get_odometer_fuel_records(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_odometer') == 'true':
            records = obj.odometer_fuel_records.all()
            return OdometerFuelPassengerCarSerializer(records, many=True).data
        return None


class NormsPassengerCarsSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsPassengerCars
        fields = '__all__'


class OdometerFuelPassengerCarSerializer(FriendlyModelSerializer):
    class Meta:
        model = OdometerFuelPassengerCar
        fields = '__all__'


class PassengerCarWaybillSerializer(FriendlyModelSerializer):
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
        ]

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

    class Meta:
        model = FireTruck
        fields = '__all__'

    def get_odometer_fuel_records(self, obj):
        request = self.context.get('request')
        if request and request.query_params.get('include_odometer') == 'true':
            records = obj.odometer_fuel_records.all()
            return OdometerFuelFireTruckSerializer(records, many=True).data
        return None


class NormsFireTruckSerializer(FriendlyModelSerializer):
    class Meta:
        model = NormsFireTruck
        fields = '__all__'


class OdometerFuelFireTruckSerializer(FriendlyModelSerializer):
    class Meta:
        model = OdometerFuelFireTruck
        fields = '__all__'


class FireTruckWaybillSerializer(FriendlyModelSerializer):
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
        ]

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