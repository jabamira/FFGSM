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
    class Meta:
        model = PassengerCar
        fields = '__all__'


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
    class Meta:
        model = FireTruck
        fields = '__all__'


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