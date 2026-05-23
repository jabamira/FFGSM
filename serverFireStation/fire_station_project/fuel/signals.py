from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Role, Permission

DEFAULT_ROLES = [
    {
        "name": "Администратор",
        "permissions": {
            "can_use_mobile_booking": True,

            "can_create_users": True,
            "can_delete_users": True,
            "can_update_users": True,
            "view_users": True,
            "view_drivers": True,

            "can_create_roles": True,
            "can_delete_roles": True,
            "can_update_roles": True,
            "view_roles": True,

            "can_create_permissions": True,
            "can_delete_permissisons": True,
            "can_update_permissisons": True,
            "view_permissisons": True,

            "can_create_fire_trucks": True,
            "can_delete_fire_trucks": True,
            "can_update_fire_trucks": True,
            "view_fire_trucks": True,

            "can_create_fire_truck_waybills": True,
            "can_delete_fire_truck_waybills": True,
            "can_update_fire_truck_waybills": True,
            "can_download_fire_truck_waybills": True,
            "view_fire_truck_waybills": True,

            "can_create_fire_truck_waybills_records": True,
            "can_delete_fire_truck_waybills_records": True,
            "can_update_fire_truck_waybills_records": True,
            "view_fire_truck_waybills_records": True,

            "can_create_fire_truck_norms": True,
            "can_delete_fire_truck_norms": True,
            "can_update_fire_truck_norms": True,
            "view_fire_truck_norms": True,

            "can_download_fire_truck_reports": True,
            "view_fire_truck_reports": True,

            "can_create_passenger_cars": True,
            "can_delete_passenger_cars": True,
            "can_update_passenger_cars": True,
            "view_passenger_cars": True,

            "can_create_passenger_cars_waybills": True,
            "can_delete_passenger_cars_waybills": True,
            "can_update_passenger_cars_waybills": True,
            "can_download_passenger_cars_waybills": True,
            "view_passenger_cars_waybills": True,

            "can_create_passenger_cars_waybills_records": True,
            "can_delete_passenger_cars_waybills_records": True,
            "can_update_passenger_cars_waybills_records": True,
            "view_passenger_cars_waybills_records": True,

            "can_create_passenger_cars_norms": True,
            "can_delete_passenger_cars_norms": True,
            "can_update_passenger_cars_norms": True,
            "view_passenger_cars_norms": True,

            "can_download_passenger_cars_reports": True,
            "view_passenger_cars_reports": True,

            "can_download_drivers_reports": True,
            "view_drivers_reports": True,

            "can_create_technical_maintenance": True,
            "can_delete_technical_maintenance": True,
            "can_update_technical_maintenance": True,
            "view_technical_maintenance": True,

            "view_operating_hours": True
        },
    },
    {
        "name": "Механик",
        "permissions": {
            "can_use_mobile_booking": True,

            "can_create_users": False,
            "can_delete_users": False,
            "can_update_users": False,
            "view_users": False,
            "view_drivers": True,

            "can_create_roles": False,
            "can_delete_roles": False,
            "can_update_roles": False,
            "view_roles": False,

            "can_create_permissions": False,
            "can_delete_permissisons": False,
            "can_update_permissisons": False,
            "view_permissisons": False,

            "can_create_fire_trucks": True,
            "can_delete_fire_trucks": False,
            "can_update_fire_trucks": True,
            "view_fire_trucks": True,

            "can_create_fire_truck_waybills": True,
            "can_delete_fire_truck_waybills": True,
            "can_update_fire_truck_waybills": True,
            "can_download_fire_truck_waybills": True,
            "view_fire_truck_waybills": True,

            "can_create_fire_truck_waybills_records": True,
            "can_delete_fire_truck_waybills_records": True,
            "can_update_fire_truck_waybills_records": True,
            "view_fire_truck_waybills_records": True,

            "can_create_fire_truck_norms": True,
            "can_delete_fire_truck_norms": True,
            "can_update_fire_truck_norms": True,
            "view_fire_truck_norms": True,

            "can_download_fire_truck_reports": True,
            "view_fire_truck_reports": True,

            "can_create_passenger_cars": True,
            "can_delete_passenger_cars": False,
            "can_update_passenger_cars": True,
            "view_passenger_cars": True,

            "can_create_passenger_cars_waybills": True,
            "can_delete_passenger_cars_waybills": True,
            "can_update_passenger_cars_waybills": True,
            "can_download_passenger_cars_waybills": True,
            "view_passenger_cars_waybills": True,

            "can_create_passenger_cars_waybills_records": True,
            "can_delete_passenger_cars_waybills_records": True,
            "can_update_passenger_cars_waybills_records": True,
            "view_passenger_cars_waybills_records": True,

            "can_create_passenger_cars_norms": True,
            "can_delete_passenger_cars_norms": True,
            "can_update_passenger_cars_norms": True,
            "view_passenger_cars_norms": True,

            "can_download_passenger_cars_reports": True,
            "view_passenger_cars_reports": True,

            "can_download_drivers_reports": True,
            "view_drivers_reports": True,

            "can_create_technical_maintenance": True,
            "can_delete_technical_maintenance": True,
            "can_update_technical_maintenance": True,
            "view_technical_maintenance": True,

            "view_operating_hours": True
        },
    },
    {
        "name": "Водитель",
        "permissions": {
            "can_use_mobile_booking": True,

            "can_create_users": False,
            "can_delete_users": False,
            "can_update_users": False,
            "view_users": False,
            "view_drivers": False,

            "can_create_roles": False,
            "can_delete_roles": False,
            "can_update_roles": False,
            "view_roles": False,

            "can_create_permissions": False,
            "can_delete_permissisons": False,
            "can_update_permissisons": False,
            "view_permissisons": False,

            "can_create_fire_trucks": False,
            "can_delete_fire_trucks": False,
            "can_update_fire_trucks": False,
            "view_fire_trucks": True,

            "can_create_fire_truck_waybills": False,
            "can_delete_fire_truck_waybills": False,
            "can_update_fire_truck_waybills": False,
            "can_download_fire_truck_waybills": False,
            "view_fire_truck_waybills": True,

            "can_create_fire_truck_waybills_records": True,
            "can_delete_fire_truck_waybills_records": False,
            "can_update_fire_truck_waybills_records": False,
            "view_fire_truck_waybills_records": False,

            "can_create_fire_truck_norms": False,
            "can_delete_fire_truck_norms": False,
            "can_update_fire_truck_norms": False,
            "view_fire_truck_norms": False,

            "can_download_fire_truck_reports": False,
            "view_fire_truck_reports": False,

            "can_create_passenger_cars": False,
            "can_delete_passenger_cars": False,
            "can_update_passenger_cars": False,
            "view_passenger_cars": True,

            "can_create_passenger_cars_waybills": False,
            "can_delete_passenger_cars_waybills": False,
            "can_update_passenger_cars_waybills": False,
            "can_download_passenger_cars_waybills": False,
            "view_passenger_cars_waybills": True,

            "can_create_passenger_cars_waybills_records": True,
            "can_delete_passenger_cars_waybills_records": False,
            "can_update_passenger_cars_waybills_records": False,

            "can_create_passenger_cars_norms": False,
            "can_delete_passenger_cars_norms": False,
            "can_update_passenger_cars_norms": False,
            "view_passenger_cars_norms": False,

            "can_download_passenger_cars_reports": False,
            "view_passenger_cars_reports": False,

            "can_download_drivers_reports": False,
            "view_drivers_reports": False,

            "can_create_technical_maintenance": False,
            "can_delete_technical_maintenance": False,
            "can_update_technical_maintenance": False,
            "view_technical_maintenance": False,

            "view_operating_hours": False
        },
    },
]


@receiver(post_migrate)
def create_default_roles_and_permissions(sender, **kwargs):
    if sender.name != 'fuel':
        return

    for role_def in DEFAULT_ROLES:
        role_name = role_def["name"]
        perm_data = role_def["permissions"]

        role, _ = Role.objects.get_or_create(name=role_name)
        # создаём Permission только если его ещё нет для этой роли
        Permission.objects.get_or_create(
            role=role,
            defaults=perm_data,
        )