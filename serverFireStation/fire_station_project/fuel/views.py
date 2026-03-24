from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from io import BytesIO
from django.conf import settings
from openpyxl import Workbook, load_workbook
from decimal import Decimal
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from urllib.parse import quote

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
    MaintenanceNotification,
)

from .serializers import (
    RoleSerializer, PermissionSerializer, UserSerializer,
    PassengerCarSerializer, NormsPassengerCarsSerializer,
    PassengerCarWaybillSerializer, PassengerCarWaybillRecordSerializer,
    OdometerFuelPassengerCarSerializer,
    FireTruckSerializer, NormsFireTruckSerializer,
    FireTruckWaybillSerializer, FireTruckWaybillRecordSerializer,
    OdometerFuelFireTruckSerializer,

    OperatingHoursCarsSerializer,
    NormsOperatingHoursPassengerCarSerializer,
    NormsOperatingHoursFireTruckSerializer,
    TechnicalMaintenanceSerializer,
    NormsTechnicalMaintenanceSerializer,
    MaintenanceNotificationSerializer,
)

from .permissions import (
    CanViewUsers, CanCreateUsers, CanUpdateUsers, CanDeleteUsers, CanViewDrivers,
    CanViewDriversReports, CanDownloadDriversReports,

    CanViewRoles, CanCreateRoles, CanUpdateRoles, CanDeleteRoles,
    CanViewPermissions, CanCreatePermissions, CanUpdatePermissions, CanDeletePermissions,

    CanViewPassengerCars, CanCreatePassengerCars,
    CanUpdatePassengerCars, CanDeletePassengerCars,

    CanViewPassengerCarNorms, CanCreatePassengerCarNorms,
    CanUpdatePassengerCarNorms, CanDeletePassengerCarNorms,

    CanViewPassengerCarWaybills, CanCreatePassengerCarWaybills,
    CanUpdatePassengerCarWaybills, CanDeletePassengerCarWaybills,
    CanDownloadPassengerCarWaybills, CanDownloadPassengerCarReports,
    CanCreatePassengerCarWaybillRecord,
    CanUpdatePassengerCarWaybillRecord,
    CanDeletePassengerCarWaybillRecord,

    CanViewFireTrucks, CanCreateFireTrucks,
    CanUpdateFireTrucks, CanDeleteFireTrucks,

    CanViewFireTruckNorms, CanCreateFireTruckNorms,
    CanUpdateFireTruckNorms, CanDeleteFireTruckNorms,

    CanViewFireTruckWaybills, CanCreateFireTruckWaybills,
    CanUpdateFireTruckWaybills, CanDeleteFireTruckWaybills,
    CanDownloadFireTruckWaybills, CanDownloadFireTruckReports,
    CanCreateFireTruckWaybillRecord,
    CanUpdateFireTruckWaybillRecord,
    CanDeleteFireTruckWaybillRecord,

    CanCreateTechnicalMaintenance, CanDeleteTechnicalMaintenance,
    CanUpdateTechnicalMaintenance, CanViewTechnicalMaintenance,
    CanViewOperatingHours,
)


class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================= РОЛИ / ПРАВА / ПОЛЬЗОВАТЕЛИ =================

class RoleViewSet(SoftDeleteModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewRoles()]
        elif self.action == 'create':
            return base + [CanCreateRoles()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateRoles()]
        elif self.action == 'destroy':
            return base + [CanDeleteRoles()]
        return base + [CanViewRoles()]


