from rest_framework.permissions import BasePermission


def _get_role_permission_obj(user):
    """
    Возвращает Permission, связанный с ролью пользователя, или None.
    В модели Permission:
        role = OneToOneField(Role, related_name="role")
    поэтому у Role обратная ссылка называется role.
    """
    if not user or not getattr(user, 'role', None):
        return None
    return getattr(user.role, 'role', None)


class RolePermission(BasePermission):
    """
    Базовый пермишен: проверяет булевый флаг perm_attr в Permission пользователя.
    """
    perm_attr = None

    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False
        if self.perm_attr is None:
            return True
        return bool(getattr(perm_obj, self.perm_attr, False))


# ================= USERS =================

class CanViewUsers(RolePermission):
    perm_attr = 'view_users'


class CanCreateUsers(RolePermission):
    perm_attr = 'can_create_users'


class CanUpdateUsers(RolePermission):
    perm_attr = 'can_update_users'


class CanDeleteUsers(RolePermission):
    perm_attr = 'can_delete_users'


class CanViewDrivers(RolePermission):
    perm_attr = 'view_drivers'


class CanViewDriversReports(RolePermission):
    perm_attr = 'view_drivers_reports'


class CanDownloadDriversReports(RolePermission):
    perm_attr = 'can_download_drivers_reports'


# ================= ROLES =================

class CanViewRoles(RolePermission):
    perm_attr = 'view_roles'


class CanCreateRoles(RolePermission):
    perm_attr = 'can_create_roles'


class CanUpdateRoles(RolePermission):
    perm_attr = 'can_update_roles'


class CanDeleteRoles(RolePermission):
    perm_attr = 'can_delete_roles'


# ================= PERMISSIONS =================

class CanViewPermissions(RolePermission):
    perm_attr = 'view_permissisons'


class CanCreatePermissions(RolePermission):
    perm_attr = 'can_create_permissions'


class CanUpdatePermissions(RolePermission):
    perm_attr = 'can_update_permissisons'


class CanDeletePermissions(RolePermission):
    perm_attr = 'can_delete_permissisons'


# ================= PASSENGER CARS =================

class CanViewPassengerCars(RolePermission):
    perm_attr = 'view_passenger_cars'


class CanCreatePassengerCars(RolePermission):
    perm_attr = 'can_create_passenger_cars'


class CanUpdatePassengerCars(RolePermission):
    perm_attr = 'can_update_passenger_cars'


class CanDeletePassengerCars(RolePermission):
    perm_attr = 'can_delete_passenger_cars'


class CanViewPassengerCarNorms(RolePermission):
    perm_attr = 'view_passenger_cars_norms'


class CanCreatePassengerCarNorms(RolePermission):
    perm_attr = 'can_create_passenger_cars_norms'


class CanUpdatePassengerCarNorms(RolePermission):
    perm_attr = 'can_update_passenger_cars_norms'


class CanDeletePassengerCarNorms(RolePermission):
    perm_attr = 'can_delete_passenger_cars_norms'


class CanViewPassengerCarWaybills(RolePermission):
    perm_attr = 'view_passenger_cars_waybills'


class CanCreatePassengerCarWaybills(RolePermission):
    perm_attr = 'can_create_passenger_cars_waybills'


class CanUpdatePassengerCarWaybills(RolePermission):
    perm_attr = 'can_update_passenger_cars_waybills'


class CanDeletePassengerCarWaybills(RolePermission):
    perm_attr = 'can_delete_passenger_cars_waybills'


class CanDownloadPassengerCarWaybills(RolePermission):
    perm_attr = 'can_download_passenger_cars_waybills'


class CanDownloadPassengerCarReports(RolePermission):
    perm_attr = 'can_download_passenger_cars_reports'


class CanViewPassengerCarReports(RolePermission):
    perm_attr = 'view_passenger_cars_reports'


class CanCreatePassengerCarWaybillRecord(BasePermission):
    """
    Создание записи легкового путевого:
    - если client='web' -> нужен can_create_passenger_cars_waybills_record
    - если client='mobile' -> нужен can_use_mobile_booking
    """
    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False

        payload = request.auth or {}
        client = payload.get('client', 'web')

        if client == 'mobile':
            return bool(getattr(perm_obj, 'can_use_mobile_booking', False))

        return bool(getattr(perm_obj, 'can_create_passenger_cars_waybills_records', False))


