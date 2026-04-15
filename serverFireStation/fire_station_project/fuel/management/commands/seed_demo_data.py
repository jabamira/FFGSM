# fuel/management/commands/fill_db.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from decimal import Decimal
from datetime import date, time, timedelta
from random import randint, choice

from fuel.models import (
    Role, User,
    PassengerCar, FireTruck,
    NormsPassengerCars, NormsFireTruck,
    NormsOperatingHoursPassengerCar, NormsOperatingHoursFireTruck,
    NormsTechnicalMaintenance,
    OdometerFuelPassengerCar, OdometerFuelFireTruck,
    PassengerCarWaybill, PassengerCarWaybillRecord,
    FireTruckWaybill, FireTruckWaybillRecord,
    TechnicalMaintenance,
    OperatingHoursCars,
)


class Command(BaseCommand):
    help = "Полное заполнение БД тестовыми данными"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Полностью удалить ранее созданные демо-данные и заполнить заново',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get('reset', False)

        self.stdout.write(self.style.NOTICE("=== Заполнение полной тестовой БД ==="))

        # ---------------- РОЛИ ----------------
        admin_role = Role.objects.filter(name="Администратор").first()
        mechanic_role = Role.objects.filter(name="Механик").first()
        driver_role = Role.objects.filter(name="Водитель").first()

        if not admin_role or not mechanic_role or not driver_role:
            self.stdout.write(self.style.ERROR(
                "Не найдены роли. Сначала должны быть созданы роли и permissions."
            ))
            return

        demo_logins = [
            'admin',
            'mechanic',
            'driver_0',
            'driver_1',
            'driver_2',
            'driver_3',
            'driver_4',
            'driver_5',
        ]

        passenger_numbers = ['А001АА54', 'А002АА54']
        fire_numbers = ['X111РУ54', 'X222РУ54']

        if reset:
            self.stdout.write(self.style.WARNING("Полностью удаляем старые demo-данные..."))
            self.reset_demo_data(
                demo_logins=demo_logins,
                passenger_numbers=passenger_numbers,
                fire_numbers=fire_numbers,
            )
            self.stdout.write(self.style.SUCCESS("Старые demo-данные полностью удалены"))

        # ---------------- ПОЛЬЗОВАТЕЛИ (8 шт.) ----------------
        users_data = []

        # 1 админ
        users_data.append({
            "login": "admin",
            "password": "admin123",
            "name": "Системный",
            "surname": "Администратор",
            "last_name": "Demo",
            "phone": "79000000001",  # 11 цифр
            "driver_license": None,
            "role": admin_role,
        })

        # 1 механик
        users_data.append({
            "login": "mechanic",
            "password": "mechanic123",
            "name": "Иван",
            "surname": "Механиков",
            "last_name": "Петрович",
            "phone": "79000000002",  # 11 цифр
            "driver_license": None,
            "role": mechanic_role,
        })

        # 6 водителей
        for i in range(6):
            users_data.append({
                "login": f"driver_{i}",
                "password": "driver123",
                "name": f"Водитель{i + 1}",
                "surname": "Тестов",
                "last_name": "Иванович",
                "phone": f"790000000{str(i + 3).zfill(2)}",  # 79000000003..79000000008
                "driver_license": f"{i+1:09d}",  # 9 цифр
                "role": driver_role,
            })

        created_users = {}
        for data in users_data:
            user = self.create_user_force(data)
            created_users[user.login] = user
            self.stdout.write(self.style.SUCCESS(f'Пользователь "{user.login}" создан'))

        # ---------------- МАШИНЫ ----------------
        passenger_car_1 = self.recreate(
            PassengerCar,
            {"number": "А001АА54"},
            {
                "number": "А001АА54",
                "brand": "Toyota",
                "model": "Camry",
                "fuel_type": "petrol95",
            }
        )
        passenger_car_2 = self.recreate(
            PassengerCar,
            {"number": "А002АА54"},
            {
                "number": "А002АА54",
                "brand": "Lada",
                "model": "Vesta",
                "fuel_type": "petrol92",
            }
        )

        fire_truck_1 = self.recreate(
            FireTruck,
            {"number": "X111РУ54"},
            {
                "number": "X111РУ54",
                "brand": "КАМАЗ",
                "model": "43118",
                "type": "АЦ-3,2-40",
                "fuel_type": "diesel",
            }
        )
        fire_truck_2 = self.recreate(
            FireTruck,
            {"number": "X222РУ54"},
            {
                "number": "X222РУ54",
                "brand": "УРАЛ",
                "model": "5557",
                "type": "АЦ-5,0-40",
                "fuel_type": "diesel",
            }
        )

        self.stdout.write(self.style.SUCCESS("Автомобили созданы"))

        # ---------------- НОРМЫ ТОПЛИВА ----------------
        for car in [passenger_car_1, passenger_car_2]:
            for season in ['summer', 'winter']:
                NormsPassengerCars.objects.create(
                    car=car,
                    season=season,
                    date=date(2025, 1, 1),
                    city_norm=Decimal('0.090') if season == 'summer' else Decimal('0.100'),
                    area_norm=Decimal('0.110') if season == 'summer' else Decimal('0.120'),
                )

        for car in [fire_truck_1, fire_truck_2]:
            for season in ['summer', 'winter']:
                NormsFireTruck.objects.create(
                    car=car,
                    season=season,
                    date=date(2025, 1, 1),
                    with_pump_norm=Decimal('0.250') if season == 'summer' else Decimal('0.300'),
                    without_pump_norm=Decimal('0.120') if season == 'summer' else Decimal('0.150'),
                    km_norm=Decimal('0.180') if season == 'summer' else Decimal('0.200'),
                )

        self.stdout.write(self.style.SUCCESS("Нормы топлива созданы"))

        # ---------------- НОРМЫ МОТОЧАСОВ ----------------
        for car in [passenger_car_1, passenger_car_2]:
            NormsOperatingHoursPassengerCar.objects.create(
                car=car,
                date=date(2025, 1, 1),
                city_norm=Decimal('0.0200'),
                area_norm=Decimal('0.0150'),
            )

        for car in [fire_truck_1, fire_truck_2]:
            NormsOperatingHoursFireTruck.objects.create(
                car=car,
                date=date(2025, 1, 1),
                km_norm=Decimal('0.0100'),
                with_pump_norm=Decimal('0.0500'),
            )

        self.stdout.write(self.style.SUCCESS("Нормы моточасов созданы"))

        # ---------------- НОРМЫ ТО ----------------
        maintenance_types = ['engine_oil', 'air_filter', 'cabine_filter', 'antifreeze']

        for car in [passenger_car_1, passenger_car_2]:
            for mt in maintenance_types:
                default_norm = {
                    'engine_oil': Decimal('250.000'),
                    'air_filter': Decimal('200.000'),
                    'cabine_filter': Decimal('300.000'),
                    'antifreeze': Decimal('500.000'),
                }[mt]

                NormsTechnicalMaintenance.objects.create(
                    passenger_car=car,
                    fire_truck=None,
                    maintenance_type=mt,
                    date=date(2025, 1, 1),
                    norm=default_norm,
                )

        for car in [fire_truck_1, fire_truck_2]:
            for mt in maintenance_types:
                default_norm = {
                    'engine_oil': Decimal('300.000'),
                    'air_filter': Decimal('250.000'),
                    'cabine_filter': Decimal('350.000'),
                    'antifreeze': Decimal('600.000'),
                }[mt]

                NormsTechnicalMaintenance.objects.create(
                    passenger_car=None,
                    fire_truck=car,
                    maintenance_type=mt,
                    date=date(2025, 1, 1),
                    norm=default_norm,
                )

        self.stdout.write(self.style.SUCCESS("Нормы ТО созданы"))

        # ---------------- СТАРТОВЫЕ ПОКАЗАНИЯ ----------------
        # Стартовые одометры и остаток топлива
        OdometerFuelPassengerCar.objects.create(
            car=passenger_car_1,
            date=date(2025, 1, 1),
            odometer=100000,
            fuel=Decimal('40.000'),
            waybill=None,
        )
        OdometerFuelPassengerCar.objects.create(
            car=passenger_car_2,
            date=date(2025, 1, 1),
            odometer=70000,
            fuel=Decimal('35.000'),
            waybill=None,
        )

        OdometerFuelFireTruck.objects.create(
            car=fire_truck_1,
            date=date(2025, 1, 1),
            odometer=50000,
            fuel=Decimal('150.000'),
            waybill=None,
        )
        OdometerFuelFireTruck.objects.create(
            car=fire_truck_2,
            date=date(2025, 1, 1),
            odometer=80000,
            fuel=Decimal('180.000'),
            waybill=None,
        )

        self.stdout.write(self.style.SUCCESS("Стартовые одометр/топливо созданы"))

        # ---------------- 100 ПУТЕВЫХ ЛИСТОВ ЛЕГКОВЫЕ ----------------
        drivers = [u for u in created_users.values() if u.role == driver_role]
        passenger_cars = [passenger_car_1, passenger_car_2]

        base_date = date(2025, 2, 1)

        for i in range(100):
            car = choice(passenger_cars)
            driver = choice(drivers)
            d = base_date + timedelta(days=i % 28)

            pw = PassengerCarWaybill.objects.create(
                car=car,
                driver=driver,
                date=d,
                norm_season="winter",
            )

            # 1 запись на путевой лист (можно увеличить при необходимости)
            distance_city = randint(5, 60)
            distance_area = randint(0, 120)

            # Рассчитываем часы
            norm = NormsOperatingHoursPassengerCar.objects.filter(
                car=pw.car,
                date__lte=pw.date
            ).order_by('-date', '-id').first()
            
            if norm:
                hours_increment = (
                    Decimal(distance_city) * norm.city_norm +
                    Decimal(distance_area) * norm.area_norm
                )
            else:
                hours_increment = Decimal('0.000')
            
            # Создаём OperatingHoursCars
            operating_hours_record = OperatingHoursCars.objects.create(
                passenger_car=pw.car,
                operating_hours=hours_increment,
                date=pw.date,
            )
            
            # Создаём WaybillRecord с FK на OperatingHoursCars
            PassengerCarWaybillRecord.objects.create(
                passenger_car_waybill=pw,
                target=f"Поездка №{i + 1}",
                departure_time=time(randint(6, 10), choice([0, 15, 30, 45]), 0),
                arrival_time=time(randint(11, 18), choice([0, 15, 30, 45]), 0),
                distance_city_km=distance_city,
                distance_area_km=distance_area,
                fuel_refueled=Decimal(f"{randint(20, 40)}.000"),
                fuel_used=Decimal(f"{randint(3, 18)}.000"),
                operating_hours_record=operating_hours_record,  # FK!
            )

        self.stdout.write(self.style.SUCCESS("100 путевых листов (легковые) созданы"))

        # ---------------- 100 ПУТЕВЫХ ЛИСТОВ ПОЖАРНЫЕ ----------------
        fire_trucks = [fire_truck_1, fire_truck_2]
        fire_odometer_current = {
            fire_truck_1.id: 50000,
            fire_truck_2.id: 80000,
        }

        for i in range(100):
            car = choice(fire_trucks)
            driver = choice(drivers)
            d = base_date + timedelta(days=i % 28)

            fw = FireTruckWaybill.objects.create(
                car=car,
                driver=driver,
                date=d,
                norm_season="winter",
            )

            # имитация пробега: увеличиваем одометр
            dist = randint(1, 30)
            fire_odometer_current[car.id] += dist
            
            # Генерируем время с/без насоса
            time_with_pump = randint(0, 60)
            time_without_pump = randint(0, 20)
            
            # Рассчитываем часы для пожарной машины
            norm = NormsOperatingHoursFireTruck.objects.filter(
                car=car,
                date__lte=fw.date
            ).order_by('-date', '-id').first()
            
            if norm:
                hours_increment = (
                    Decimal(dist) * norm.km_norm +
                    Decimal(time_with_pump / 60.0) * norm.with_pump_norm +
                    Decimal(time_without_pump / 60.0)
                )
            else:
                hours_increment = Decimal('0.000')
            
            # Создаём OperatingHoursCars
            operating_hours_record = OperatingHoursCars.objects.create(
                fire_truck=car,
                operating_hours=hours_increment,
                date=fw.date,
            )

            FireTruckWaybillRecord.objects.create(
                fire_truck_waybill=fw,
                driving_route=f"Маршрут №{i + 1}",
                target=choice(["Тушение пожара", "Учения", "Дежурство", "Хозяйственный выезд"]),
                departure_time=time(randint(0, 23), choice([0, 15, 30, 45]), 0),
                arrival_time=time(randint(0, 23), choice([0, 15, 30, 45]), 0),
                odometer_after=fire_odometer_current[car.id],
                time_with_pump=time_with_pump,
                time_without_pump=time_without_pump,
                fuel_refueled=Decimal(f"{randint(0, 50)}.000"),
                fuel_used=Decimal(f"{randint(5, 25)}.000"),
                operating_hours_record=operating_hours_record,  # FK!
            )

        self.stdout.write(self.style.SUCCESS("100 путевых листов (пожарные) созданы"))

        # ---------------- ДОКУМЕНТЫ ТО (по максимуму разумно) ----------------
        # Создадим 40 документов ТО (20 для легковых, 20 для пожарных)
        for i in range(20):
            car = choice(passenger_cars)
            mt = choice(maintenance_types)
            TechnicalMaintenance.objects.create(
                date=base_date + timedelta(days=randint(0, 27)),
                car_type='passenger',
                passenger_car=car,
                fire_truck=None,
                maintenance_type=mt,
                spent=Decimal(f"{randint(1, 5)}.000"),
                received=Decimal(f"{randint(1, 6)}.000"),
                operating_hours=Decimal('0.000'),
            )

        for i in range(20):
            car = choice(fire_trucks)
            mt = choice(maintenance_types)
            TechnicalMaintenance.objects.create(
                date=base_date + timedelta(days=randint(0, 27)),
                car_type='fire_truck',
                passenger_car=None,
                fire_truck=car,
                maintenance_type=mt,
                spent=Decimal(f"{randint(1, 5)}.000"),
                received=Decimal(f"{randint(1, 6)}.000"),
                operating_hours=Decimal('0.000'),
            )

        self.stdout.write(self.style.SUCCESS("Документы ТО созданы"))
        self.stdout.write(self.style.SUCCESS("=== Полное заполнение БД завершено ==="))

    def recreate(self, model, lookup: dict, create_data: dict):
        model.all_objects.filter(**lookup).hard_delete()
        return model.objects.create(**create_data)

    def create_user_force(self, data: dict):
        query = Q(login=data["login"]) | Q(phone=data["phone"])

        if data.get("driver_license"):
            query |= Q(driver_license=data["driver_license"])

        User.all_objects.filter(query).hard_delete()

        password = data.pop("password")
        user = User.objects.create(**data)
        user.set_password(password)
        user.save()
        return user

    def reset_demo_data(self, demo_logins, passenger_numbers, fire_numbers):
        passenger_car_ids = list(
            PassengerCar.all_objects.filter(number__in=passenger_numbers).values_list('id', flat=True)
        )
        fire_truck_ids = list(
            FireTruck.all_objects.filter(number__in=fire_numbers).values_list('id', flat=True)
        )

        # Сначала удаляем всё зависимое
        PassengerCarWaybillRecord.all_objects.filter(
            passenger_car_waybill__car_id__in=passenger_car_ids
        ).hard_delete()

        FireTruckWaybillRecord.all_objects.filter(
            fire_truck_waybill__car_id__in=fire_truck_ids
        ).hard_delete()

        PassengerCarWaybill.all_objects.filter(car_id__in=passenger_car_ids).hard_delete()
        FireTruckWaybill.all_objects.filter(car_id__in=fire_truck_ids).hard_delete()

        TechnicalMaintenance.all_objects.filter(passenger_car_id__in=passenger_car_ids).hard_delete()
        TechnicalMaintenance.all_objects.filter(fire_truck_id__in=fire_truck_ids).hard_delete()

        OperatingHoursCars.all_objects.filter(passenger_car_id__in=passenger_car_ids).hard_delete()
        OperatingHoursCars.all_objects.filter(fire_truck_id__in=fire_truck_ids).hard_delete()

        OdometerFuelPassengerCar.all_objects.filter(car_id__in=passenger_car_ids).hard_delete()
        OdometerFuelFireTruck.all_objects.filter(car_id__in=fire_truck_ids).hard_delete()

        NormsPassengerCars.all_objects.filter(car_id__in=passenger_car_ids).hard_delete()
        NormsFireTruck.all_objects.filter(car_id__in=fire_truck_ids).hard_delete()

        NormsOperatingHoursPassengerCar.all_objects.filter(car_id__in=passenger_car_ids).hard_delete()
        NormsOperatingHoursFireTruck.all_objects.filter(car_id__in=fire_truck_ids).hard_delete()

        NormsTechnicalMaintenance.all_objects.filter(passenger_car_id__in=passenger_car_ids).hard_delete()
        NormsTechnicalMaintenance.all_objects.filter(fire_truck_id__in=fire_truck_ids).hard_delete()

        PassengerCar.all_objects.filter(id__in=passenger_car_ids).hard_delete()
        FireTruck.all_objects.filter(id__in=fire_truck_ids).hard_delete()

        # Пользователи в конце
        User.all_objects.filter(login__in=demo_logins).hard_delete()