class PermissionViewSet(SoftDeleteModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        queryset = Permission.objects.filter(deleted_at__isnull=True)
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        return queryset

    def get_permissions(self):
        base = [IsAuthenticated()]

        if self.action == 'current':
            return base
        elif self.action in ['list', 'retrieve']:
            return base + [CanViewPermissions()]
        elif self.action == 'create':
            return base + [CanCreatePermissions()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePermissions()]
        elif self.action == 'destroy':
            return base + [CanDeletePermissions()]

        return base + [CanViewPermissions()]

    @action(detail=False, methods=['get'])
    def current(self, request):
        user = request.user

        if not user or not hasattr(user, 'role'):
            return Response(
                {'detail': 'User or user role not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            permission = Permission.objects.get(role=user.role, deleted_at__isnull=True)
            serializer = self.get_serializer(permission)
            return Response(serializer.data)
        except Permission.DoesNotExist:
            return Response(
                {'detail': 'No permissions found for user role'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserViewSet(SoftDeleteModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewUsers()]
        elif self.action == 'create':
            return base + [CanCreateUsers()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateUsers()]
        elif self.action == 'destroy':
            return base + [CanDeleteUsers()]
        elif self.action == 'drivers':
            return base + [CanViewDrivers()]
        elif self.action == 'drivers_report':
            return base + [CanViewDriversReports()]
        elif self.action == 'drivers_report_excel':
            return base + [CanDownloadDriversReports()]
        return base + [CanViewUsers()]

    def get_queryset(self):
        role_id = self.request.query_params.get('role')
        if role_id:
            return self.queryset.filter(role_id=role_id, deleted_at__isnull=True)
        return self.queryset.filter(deleted_at__isnull=True)

    @action(detail=False, methods=['get'])
    def drivers(self, request):
        drivers = self.queryset.filter(role_id=3, deleted_at__isnull=True)
        serializer = self.get_serializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='drivers-report')
    def drivers_report(self, request):
        from_str = request.query_params.get('from')
        to_str = request.query_params.get('to')

        if not from_str or not to_str:
            return Response({"detail": "Параметры from и to обязательны"}, status=400)

        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        if not from_date or not to_date:
            return Response({"detail": "Неверный формат дат"}, status=400)

        passenger_records = PassengerCarWaybillRecord.objects.filter(
            passenger_car_waybill__date__gte=from_date,
            passenger_car_waybill__date__lte=to_date,
        ).select_related('passenger_car_waybill__driver', 'passenger_car_waybill__car')

        fire_records = FireTruckWaybillRecord.objects.filter(
            fire_truck_waybill__date__gte=from_date,
            fire_truck_waybill__date__lte=to_date,
        ).select_related('fire_truck_waybill__driver', 'fire_truck_waybill__car')

        result = []

        for rec in passenger_records:
            d = rec.passenger_car_waybill.driver
            result.append({
                'date': rec.passenger_car_waybill.date,
                'driver': f'{d.surname} {d.name} {d.last_name}',
                'car_type': 'passenger',
                'car_number': rec.passenger_car_waybill.car.number,
                'route_or_target': rec.target,
                'distance': rec.distance_total_km,
                'fuel_used_fact': rec.fuel_used,
                'fuel_used_normal': rec.fuel_used_normal,
            })

        for rec in fire_records:
            d = rec.fire_truck_waybill.driver
            route = f"{rec.target} {rec.driving_route or ''}".strip()
            result.append({
                'date': rec.fire_truck_waybill.date,
                'driver': f'{d.surname} {d.name} {d.last_name}',
                'car_type': 'fire_truck',
                'car_number': rec.fire_truck_waybill.car.number,
                'route_or_target': route,
                'distance': rec.distance_km,
                'fuel_used_fact': rec.fuel_used,
                'fuel_used_normal': rec.fuel_used_normal,
            })

        return Response(result)

    @action(detail=False, methods=['get'], url_path='drivers-report-excel')
    def drivers_report_excel(self, request):
        from_str = request.query_params.get('from')
        to_str = request.query_params.get('to')

        if not from_str or not to_str:
            return Response({"detail": "Параметры from и to обязательны"}, status=400)

        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        if not from_date or not to_date:
            return Response({"detail": "Неверный формат дат"}, status=400)

        passenger_records = PassengerCarWaybillRecord.objects.filter(
            passenger_car_waybill__date__gte=from_date,
            passenger_car_waybill__date__lte=to_date,
        ).select_related('passenger_car_waybill__driver', 'passenger_car_waybill__car')

        fire_records = FireTruckWaybillRecord.objects.filter(
            fire_truck_waybill__date__gte=from_date,
            fire_truck_waybill__date__lte=to_date,
        ).select_related('fire_truck_waybill__driver', 'fire_truck_waybill__car')

        wb = Workbook()
        ws = wb.active
        ws.title = "Отчет по водителям"

        ws['A1'] = "Период"
        ws['B1'] = f"{from_date.strftime('%d.%m.%Y')} - {to_date.strftime('%d.%m.%Y')}"

        headers = ['Дата', 'Водитель', 'Тип автомобиля', 'Автомобиль', 'Маршрут/цель', 'Пробег', 'Факт расход', 'По норме']
        for i, h in enumerate(headers, start=1):
            ws.cell(row=3, column=i, value=h)

        row_idx = 4

        for rec in passenger_records:
            driver = rec.passenger_car_waybill.driver
            fio = f"{driver.surname} {driver.name} {driver.last_name}"
            ws.cell(row=row_idx, column=1, value=rec.passenger_car_waybill.date.strftime('%d.%m.%Y'))
            ws.cell(row=row_idx, column=2, value=fio)
            ws.cell(row=row_idx, column=3, value='Легковой')
            ws.cell(row=row_idx, column=4, value=rec.passenger_car_waybill.car.number)
            ws.cell(row=row_idx, column=5, value=rec.target)
            ws.cell(row=row_idx, column=6, value=rec.distance_total_km)
            ws.cell(row=row_idx, column=7, value=float(rec.fuel_used))
            ws.cell(row=row_idx, column=8, value=float(rec.fuel_used_normal))
            row_idx += 1

        for rec in fire_records:
            driver = rec.fire_truck_waybill.driver
            fio = f"{driver.surname} {driver.name} {driver.last_name}"
            route = f"{rec.target} {rec.driving_route or ''}".strip()
            ws.cell(row=row_idx, column=1, value=rec.fire_truck_waybill.date.strftime('%d.%m.%Y'))
            ws.cell(row=row_idx, column=2, value=fio)
            ws.cell(row=row_idx, column=3, value='Пожарный')
            ws.cell(row=row_idx, column=4, value=rec.fire_truck_waybill.car.number)
            ws.cell(row=row_idx, column=5, value=route)
            ws.cell(row=row_idx, column=6, value=rec.distance_km)
            ws.cell(row=row_idx, column=7, value=float(rec.fuel_used))
            ws.cell(row=row_idx, column=8, value=float(rec.fuel_used_normal))
            row_idx += 1

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Отчет по водителям {from_date.strftime('%d.%m.%Y')}-{to_date.strftime('%d.%m.%Y')}.xlsx"
        quoted_filename = quote(filename)

        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quoted_filename}"
        return response


# ================= ЛЕГКОВЫЕ =================

class PassengerCarViewSet(SoftDeleteModelViewSet):
    queryset = PassengerCar.objects.all()
    serializer_class = PassengerCarSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewPassengerCars()]
        elif self.action == 'create':
            return base + [CanCreatePassengerCars()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePassengerCars()]
        elif self.action == 'destroy':
            return base + [CanDeletePassengerCars()]
        return base


class NormsPassengerCarsViewSet(SoftDeleteModelViewSet):
    queryset = NormsPassengerCars.objects.all()
    serializer_class = NormsPassengerCarsSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action == 'for_date':
            return base + [CanViewPassengerCarNorms()]
        elif self.action in ['list', 'retrieve']:
            return base + [CanViewPassengerCarNorms()]
        elif self.action == 'create':
            return base + [CanCreatePassengerCarNorms()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePassengerCarNorms()]
        elif self.action == 'destroy':
            return base + [CanDeletePassengerCarNorms()]
        return base

    @action(detail=False, methods=['get'], url_path='for-date')
    def for_date(self, request):
        car_id = request.query_params.get('car')
        season = request.query_params.get('season')
        date_str = request.query_params.get('date')

        if not car_id or not season or not date_str:
            return Response({"detail": "Параметры car, season и date обязательны"}, status=400)

        doc_date = parse_date(date_str)
        if not doc_date:
            return Response({"detail": "Неверный формат date, ожидается YYYY-MM-DD"}, status=400)

        norm = (
            NormsPassengerCars.objects
            .filter(car_id=car_id, season=season, date__lte=doc_date)
            .order_by('-date', '-id')
            .first()
        )
        if not norm:
            return Response({"detail": "Норма не найдена"}, status=404)

        serializer = self.get_serializer(norm)
        return Response(serializer.data)


class OdometerFuelPassengerCarViewSet(SoftDeleteModelViewSet):
    queryset = OdometerFuelPassengerCar.objects.all()
    serializer_class = OdometerFuelPassengerCarSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve', 'last_record']:
            return base + [CanViewPassengerCars()]
        elif self.action == 'create':
            return base + [CanCreatePassengerCars()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePassengerCars()]
        elif self.action == 'destroy':
            return base + [CanDeletePassengerCars()]
        return base

    @action(detail=False, methods=['get'], url_path='last')
    def last_record(self, request):
        car_id = request.query_params.get('car')
        if not car_id:
            return Response({"detail": "Параметр car обязателен"}, status=400)

        obj = (
            OdometerFuelPassengerCar.objects
            .filter(car_id=car_id)
            .order_by('-date', '-id')
            .first()
        )
        if not obj:
            return Response({"detail": "Записей не найдено"}, status=404)

        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class PassengerCarWaybillViewSet(SoftDeleteModelViewSet):
    queryset = PassengerCarWaybill.objects.all()
    serializer_class = PassengerCarWaybillSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewPassengerCarWaybills()]
        elif self.action == 'create':
            return base + [CanCreatePassengerCarWaybills()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePassengerCarWaybills()]
        elif self.action == 'destroy':
            return base + [CanDeletePassengerCarWaybills()]
        elif self.action == 'export_excel':
            return base + [CanDownloadPassengerCarWaybills()]
        return base

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        car_id = request.query_params.get('car')
        from_str = request.query_params.get('from')
        to_str = request.query_params.get('to')

        if not car_id or not from_str or not to_str:
            return Response({"detail": "Параметры car, from и to обязательны"}, status=400)

        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        if not from_date or not to_date:
            return Response({"detail": "Неверный формат дат, используйте YYYY-MM-DD"}, status=400)

        records = (
            PassengerCarWaybillRecord.objects
            .filter(
                passenger_car_waybill__car_id=car_id,
                passenger_car_waybill__date__gte=from_date,
                passenger_car_waybill__date__lte=to_date,
            )
            .select_related('passenger_car_waybill__driver', 'passenger_car_waybill__car')
            .order_by('passenger_car_waybill__date', 'id')
        )

        if not records.exists():
            return Response({"detail": "Записей за указанный период не найдено"}, status=404)

        car = records.first().passenger_car_waybill.car

        template_path = settings.BASE_DIR / 'report_templates' / 'passenger_car.xlsx'
        wb = load_workbook(template_path)
        ws = wb.active

        ws['D2'] = car.number
        ws['I2'] = from_date.strftime('%d.%m.%Y')
        ws['N2'] = to_date.strftime('%d.%m.%Y')

        data_start_row = 7
        row_idx = data_start_row

        total_distance_city = 0
        total_distance_area = 0
        total_distance = 0
        total_fuel_used_city = Decimal('0.000')
        total_fuel_used_area = Decimal('0.000')
        total_fuel_used_fact = Decimal('0.000')
        total_fuel_used_normal = Decimal('0.000')
        total_fuel_refueled = Decimal('0.000')
        total_savings = Decimal('0.000')
        total_overrun = Decimal('0.000')

        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000'),
        )

        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        green_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
        red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

        for rec in records:
            wb_obj = rec.passenger_car_waybill
            driver = wb_obj.driver

            savings = Decimal('0.000')
            overrun = Decimal('0.000')

            fio = f"{driver.surname} {driver.name[0]}. {driver.last_name[0]}."

            ws.cell(row=row_idx, column=1, value=wb_obj.date.strftime('%d.%m.%Y'))
            ws.cell(row=row_idx, column=2, value=fio)

            cell = ws.cell(row=row_idx, column=3, value=rec.fuel_before_departure)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=4, value=rec.odometer_before)
            cell.fill = yellow_fill

            ws.cell(row=row_idx, column=5, value=rec.distance_total_km)
            ws.cell(row=row_idx, column=6, value=rec.distance_city_km)
            ws.cell(row=row_idx, column=7, value=rec.distance_area_km)
            ws.cell(row=row_idx, column=8, value=rec.fuel_used_city)
            ws.cell(row=row_idx, column=9, value=rec.fuel_used_area)

            cell = ws.cell(row=row_idx, column=10, value=rec.fuel_used_normal)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=11, value=rec.fuel_used)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=12, value=rec.fuel_refueled)
            cell.fill = green_fill
            cell = ws.cell(row=row_idx, column=13, value=rec.fuel_on_return)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=14, value=rec.odometer_after)
            cell.fill = yellow_fill

            if rec.fuel_used_normal > rec.fuel_used:
                savings = rec.fuel_used_normal - rec.fuel_used
                overrun = Decimal('0.000')
            elif rec.fuel_used_normal < rec.fuel_used:
                savings = Decimal('0.000')
                overrun = rec.fuel_used - rec.fuel_used_normal

            cell = ws.cell(row=row_idx, column=15, value=float(savings))
            cell.fill = green_fill
            cell = ws.cell(row=row_idx, column=16, value=float(overrun))
            cell.fill = red_fill

            total_distance_city += rec.distance_city_km
            total_distance_area += rec.distance_area_km
            total_distance += rec.distance_total_km
            total_fuel_used_city += rec.fuel_used_city
            total_fuel_used_area += rec.fuel_used_area
            total_fuel_used_fact += rec.fuel_used
            total_fuel_used_normal += rec.fuel_used_normal
            total_fuel_refueled += rec.fuel_refueled
            total_savings += savings
            total_overrun += overrun

            row_idx += 1

        cell = ws.cell(row=row_idx, column=2, value="ИТОГО")
        cell.fill = yellow_fill
        ws.cell(row=row_idx, column=5, value=total_distance).fill = yellow_fill
        ws.cell(row=row_idx, column=6, value=total_distance_city).fill = yellow_fill
        ws.cell(row=row_idx, column=7, value=total_distance_area).fill = yellow_fill
        ws.cell(row=row_idx, column=8, value=float(total_fuel_used_city)).fill = yellow_fill
        ws.cell(row=row_idx, column=9, value=float(total_fuel_used_area)).fill = yellow_fill
        ws.cell(row=row_idx, column=10, value=float(total_fuel_used_normal)).fill = yellow_fill
        ws.cell(row=row_idx, column=11, value=float(total_fuel_used_fact)).fill = yellow_fill
        ws.cell(row=row_idx, column=12, value=float(total_fuel_refueled)).fill = green_fill
        ws.cell(row=row_idx, column=15, value=float(total_savings)).fill = green_fill
        ws.cell(row=row_idx, column=16, value=float(total_overrun)).fill = red_fill

        data_end_row = row_idx
        for r in range(data_start_row, data_end_row + 1):
            for c in range(1, 16 + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = thin_border
                cell.font = Font(name='Times New Roman', size=11)
                cell.alignment = Alignment(horizontal='center', vertical='center')

        for c in range(1, 16 + 1):
            ws.cell(row=data_end_row, column=c).font = Font(name='Times New Roman', size=11, bold=True)

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Путевые листы легкового автомобиля({car.number}) за период {from_date.strftime('%d.%m.%Y')}-{to_date.strftime('%d.%m.%Y')}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        quoted_filename = quote(filename)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quoted_filename}"
        return response


