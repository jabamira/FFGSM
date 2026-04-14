# fuel/statistics.py
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
    User, PassengerCar, FireTruck
)
from .permissions import (
    CanViewPassengerCarWaybills, CanViewFireTruckWaybills
)


class FuelStatisticsViewSet(viewsets.ViewSet):
    """
    Полная статистика по топливу за период
    """
    permission_classes = [IsAuthenticated, CanViewPassengerCarWaybills]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Получить полную статистику за период
        GET /api/statistics/summary/?from=2025-01-01&to=2025-01-31&vehicle_type=all
        GET /api/statistics/summary/?vehicle_type=all (загрузит все время)
        
        Parameters:
        - vehicle_type: all | passenger-car | fire-truck
        - from, to: опциональны (если не указаны - загружается статистика за всё время)
        - vehicle_type_prefix: ft (fire-truck) | pc (passenger-car) - для фильтра конкретной машины
        - vehicle_id: ID конкретной машины (если указан vehicle_type_prefix)
        - driver_id: ID конкретного водителя
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
            
            # Если даты указаны, их нужно обе
            if (from_str and not to_str) or (not from_str and to_str):
                return Response(
                    {"detail": "Либо укажите обе даты (from и to), либо ни одну"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from_date = None
            to_date = None
            
            if from_str and to_str:
                from_date = parse_date(from_str)
                to_date = parse_date(to_str)
                
                if not from_date or not to_date:
                    return Response(
                        {"detail": "Неверный формат дат"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            stats = {
                'period': {
                    'from': from_date.isoformat() if from_date else None,
                    'to': to_date.isoformat() if to_date else None,
                    'all_time': from_date is None and to_date is None
                },
                'daily_fuel': {},  # Will store daily aggregates
                'passenger_cars': {},
                'fire_trucks': {},
                'drivers': {},
                'total': {
                    'fuel_used': 0,
                    'fuel_by_norm': 0,
                    'distance': 0,
                    'trip_count': 0,
                    'difference': 0
                }
            }
            
            # ========== ЛЕГКОВЫЕ АВТОМОБИЛИ ==========
            if vehicle_type in ['all', 'passenger-car']:
                query = PassengerCarWaybill.objects.filter(deleted_at__isnull=True)
                
                if from_date and to_date:
                    query = query.filter(date__gte=from_date, date__lte=to_date)
                
                # Filter by specific vehicle if requested
                if vehicle_type_prefix == 'pc' and vehicle_id:
                    query = query.filter(car_id=int(vehicle_id))
                
                # Filter by driver if requested
                if driver_id:
                    query = query.filter(driver_id=int(driver_id))
                
                pc_waybills = query.select_related('car', 'driver').prefetch_related('records')
                
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'[Statistics] Processing {pc_waybills.count()} passenger car waybills')
                
                for waybill in pc_waybills:
                    car = waybill.car
                    driver = waybill.driver
                    
                    fuel_used = float(waybill.total_spent or 0)
                    fuel_by_norm = float(waybill.required_by_norm or 0)
                    
                    # Aggregate by day
                    date_key = waybill.date.isoformat()
                    if date_key not in stats['daily_fuel']:
                        stats['daily_fuel'][date_key] = {'fuel_used': 0, 'fuel_by_norm': 0}
                    stats['daily_fuel'][date_key]['fuel_used'] += fuel_used
                    stats['daily_fuel'][date_key]['fuel_by_norm'] += fuel_by_norm
                    
                    # Инициализировать данные машины
                    car_key = car.id
                    if car_key not in stats['passenger_cars']:
                        stats['passenger_cars'][car_key] = {
                            'number': car.number,
                            'brand': car.brand,
                            'model': car.model,
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0
                        }
                    
                    # Считаем расстояние для легкового авто
                    distance = 0
                    if waybill.records.exists():
                        distance = waybill.records.aggregate(
                            total=Sum('distance_city_km', output_field=IntegerField())
                        )['total'] or 0
                        distance += waybill.records.aggregate(
                            total=Sum('distance_area_km', output_field=IntegerField())
                        )['total'] or 0
                    
                    trip_count = waybill.records.count()
                    difference = fuel_used - fuel_by_norm
                    
                    stats['passenger_cars'][car_key]['fuel_used'] += fuel_used
                    stats['passenger_cars'][car_key]['fuel_by_norm'] += fuel_by_norm
                    stats['passenger_cars'][car_key]['distance'] += distance
                    stats['passenger_cars'][car_key]['trip_count'] += trip_count
                    stats['passenger_cars'][car_key]['difference'] += difference
                    
                    # Добавить в данные водителей
                    driver_key = driver.id
                    if driver_key not in stats['drivers']:
                        stats['drivers'][driver_key] = {
                            'id': driver.id,
                            'name': f"{driver.surname} {driver.name} {driver.last_name}".strip(),
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0
                        }
                    
                    stats['drivers'][driver_key]['fuel_used'] += fuel_used
                    stats['drivers'][driver_key]['fuel_by_norm'] += fuel_by_norm
                    stats['drivers'][driver_key]['distance'] += distance
                    stats['drivers'][driver_key]['trip_count'] += trip_count
                    stats['drivers'][driver_key]['difference'] += difference
                    
                    # Добавить в общий итог
                    stats['total']['fuel_used'] += fuel_used
                    stats['total']['fuel_by_norm'] += fuel_by_norm
                    stats['total']['distance'] += distance
                    stats['total']['trip_count'] += trip_count
                    stats['total']['difference'] += difference
            
            # ========== ПОЖАРНЫЕ АВТОМОБИЛИ ==========
            if vehicle_type in ['all', 'fire-truck']:
                query = FireTruckWaybill.objects.filter(deleted_at__isnull=True)
                
                if from_date and to_date:
                    query = query.filter(date__gte=from_date, date__lte=to_date)
                
                # Filter by specific vehicle if requested
                if vehicle_type_prefix == 'ft' and vehicle_id:
                    query = query.filter(car_id=int(vehicle_id))
                
                # Filter by driver if requested
                if driver_id:
                    query = query.filter(driver_id=int(driver_id))
                
                ft_waybills = query.select_related('car', 'driver').prefetch_related('records')
                
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'[Statistics] Processing {ft_waybills.count()} fire truck waybills')
                
                for waybill in ft_waybills:
                    car = waybill.car
                    driver = waybill.driver
                    
                    fuel_used = float(waybill.total_spent or 0)
                    fuel_by_norm = float(waybill.required_by_norm or 0)
                    
                    # Aggregate by day
                    date_key = waybill.date.isoformat()
                    if date_key not in stats['daily_fuel']:
                        stats['daily_fuel'][date_key] = {'fuel_used': 0, 'fuel_by_norm': 0}
                    stats['daily_fuel'][date_key]['fuel_used'] += fuel_used
                    stats['daily_fuel'][date_key]['fuel_by_norm'] += fuel_by_norm
                    
                    # Инициализировать данные машины
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
                            'difference': 0
                        }
                    
                    # Считаем расстояние для пожарного авто из одометра
                    distance = 0
                    if waybill.records.exists():
                        distance = waybill.records.aggregate(
                            total=Sum('distance_km', output_field=IntegerField())
                        )['total'] or 0
                    
                    fuel_used = float(waybill.total_spent or 0)
                    fuel_by_norm = float(waybill.required_by_norm or 0)
                    trip_count = waybill.records.count()
                    difference = fuel_used - fuel_by_norm
                    
                    stats['fire_trucks'][car_key]['fuel_used'] += fuel_used
                    stats['fire_trucks'][car_key]['fuel_by_norm'] += fuel_by_norm
                    stats['fire_trucks'][car_key]['distance'] += distance
                    stats['fire_trucks'][car_key]['trip_count'] += trip_count
                    stats['fire_trucks'][car_key]['difference'] += difference
                    
                    # Добавить в данные водителей
                    driver_key = driver.id
                    if driver_key not in stats['drivers']:
                        stats['drivers'][driver_key] = {
                            'id': driver.id,
                            'name': f"{driver.surname} {driver.name} {driver.last_name}".strip(),
                            'fuel_used': 0,
                            'fuel_by_norm': 0,
                            'distance': 0,
                            'trip_count': 0,
                            'difference': 0
                        }
                    
                    stats['drivers'][driver_key]['fuel_used'] += fuel_used
                    stats['drivers'][driver_key]['fuel_by_norm'] += fuel_by_norm
                    stats['drivers'][driver_key]['distance'] += distance
                    stats['drivers'][driver_key]['trip_count'] += trip_count
                    stats['drivers'][driver_key]['difference'] += difference
                    
                    # Добавить в общий итог
                    stats['total']['fuel_used'] += fuel_used
                    stats['total']['fuel_by_norm'] += fuel_by_norm
                    stats['total']['distance'] += distance
                    stats['total']['trip_count'] += trip_count
                    stats['total']['difference'] += difference
            
            # Конвертировать в списки для JSON сериализации
            # Daily fuel: sort by date
            daily_fuel_list = [
                {'date': date, 'fuel_used': data['fuel_used'], 'fuel_by_norm': data['fuel_by_norm']}
                for date, data in sorted(stats['daily_fuel'].items())
            ]
            stats['daily_fuel'] = daily_fuel_list
            
            stats['passenger_cars'] = list(stats['passenger_cars'].values())
            stats['fire_trucks'] = list(stats['fire_trucks'].values())
            stats['drivers'] = list(stats['drivers'].values())
            
            # Логирование
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'[Statistics] Loaded {len(stats["passenger_cars"])} passenger cars, {len(stats["fire_trucks"])} fire trucks, {len(stats["drivers"])} drivers')
            logger.warning(f'[Statistics] Drivers: {[d["name"] for d in stats["drivers"]]}')
            if stats['drivers']:
                logger.warning(f'[Statistics] First driver details: {stats["drivers"][0]}')
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": f"Ошибка при создании статистики: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
