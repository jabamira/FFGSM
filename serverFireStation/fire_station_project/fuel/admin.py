from django.contrib import admin
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


# Самый простой вариант — просто зарегистрировать модели

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Permission)

admin.site.register(PassengerCar)
admin.site.register(PassengerCarWaybill)
admin.site.register(PassengerCarWaybillRecord)
admin.site.register(OdometerFuelPassengerCar)
admin.site.register(NormsPassengerCars)

admin.site.register(FireTruck)
admin.site.register(FireTruckWaybill)
admin.site.register(FireTruckWaybillRecord)
admin.site.register(OdometerFuelFireTruck)
admin.site.register(NormsFireTruck)

admin.site.register(OperatingHoursCars)
admin.site.register(NormsOperatingHoursPassengerCar)
admin.site.register(NormsOperatingHoursFireTruck)
admin.site.register(TechnicalMaintenance)
admin.site.register(NormsTechnicalMaintenance)