class PassengerCarWaybillRecordViewSet(SoftDeleteModelViewSet):
    queryset = PassengerCarWaybillRecord.objects.select_related('passenger_car_waybill')
    serializer_class = PassengerCarWaybillRecordSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewPassengerCarWaybills()]
        elif self.action == 'create':
            return base + [CanCreatePassengerCarWaybillRecord()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePassengerCarWaybillRecord()]
        elif self.action == 'destroy':
            return base + [CanDeletePassengerCarWaybillRecord()]
        return base


# ================= ПОЖАРНЫЕ =================

class FireTruckViewSet(SoftDeleteModelViewSet):
    queryset = FireTruck.objects.all()
    serializer_class = FireTruckSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewFireTrucks()]
        elif self.action == 'create':
            return base + [CanCreateFireTrucks()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateFireTrucks()]
        elif self.action == 'destroy':
            return base + [CanDeleteFireTrucks()]
        return base


class NormsFireTruckViewSet(SoftDeleteModelViewSet):
    queryset = NormsFireTruck.objects.all()
    serializer_class = NormsFireTruckSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action == 'for_date':
            return base + [CanViewFireTruckNorms()]
        elif self.action in ['list', 'retrieve']:
            return base + [CanViewFireTruckNorms()]
        elif self.action == 'create':
            return base + [CanCreateFireTruckNorms()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateFireTruckNorms()]
        elif self.action == 'destroy':
            return base + [CanDeleteFireTruckNorms()]
        return base

    @action(detail=False, methods=['get'], url_path='for-date')
    def for_date(self, request):
        car_id = request.query_params.get('car')
        season = request.query_params.get('season')
        date_str = request.query_params.get('date')

        if not car_id or not season or not date_str:
            return Response({"detail": "Параметры car, season и date обязательны"}, status=400)

        doc_date = parse_date(date_str)
        if not doc_date:
            return Response({"detail": "Неверный формат date, ожидается YYYY-MM-DD"}, status=400)

        norm = (
            NormsFireTruck.objects
            .filter(car_id=car_id, season=season, date__lte=doc_date)
            .order_by('-date', '-id')
            .first()
        )
        if not norm:
            return Response({"detail": "Норма не найдена"}, status=404)

        serializer = self.get_serializer(norm)
        return Response(serializer.data)