class CanUpdatePassengerCarWaybillRecord(RolePermission):

    perm_attr = 'can_update_passenger_cars_waybills_records'
class CanViewPassengerCarWaybillRecord(RolePermission):
    perm_attr = 'view_passenger_cars_waybills_records'

class CanDeletePassengerCarWaybillRecord(RolePermission):
    perm_attr = 'can_delete_passenger_cars_waybills_records'


# ================= FIRE TRUCKS =================

class CanViewFireTrucks(RolePermission):
    perm_attr = 'view_fire_trucks'


class CanCreateFireTrucks(RolePermission):
    perm_attr = 'can_create_fire_trucks'


class CanUpdateFireTrucks(RolePermission):
    perm_attr = 'can_update_fire_trucks'


class CanDeleteFireTrucks(RolePermission):
    perm_attr = 'can_delete_fire_trucks'


class CanViewFireTruckNorms(RolePermission):
    perm_attr = 'view_fire_truck_norms'


class CanCreateFireTruckNorms(RolePermission):
    perm_attr = 'can_create_fire_truck_norms'


class CanUpdateFireTruckNorms(RolePermission):
    perm_attr = 'can_update_fire_truck_norms'


class CanDeleteFireTruckNorms(RolePermission):
    perm_attr = 'can_delete_fire_truck_norms'


class CanViewFireTruckWaybills(RolePermission):
    perm_attr = 'view_fire_truck_waybills'


class CanCreateFireTruckWaybills(RolePermission):
    perm_attr = 'can_create_fire_truck_waybills'


class CanUpdateFireTruckWaybills(RolePermission):
    perm_attr = 'can_update_fire_truck_waybills'


class CanDeleteFireTruckWaybills(RolePermission):
    perm_attr = 'can_delete_fire_truck_waybills'


class CanDownloadFireTruckWaybills(RolePermission):
    perm_attr = 'can_download_fire_truck_waybills'


class CanDownloadFireTruckReports(RolePermission):
    perm_attr = 'can_download_fire_truck_reports'


class CanViewFireTruckReports(RolePermission):
    perm_attr = 'view_fire_truck_reports'


class CanCreateFireTruckWaybillRecord(BasePermission):
    """
    Создание записи пожарного путевого:
    - если client='web' -> нужен can_create_fire_truck_waybills_record
    - если client='mobile' -> нужен can_use_mobile_booking
    """
    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False

        payload = request.auth or {}
        client = payload.get('client', 'web')

        if client == 'mobile':
            return bool(getattr(perm_obj, 'can_use_mobile_booking', False))

        return bool(getattr(perm_obj, 'can_create_fire_truck_waybills_records', False))


class CanUpdateFireTruckWaybillRecord(RolePermission):
    perm_attr = 'can_update_fire_truck_waybills_records'

class CanViewFireTruckWaybillRecord(RolePermission):
    perm_attr = 'view_fire_truck_waybills_records'


class CanDeleteFireTruckWaybillRecord(RolePermission):
    perm_attr = 'can_delete_fire_truck_waybills_records'


# ================= TECHNICAL MAINTENANCE =================

class CanViewTechnicalMaintenance(RolePermission):
    perm_attr = 'view_technical_maintenance'


class CanCreateTechnicalMaintenance(RolePermission):
    perm_attr = 'can_create_technical_maintenance'


class CanUpdateTechnicalMaintenance(RolePermission):
    perm_attr = 'can_update_technical_maintenance'


class CanDeleteTechnicalMaintenance(RolePermission):
    perm_attr = 'can_delete_technical_maintenance'


class CanViewOperatingHours(RolePermission):
    perm_attr = 'view_operating_hours'
    
# ================= MOBILE ONLY ACTIONS =================

class CanBookCarFromMobile(BasePermission):
    """
    Для спец-экшенов, которые должны работать только из мобильного приложения.
    """
    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False

        payload = request.auth or {}
        if payload.get("client") != "mobile":
            return False

        return bool(getattr(perm_obj, 'can_use_mobile_booking', False))