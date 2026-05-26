from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, F, DecimalField, IntegerField
from django.db.models.functions import Cast
from decimal import Decimal

from .models import (
    PassengerCarWaybill, PassengerCarWaybillRecord,
    FireTruckWaybill, FireTruckWaybillRecord,
    User, PassengerCar, FireTruck, OperatingHoursCars
)
from .permissions import (
    CanViewPassengerCarWaybills, CanViewFireTruckWaybills
)


class FuelStatisticsViewSet(viewsets.ViewSet):
    """
    Полная статистика по топливу за период - ПРАВИЛЬНЫЙ РАСЧЕТ
    """
    permission_classes = [IsAuthenticated, CanViewPassengerCarWaybills]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Получить полную статистику за период
        
        Логика расчетов:
        - fuel_used: сумма fuel_used из всех records путевых листов
        - fuel_by_norm: сумма fuel_used_normal из всех records
        - distance: max(odometer_after) - min(odometer_before) в периоде
        - trip_count: количество records (каждая запись = 1 выезд)
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            from_str = request.query_params.get('from')
            to_str = request.query_params.get('to')
            vehicle_type = request.query_params.get('vehicle_type', 'all')
            vehicle_type_prefix = request.query_params.get('vehicle_type_prefix')
            vehicle_id = request.query_params.get('vehicle_id')
            driver_id = request.query_params.get('driver_id')
            
            # Парсим даты
            from_date = None
            to_date = None
            
            if from_str and to_str:
                from_date = parse_date(from_str)
                to_date = parse_date(to_str)
            
            stats = {
                'period': {
                    'from': from_date.isoformat() if from_date else None,
                    'to': to_date.isoformat() if to_date else None,
                    'all_time': from_date is None and to_date is None
                },
                'daily_fuel': {},
                'passenger_cars': {},
                'fire_trucks': {},
                'drivers': {},
                'total': {
                    'fuel_used': 0,
                    'fuel_by_norm': 0,
                    'distance': 0,
                    'trip_count': 0,
                    'trip_count_passenger_cars': 0,
                    'trip_count_fire_trucks': 0,
                    'operating_hours': 0,
                    'difference': 0
                }
            }
            
            # Если выбрана конкретная машина - определяем тип по vehicle_type_prefix
            actual_vehicle_type = vehicle_type
            if vehicle_type_prefix == 'pc':
                actual_vehicle_type = 'passenger-car'
            elif vehicle_type_prefix == 'ft':
                actual_vehicle_type = 'fire-truck'
            
            logger.warning(f'[Statistics] vehicle_type={vehicle_type}, vehicle_type_prefix={vehicle_type_prefix}, actual_vehicle_type={actual_vehicle_type}')
            
            # ========== ЛЕГКОВЫЕ АВТОМОБИЛИ ==========
            if actual_vehicle_type in ['all', 'passenger-car']:
                logger.warning('[Statistics] Processing PASSENGER CARS')
                
                pc_query = PassengerCarWaybill.objects.filter(deleted_at__isnull=True)
                if from_date and to_date:
                    pc_query = pc_query.filter(date__gte=from_date, date__lte=to_date)
                if vehicle_type_prefix == 'pc' and vehicle_id:
                    pc_query = pc_query.filter(car_id=int(vehicle_id))
                if driver_id:
                    pc_query = pc_query.filter(driver_id=int(driver_id))
                
                pc_waybills = pc_query.select_related('car', 'driver').prefetch_related('records')
                
                for waybill in pc_waybills:
                    car = waybill.car
                    driver = waybill.driver
                    records = list(waybill.records.all())
                    
                    if not records:
                        continue
                    
                    # Считаем метрики из RECORDS
                    fuel_used = sum(float(r.fuel_used or 0) for r in records)
                    fuel_by_norm = sum(float(r.fuel_used_normal or 0) for r in records)
                    trip_count = len(records)
                    
                    # Distance = last_odometer_after - first_odometer_before
                    first_record = min(records, key=lambda r: r.id)
                    last_record = max(records, key=lambda r: r.id)
                    distance = (last_record.odometer_after or 0) - (first_record.odometer_before or 0)
                    
                    difference = fuel_used - fuel_by_norm
                    
                    # Добавляем в ежедневную статистику
                    date_key = waybill.date.isoformat()
                    if date_key not in stats['daily_fuel']:
                        stats['daily_fuel'][date_key] = {'fuel_used': 0, 'fuel_by_norm': 0, 'operating_hours': 0}
                    
                    stats['daily_fuel'][date_key]['fuel_used'] += fuel_used
                    stats['daily_fuel'][date_key]['fuel_by_norm'] += fuel_by_norm
                    
                    # Считаем operating_hours из записей
                    op_hours_for_records = sum(
                        float(r.operating_hours_record.operating_hours or 0) 
                        for r in records 
                        if r.operating_hours_record
                    )
                    
                    # Убеждаемся что ключ существует перед добавлением
                    if 'operating_hours' not in stats['daily_fuel'][date_key]:
                        stats['daily_fuel'][date_key]['operating_hours'] = 0
                    stats['daily_fuel'][date_key]['operating_hours'] += op_hours_for_records
                    
                    # Данные машины
                    car_key = car.id
                    if car_key not in stats['passenger_cars']:
                        stats['passenger_cars'][car_key] = {
                            'id': car.id,
                            'number': car.number,
                            'brand': car.brand,
                            'model': car.model,
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0,
                            'operating_hours': 0
                        }
                    
                    stats['passenger_cars'][car_key]['fuel_used'] += fuel_used
                    stats['passenger_cars'][car_key]['fuel_by_norm'] += fuel_by_norm
                    stats['passenger_cars'][car_key]['distance'] += distance
                    stats['passenger_cars'][car_key]['trip_count'] += trip_count
                    stats['passenger_cars'][car_key]['difference'] += difference
                    
                    # Данные водителя
                    driver_key = driver.id
                    if driver_key not in stats['drivers']:
                        driver_name = driver.name or ""
                        if hasattr(driver, 'last_name') and driver.last_name:
                            driver_name = f"{driver_name} {driver.last_name}".strip()
                        if hasattr(driver, 'surname') and driver.surname:
                            driver_name = f"{driver.surname} {driver_name}".strip()
                        if not driver_name:
                            driver_name = f"Водитель {driver.id}"
                        
                        stats['drivers'][driver_key] = {
                            'id': driver.id,
                            'name': driver_name,
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0,
                            'operating_hours': 0
                        }
                    
                    # Считаем operating_hours из записей
                    op_hours_for_records = sum(
                        float(r.operating_hours_record.operating_hours or 0) 
                        for r in records 
                        if r.operating_hours_record
                    )
                    
                    stats['drivers'][driver_key]['fuel_used'] += fuel_used
                    stats['drivers'][driver_key]['fuel_by_norm'] += fuel_by_norm
                    stats['drivers'][driver_key]['distance'] += distance
                    stats['drivers'][driver_key]['trip_count'] += trip_count
                    stats['drivers'][driver_key]['difference'] += difference
                    stats['drivers'][driver_key]['operating_hours'] += op_hours_for_records
                    
                    # Добавляем operating_hours к машине
                    stats['passenger_cars'][car_key]['operating_hours'] += op_hours_for_records
                    
                    # Общий итог
                    stats['total']['fuel_used'] += fuel_used
                    stats['total']['fuel_by_norm'] += fuel_by_norm
                    stats['total']['distance'] += distance
                    stats['total']['trip_count'] += trip_count
                    stats['total']['trip_count_passenger_cars'] += trip_count
                    stats['total']['difference'] += difference
            
            # ========== ПОЖАРНЫЕ АВТОМОБИЛИ ==========
            if actual_vehicle_type in ['all', 'fire-truck']:
                logger.warning('[Statistics] Processing FIRE TRUCKS')
                
                ft_query = FireTruckWaybill.objects.filter(deleted_at__isnull=True)
                if from_date and to_date:
                    ft_query = ft_query.filter(date__gte=from_date, date__lte=to_date)
                if vehicle_type_prefix == 'ft' and vehicle_id:
                    ft_query = ft_query.filter(car_id=int(vehicle_id))
                if driver_id:
                    ft_query = ft_query.filter(driver_id=int(driver_id))
                
                ft_waybills = ft_query.select_related('car', 'driver').prefetch_related('records')
                
                for waybill in ft_waybills:
                    car = waybill.car
                    driver = waybill.driver
                    records = list(waybill.records.all())
                    
                    if not records:
                        continue
                    
                    # Считаем метрики из RECORDS
                    fuel_used = sum(float(r.fuel_used or 0) for r in records)
                    fuel_by_norm = sum(float(r.fuel_used_normal or 0) for r in records)
                    trip_count = len(records)
                    
                    # Distance = last_odometer_after - first_odometer_before
                    first_record = min(records, key=lambda r: r.id)
                    last_record = max(records, key=lambda r: r.id)
                    distance = (last_record.odometer_after or 0) - (first_record.odometer_before or 0)
                    
                    difference = fuel_used - fuel_by_norm
                    
                    # Добавляем в ежедневную статистику
                    date_key = waybill.date.isoformat()
                    if date_key not in stats['daily_fuel']:
                        stats['daily_fuel'][date_key] = {'fuel_used': 0, 'fuel_by_norm': 0, 'operating_hours': 0}
                    
                    stats['daily_fuel'][date_key]['fuel_used'] += fuel_used
                    stats['daily_fuel'][date_key]['fuel_by_norm'] += fuel_by_norm
                    
                    # Считаем operating_hours из записей
                    op_hours_for_records = sum(
                        float(r.operating_hours_record.operating_hours or 0) 
                        for r in records 
                        if r.operating_hours_record
                    )
                    
                    # Убеждаемся что ключ существует перед добавлением
                    if 'operating_hours' not in stats['daily_fuel'][date_key]:
                        stats['daily_fuel'][date_key]['operating_hours'] = 0
                    stats['daily_fuel'][date_key]['operating_hours'] += op_hours_for_records
                    
                    # Данные машины
                    car_key = f"ft_{car.id}"
                    if car_key not in stats['fire_trucks']:
                        stats['fire_trucks'][car_key] = {
                            'id': car.id,
                            'number': car.number,
                            'brand': car.brand,
                            'model': car.model,
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0,
                            'operating_hours': 0
                        }
                    
                    # Считаем operating_hours из записей
                    op_hours_for_records = sum(
                        float(r.operating_hours_record.operating_hours or 0) 
                        for r in records 
                        if r.operating_hours_record
                    )
                    
                    stats['fire_trucks'][car_key]['fuel_used'] += fuel_used
                    stats['fire_trucks'][car_key]['fuel_by_norm'] += fuel_by_norm
                    stats['fire_trucks'][car_key]['distance'] += distance
                    stats['fire_trucks'][car_key]['trip_count'] += trip_count
                    stats['fire_trucks'][car_key]['difference'] += difference
                    stats['fire_trucks'][car_key]['operating_hours'] += op_hours_for_records
                    
                    # Данные водителя
                    driver_key = driver.id
                    if driver_key not in stats['drivers']:
                        driver_name = driver.name or ""
                        if hasattr(driver, 'last_name') and driver.last_name:
                            driver_name = f"{driver_name} {driver.last_name}".strip()
                        if hasattr(driver, 'surname') and driver.surname:
                            driver_name = f"{driver.surname} {driver_name}".strip()
                        if not driver_name:
                            driver_name = f"Водитель {driver.id}"
                        
                        stats['drivers'][driver_key] = {
                            'id': driver.id,
                            'name': driver_name,
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0,
                            'operating_hours': 0
                        }
                    
                    stats['drivers'][driver_key]['fuel_used'] += fuel_used
                    stats['drivers'][driver_key]['fuel_by_norm'] += fuel_by_norm
                    stats['drivers'][driver_key]['distance'] += distance
                    stats['drivers'][driver_key]['trip_count'] += trip_count
                    stats['drivers'][driver_key]['difference'] += difference
                    stats['drivers'][driver_key]['operating_hours'] += op_hours_for_records
                    
                    # Общий итог
                    stats['total']['fuel_used'] += fuel_used
                    stats['total']['fuel_by_norm'] += fuel_by_norm
                    stats['total']['distance'] += distance
                    stats['total']['trip_count'] += trip_count
                    stats['total']['trip_count_fire_trucks'] += trip_count
                    stats['total']['difference'] += difference
            
            # Конвертируем в список
            daily_fuel_list = [
                {'date': date, 'fuel_used': data['fuel_used'], 'fuel_by_norm': data['fuel_by_norm'], 'operating_hours': data['operating_hours']}
                for date, data in sorted(stats['daily_fuel'].items())
            ]
            stats['daily_fuel'] = daily_fuel_list
            stats['passenger_cars'] = list(stats['passenger_cars'].values())
            stats['fire_trucks'] = list(stats['fire_trucks'].values())
            stats['drivers'] = list(stats['drivers'].values())
            
            # Operating hours - если выбран конкретный автомобиль или тип машины (но не водитель)
            should_calc_op_hours = False
            
            try:
                if driver_id:
                    # Расчет моточасов по водителю - ищем моточасы всех его путевых листов
                    op_hours = Decimal('0')
                    
                    # Пассажирские путевые листы водителя
                    pc_waybills = PassengerCarWaybill.objects.filter(
                        driver_id=int(driver_id),
                        deleted_at__isnull=True
                    )
                    if from_date and to_date:
                        pc_waybills = pc_waybills.filter(date__gte=from_date, date__lte=to_date)
                    
                    for waybill in pc_waybills:
                        records = waybill.records.filter(operating_hours_record__isnull=False)
                        for record in records:
                            if record.operating_hours_record:
                                op_hours += record.operating_hours_record.operating_hours or Decimal('0')
                    
                    # Пожарные путевые листы водителя
                    ft_waybills = FireTruckWaybill.objects.filter(
                        driver_id=int(driver_id),
                        deleted_at__isnull=True
                    )
                    if from_date and to_date:
                        ft_waybills = ft_waybills.filter(date__gte=from_date, date__lte=to_date)
                    
                    for waybill in ft_waybills:
                        records = waybill.records.filter(operating_hours_record__isnull=False)
                        for record in records:
                            if record.operating_hours_record:
                                op_hours += record.operating_hours_record.operating_hours or Decimal('0')
                    
                    stats['total']['operating_hours'] = float(op_hours)
                    logger.warning(f'[Statistics] Operating hours for driver {driver_id}: {float(op_hours)}')
                    
                else:
                    # Расчет моточасов по машинам/типам
                    op_query = OperatingHoursCars.objects.filter(deleted_at__isnull=True)
                    if from_date and to_date:
                        op_query = op_query.filter(date__gte=from_date, date__lte=to_date)
                    
                    if vehicle_type_prefix == 'pc' and vehicle_id:
                        # Конкретный пассажирский автомобиль
                        op_query = op_query.filter(passenger_car_id=int(vehicle_id))
                        should_calc_op_hours = True
                    elif vehicle_type_prefix == 'ft' and vehicle_id:
                        # Конкретный пожарный автомобиль
                        op_query = op_query.filter(fire_truck_id=int(vehicle_id))
                        should_calc_op_hours = True
                    elif not vehicle_type_prefix:
                        # Тип машины без конкретной машины
                        if actual_vehicle_type == 'passenger-car':
                            op_query = op_query.filter(passenger_car_id__isnull=False)
                            should_calc_op_hours = True
                        elif actual_vehicle_type == 'fire-truck':
                            op_query = op_query.filter(fire_truck_id__isnull=False)
                            should_calc_op_hours = True
                        elif actual_vehicle_type == 'all':
                            # Все машины
                            should_calc_op_hours = True
                    
                    if should_calc_op_hours:
                        total_op_hours = op_query.aggregate(total=Sum('operating_hours'))['total'] or Decimal('0')
                        stats['total']['operating_hours'] = float(total_op_hours)
                        logger.warning(f'[Statistics] Operating hours calculated: {stats["total"]["operating_hours"]}')
                    else:
                        logger.warning('[Statistics] Operating hours NOT calculated')
                    
            except Exception as e:
                logger.error(f'[Statistics] Operating hours error: {str(e)}')
                stats['total']['operating_hours'] = 0
            
            logger.warning(f'[Statistics] FINAL: fuel_used={stats["total"]["fuel_used"]}, distance={stats["total"]["distance"]}, trip_count={stats["total"]["trip_count"]}')
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            logger.error(f'[Statistics] ERROR: {str(e)}')
            logger.error(traceback.format_exc())
            return Response(
                {"detail": f"Ошибка статистики: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