class OdometerFuelFireTruckViewSet(SoftDeleteModelViewSet):
    queryset = OdometerFuelFireTruck.objects.all()
    serializer_class = OdometerFuelFireTruckSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve', 'last_record']:
            return base + [CanViewFireTrucks()]
        elif self.action == 'create':
            return base + [CanCreateFireTrucks()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateFireTrucks()]
        elif self.action == 'destroy':
            return base + [CanDeleteFireTrucks()]
        return base

    @action(detail=False, methods=['get'], url_path='last')
    def last_record(self, request):
        car_id = request.query_params.get('car')
        if not car_id:
            return Response({"detail": "Параметр car обязателен"}, status=400)

        obj = (
            OdometerFuelFireTruck.objects
            .filter(car_id=car_id)
            .order_by('-date', '-id')
            .first()
        )
        if not obj:
            return Response({"detail": "Записей не найдено"}, status=404)

        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class FireTruckWaybillViewSet(SoftDeleteModelViewSet):
    queryset = FireTruckWaybill.objects.all()
    serializer_class = FireTruckWaybillSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewFireTruckWaybills()]
        elif self.action == 'create':
            return base + [CanCreateFireTruckWaybills()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateFireTruckWaybills()]
        elif self.action == 'destroy':
            return base + [CanDeleteFireTruckWaybills()]
        elif self.action == 'export_excel':
            return base + [CanDownloadFireTruckWaybills()]
        return base

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        car_id = request.query_params.get('car')
        from_str = request.query_params.get('from')
        to_str = request.query_params.get('to')

        if not car_id or not from_str or not to_str:
            return Response({"detail": "Параметры car, from и to обязательны"}, status=400)

        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        if not from_date or not to_date:
            return Response({"detail": "Неверный формат дат, используйте YYYY-MM-DD"}, status=400)

        records = (
            FireTruckWaybillRecord.objects
            .filter(
                fire_truck_waybill__car_id=car_id,
                fire_truck_waybill__date__gte=from_date,
                fire_truck_waybill__date__lte=to_date,
            )
            .select_related('fire_truck_waybill__driver', 'fire_truck_waybill__car')
            .order_by('fire_truck_waybill__date', 'id')
        )

        if not records.exists():
            return Response({"detail": "Записей за указанный период не найдено"}, status=404)

        car = records.first().fire_truck_waybill.car

        template_path = settings.BASE_DIR / 'report_templates' / 'fire_truck.xlsx'
        wb = load_workbook(template_path)
        ws = wb.active

        ws['D2'] = car.number
        ws['K2'] = from_date.strftime('%d.%m.%Y')
        ws['R2'] = to_date.strftime('%d.%m.%Y')

        data_start_row = 7
        row_idx = data_start_row

        total_distance_km = 0
        total_time_with_pump = 0
        total_time_without_pump = 0
        total_fuel_by_distance = Decimal('0.000')
        total_fuel_with_pump = Decimal('0.000')
        total_fuel_without_pump = Decimal('0.000')
        total_fuel_normal = Decimal('0.000')
        total_fuel_fact = Decimal('0.000')
        total_fuel_refueled = Decimal('0.000')
        total_savings = Decimal('0.000')
        total_overrun = Decimal('0.000')

        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000'),
        )

        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        green_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
        red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

        center_font = Font(name='Times New Roman', size=11)
        bold_font = Font(name='Times New Roman', size=11, bold=True)
        center_align = Alignment(horizontal='center', vertical='center')

        for rec in records:
            wb_obj = rec.fire_truck_waybill
            driver = wb_obj.driver

            route = getattr(rec, 'driving_route', '') or ''
            name_place = (rec.target or '') + (f" {route}" if route else '')

            savings = Decimal('0.000')
            overrun = Decimal('0.000')

            ws.cell(row=row_idx, column=1, value=wb_obj.date.strftime('%d.%m.%Y'))
            ws.cell(row=row_idx, column=2, value=name_place)

            cell = ws.cell(row=row_idx, column=3, value=rec.fuel_before_departure)
            cell.fill = yellow_fill
            ws.cell(row=row_idx, column=4, value=rec.departure_time.strftime('%H:%M'))
            ws.cell(row=row_idx, column=5, value=rec.arrival_time.strftime('%H:%M'))
            cell = ws.cell(row=row_idx, column=6, value=rec.odometer_before)
            cell.fill = yellow_fill
            ws.cell(row=row_idx, column=7, value=rec.distance_km)
            ws.cell(row=row_idx, column=8, value=rec.fuel_used_by_distance)
            ws.cell(row=row_idx, column=9, value=rec.time_with_pump)
            ws.cell(row=row_idx, column=10, value=rec.time_without_pump)
            ws.cell(row=row_idx, column=11, value=rec.fuel_used_with_pump)
            ws.cell(row=row_idx, column=12, value=rec.fuel_used_without_pump)

            cell = ws.cell(row=row_idx, column=13, value=rec.fuel_used)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=14, value=rec.fuel_used_normal)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=15, value=rec.fuel_refueled)
            cell.fill = green_fill
            cell = ws.cell(row=row_idx, column=16, value=rec.fuel_on_return)
            cell.fill = yellow_fill
            cell = ws.cell(row=row_idx, column=17, value=rec.odometer_after)
            cell.fill = yellow_fill

            if rec.fuel_used_normal > rec.fuel_used:
                savings = rec.fuel_used_normal - rec.fuel_used
            elif rec.fuel_used_normal < rec.fuel_used:
                overrun = rec.fuel_used - rec.fuel_used_normal

            cell = ws.cell(row=row_idx, column=18, value=float(savings))
            cell.fill = green_fill
            cell = ws.cell(row=row_idx, column=19, value=float(overrun))
            cell.fill = red_fill

            total_distance_km += rec.distance_km
            total_time_with_pump += rec.time_with_pump
            total_time_without_pump += rec.time_without_pump
            total_fuel_by_distance += rec.fuel_used_by_distance
            total_fuel_with_pump += rec.fuel_used_with_pump
            total_fuel_without_pump += rec.fuel_used_without_pump
            total_fuel_normal += rec.fuel_used_normal
            total_fuel_fact += rec.fuel_used
            total_fuel_refueled += rec.fuel_refueled
            total_savings += savings
            total_overrun += overrun

            row_idx += 1

        cell = ws.cell(row=row_idx, column=2, value="ИТОГО")
        cell.fill = yellow_fill

        ws.cell(row=row_idx, column=7, value=total_distance_km).fill = yellow_fill
        ws.cell(row=row_idx, column=9, value=total_time_with_pump).fill = yellow_fill
        ws.cell(row=row_idx, column=10, value=total_time_without_pump).fill = yellow_fill
        ws.cell(row=row_idx, column=8, value=float(total_fuel_by_distance)).fill = yellow_fill
        ws.cell(row=row_idx, column=11, value=float(total_fuel_with_pump)).fill = yellow_fill
        ws.cell(row=row_idx, column=12, value=float(total_fuel_without_pump)).fill = yellow_fill
        ws.cell(row=row_idx, column=13, value=float(total_fuel_fact)).fill = yellow_fill
        ws.cell(row=row_idx, column=14, value=float(total_fuel_normal)).fill = yellow_fill
        ws.cell(row=row_idx, column=15, value=float(total_fuel_refueled)).fill = green_fill
        ws.cell(row=row_idx, column=18, value=float(total_savings)).fill = green_fill
        ws.cell(row=row_idx, column=19, value=float(total_overrun)).fill = red_fill

        data_end_row = row_idx
        for r in range(data_start_row, data_end_row + 1):
            for c in range(1, 21 + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = thin_border
                cell.font = center_font
                cell.alignment = center_align

        for c in range(1, 19 + 1):
            ws.cell(row=data_end_row, column=c).font = bold_font

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Путевые листы пожарного автомобиля({car.number}) за период {from_date.strftime('%d.%m.%Y')}-{to_date.strftime('%d.%m.%Y')}.xlsx"
        quoted_filename = quote(filename)

        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quoted_filename}"
        return response


