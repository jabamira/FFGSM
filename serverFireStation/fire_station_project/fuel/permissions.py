# fuel/permissions.py
from rest_framework.permissions import BasePermission


def _get_role_permission_obj(user):
    """
    Возвращает Permission, связанный с ролью пользователя, или None.

    В модели Permission:
        role = models.OneToOneField(Role, related_name="role")
    поэтому у Role обратная ссылка называется role.
    """
    if not user or not getattr(user, 'role', None):
        return None
    return getattr(user.role, 'role', None)  # Permission или None


class RolePermission(BasePermission):
    """
    Базовый пермишен: проверяет булевый флаг perm_attr в Permission пользователя.
    НЕ учитывает web/mobile — только сам флаг.
    """
    perm_attr = None

    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False
        if self.perm_attr is None:
            return True
        return bool(getattr(perm_obj, self.perm_attr, False))


# ================== ЛЕГКОВЫЕ ПУТЕВЫЕ (ШАПКА) ==================

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


# ================== ЛЕГКОВЫЕ ПУТЕВЫЕ (СТРОКИ) =================

class CanCreatePassengerCarWaybillRecord(BasePermission):
    """
    Создание записи легкового путевого:

    - если в токене client="web" (или client отсутствует):
        проверяем Permission.can_create_passenger_cars_waybills_record;
    - если client="mobile":
        проверяем Permission.can_use_mobile_booking.

    Если оба флага True -> пользователь может создавать записи и с веба, и с мобилки.
    """
    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False

        payload = request.auth or {}
        client = payload.get("client", "web")

        if client == "mobile":
            # мобильное приложение
            return bool(getattr(perm_obj, 'can_use_mobile_booking', False))

        # web/desktop и т.п.
        return bool(getattr(perm_obj, 'can_create_passenger_cars_waybills_record', False))


class CanUpdatePassengerCarWaybillRecord(RolePermission):
    perm_attr = 'can_update_passenger_cars_waybills_record'


class CanDeletePassengerCarWaybillRecord(RolePermission):
    perm_attr = 'can_delete_passenger_cars_waybills_record'


# ================== ПОЖАРНЫЕ ПУТЕВЫЕ (ШАПКА) ===================

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


# ================== ПОЖАРНЫЕ ПУТЕВЫЕ (СТРОКИ) ==================

class CanCreateFireTruckWaybillRecord(BasePermission):
    """
    Создание записи пожарного путевого:

    - client="web"  -> Permission.can_create_fire_truck_waybills_record;
    - client="mobile" -> Permission.can_use_mobile_booking.
    """
    def has_permission(self, request, view):
        perm_obj = _get_role_permission_obj(request.user)
        if not perm_obj:
            return False

        payload = request.auth or {}
        client = payload.get("client", "web")

        if client == "mobile":
            return bool(getattr(perm_obj, 'can_use_mobile_booking', False))

        return bool(getattr(perm_obj, 'can_create_fire_truck_waybills_record', False))


class CanUpdateFireTruckWaybillRecord(RolePermission):
    perm_attr = 'can_update_fire_truck_waybills_record'


class CanDeleteFireTruckWaybillRecord(RolePermission):
    perm_attr = 'can_delete_fire_truck_waybills_record'


# ========= СПЕЦ. ПЕРМИШЕН ДЛЯ МОБ. ЭКШЕНОВ (например /book-mobile) =========

class CanBookCarFromMobile(BasePermission):
    """
    Для action'ов, которые ДОЛЖНЫ работать только из мобильного приложения,
    например, /cars/{id}/book-mobile/.
    """
    def has_permission(self, request, view):
        user = request.user
        payload = request.auth or {}
        perm_obj = _get_role_permission_obj(user)

        if not perm_obj:
            return False

        if payload.get("client") != "mobile":
            return False

        return bool(getattr(perm_obj, 'can_use_mobile_booking', False))