# fuel/serializers.py
from rest_framework import serializers
from .models import (
    Role, Permission, User,
    PassengerCar, NormsPassengerCars, PassengerCarWaybill,
    PassengerCarWaybillRecord, OdometerFuelPassengerCar,
    FireTruck, NormsFireTruck, FireTruckWaybill,
    FireTruckWaybillRecord, OdometerFuelFireTruck,
)


# --- Роли и права ------------------------------------------------------------

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


# --- Пользователь ------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    role_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': False, 'allow_null': True}
        }

    def get_role_name(self, obj):
        """Возвращает название роли или '-' если роль не указана"""
        return obj.role.name if obj.role else '-'

    def create(self, validated_data):
        from .models import Role, Permission
        
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        
        # Если роль не указана, создаём уникальную роль с именем "User_<временная-метка>"
        if not role:
            import time
            unique_role_name = f"User_{int(time.time() * 1000)}"
            role = Role.objects.create(name=unique_role_name)
        
        validated_data['role'] = role
        user = User(**validated_data)
        
        # Устанавливаем пароль если он был предоставлен
        if password:
            user.set_password(password)
        
        user.save()
        
        # Создаём Permission объект для роли если его ещё нет
        if user.role and not Permission.objects.filter(role=user.role).exists():
            Permission.objects.create(role=user.role)
        
        return user

    def update(self, instance, validated_data):
        # Извлекаем пароль, если он был предоставлен
        # Если пароль пустой или None, не обновляем его
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Обновляем пароль только если он не пустой
        if password and password.strip():
            instance.set_password(password)

        instance.save()
        return instance


# --- Легковой автомобиль -----------------------------------------------------

class PassengerCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerCar
        fields = '__all__'


class NormsPassengerCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormsPassengerCars
        fields = '__all__'


class OdometerFuelPassengerCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdometerFuelPassengerCar
        fields = '__all__'


class PassengerCarWaybillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerCarWaybill
        fields = '__all__'
        read_only_fields = [
            'upon_issuance',
            'total_spent',
            'total_received',
            'required_by_norm',
            'availability_upon_delivery',
            'savings',
            'overrun',
        ]


class PassengerCarWaybillRecordSerializer(serializers.ModelSerializer):
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


# --- Пожарный автомобиль -----------------------------------------------------

class FireTruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = FireTruck
        fields = '__all__'


class NormsFireTruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormsFireTruck
        fields = '__all__'


class OdometerFuelFireTruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdometerFuelFireTruck
        fields = '__all__'


class FireTruckWaybillSerializer(serializers.ModelSerializer):
    class Meta:
        model = FireTruckWaybill
        fields = '__all__'
        read_only_fields = [
            'upon_issuance',
            'total_spent',
            'total_received',
            'required_by_norm',
            'availability_upon_delivery',
            'savings',
            'overrun',
        ]


class FireTruckWaybillRecordSerializer(serializers.ModelSerializer):
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