class FireTruckWaybillRecordViewSet(SoftDeleteModelViewSet):
    queryset = FireTruckWaybillRecord.objects.select_related('fire_truck_waybill')
    serializer_class = FireTruckWaybillRecordSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewFireTruckWaybills()]
        elif self.action == 'create':
            return base + [CanCreateFireTruckWaybillRecord()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateFireTruckWaybillRecord()]
        elif self.action == 'destroy':
            return base + [CanDeleteFireTruckWaybillRecord()]
        return base


# ================= МОТОЧАСЫ / ТО =================

class OperatingHoursCarsViewSet(SoftDeleteModelViewSet):
    queryset = OperatingHoursCars.objects.all().order_by('-date', '-id')
    serializer_class = OperatingHoursCarsSerializer
    http_method_names = ['get', 'head', 'options']

    def get_permissions(self):
        return [IsAuthenticated(), CanViewOperatingHours()]


class NormsOperatingHoursPassengerCarViewSet(SoftDeleteModelViewSet):
    queryset = NormsOperatingHoursPassengerCar.objects.all()
    serializer_class = NormsOperatingHoursPassengerCarSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewPassengerCarNorms()]
        elif self.action == 'create':
            return base + [CanCreatePassengerCarNorms()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdatePassengerCarNorms()]
        elif self.action == 'destroy':
            return base + [CanDeletePassengerCarNorms()]
        return base


class NormsOperatingHoursFireTruckViewSet(SoftDeleteModelViewSet):
    queryset = NormsOperatingHoursFireTruck.objects.all()
    serializer_class = NormsOperatingHoursFireTruckSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewFireTruckNorms()]
        elif self.action == 'create':
            return base + [CanCreateFireTruckNorms()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateFireTruckNorms()]
        elif self.action == 'destroy':
            return base + [CanDeleteFireTruckNorms()]
        return base


class NormsTechnicalMaintenanceViewSet(SoftDeleteModelViewSet):
    queryset = NormsTechnicalMaintenance.objects.all()
    serializer_class = NormsTechnicalMaintenanceSerializer

    def get_queryset(self):
        user = self.request.user
        role_perm = getattr(getattr(user, 'role', None), 'role', None)

        if not role_perm:
            return NormsTechnicalMaintenance.objects.none()

        can_passenger = getattr(role_perm, 'view_passenger_cars_norms', False)
        can_fire = getattr(role_perm, 'view_fire_truck_norms', False)

        qs = NormsTechnicalMaintenance.objects.all()

        if can_passenger and can_fire:
            return qs
        elif can_passenger:
            return qs.filter(fire_truck__isnull=True)
        elif can_fire:
            return qs.filter(passenger_car__isnull=True)
        return qs.none()

    def get_permissions(self):
        return [IsAuthenticated()]


class TechnicalMaintenanceViewSet(SoftDeleteModelViewSet):
    queryset = TechnicalMaintenance.objects.all()
    serializer_class = TechnicalMaintenanceSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return base + [CanViewTechnicalMaintenance()]
        elif self.action == 'create':
            return base + [CanCreateTechnicalMaintenance()]
        elif self.action in ['update', 'partial_update']:
            return base + [CanUpdateTechnicalMaintenance()]
        elif self.action == 'destroy':
            return base + [CanDeleteTechnicalMaintenance()]
        return base


class MaintenanceNotificationViewSet(SoftDeleteModelViewSet):
    queryset = MaintenanceNotification.objects.all().order_by('-created_at')
    serializer_class = MaintenanceNotificationSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        obj = self.get_object()
        obj.is_read = True
        obj.save(update_fields=['is_read'])
        return Response({'detail': 'Уведомление отмечено как прочитанное'})