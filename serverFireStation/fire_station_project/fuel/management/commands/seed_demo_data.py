from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date, time
from django.db.models import Q

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
            'driver_pass',
            'driver_fire',
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

        # ---------------- ПОЛЬЗОВАТЕЛИ ----------------
        users_data = [
            {
                "login": "admin",
                "password": "admin123",
                "name": "Системный",
                "surname": "Администратор",
                "last_name": "Demo",
                "phone": "+70000000001",
                "driver_license": None,
                "role": admin_role,
            },
            {
                "login": "mechanic",
                "password": "mechanic123",
                "name": "Иван",
                "surname": "Механиков",
                "last_name": "Петрович",
                "phone": "+70000000002",
                "driver_license": None,
                "role": mechanic_role,
            },
            {
                "login": "driver_pass",
                "password": "driver123",
                "name": "Петр",
                "surname": "Иванов",
                "last_name": "Сергеевич",
                "phone": "+70000000003",
                "driver_license": "001234567",
                "role": driver_role,
            },
            {
                "login": "driver_fire",
                "password": "driver123",
                "name": "Сергей",
                "surname": "Пожарный",
                "last_name": "Иванович",
                "phone": "+70000000004",
                "driver_license": "347654321",
                "role": driver_role,
            },
        ]

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

        # ---------------- ПУТЕВЫЕ ЛИСТЫ ЛЕГКОВЫЕ ----------------
        pw1 = PassengerCarWaybill.objects.create(
            car=passenger_car_1,
            driver=created_users["driver_pass"],
            date=date(2025, 2, 1),
            norm_season="winter",
        )

        pw2 = PassengerCarWaybill.objects.create(
            car=passenger_car_2,
            driver=created_users["driver_pass"],
            date=date(2025, 2, 2),
            norm_season="winter",
        )

        self.stdout.write(self.style.SUCCESS("Шапки путевых легковых созданы"))

        # ---------------- ЗАПИСИ К ЛЕГКОВЫМ ПУТЕВЫМ ----------------
        PassengerCarWaybillRecord.objects.create(
            passenger_car_waybill=pw1,
            target="Поездка в район",
            departure_time=time(8, 30, 0),
            arrival_time=time(11, 0, 0),
            distance_city_km=20,
            distance_area_km=50,
            fuel_refueled=Decimal('10.000'),
            fuel_used=Decimal('7.500'),
        )

        PassengerCarWaybillRecord.objects.create(
            passenger_car_waybill=pw2,
            target="Поездка в город",
            departure_time=time(9, 0, 0),
            arrival_time=time(10, 30, 0),
            distance_city_km=30,
            distance_area_km=0,
            fuel_refueled=Decimal('5.000'),
            fuel_used=Decimal('3.000'),
        )

        self.stdout.write(self.style.SUCCESS("Записи легковых путевых созданы"))

        # ---------------- ПУТЕВЫЕ ЛИСТЫ ПОЖАРНЫЕ ----------------
        fw1 = FireTruckWaybill.objects.create(
            car=fire_truck_1,
            driver=created_users["driver_fire"],
            date=date(2025, 2, 1),
            norm_season="winter",
        )

        fw2 = FireTruckWaybill.objects.create(
            car=fire_truck_2,
            driver=created_users["driver_fire"],
            date=date(2025, 2, 2),
            norm_season="winter",
        )

        self.stdout.write(self.style.SUCCESS("Шапки путевых ПА созданы"))

        # ---------------- ЗАПИСИ К ПОЖАРНЫМ ПУТЕВЫМ ----------------
        FireTruckWaybillRecord.objects.create(
            fire_truck_waybill=fw1,
            driving_route="ул. Ленина 15",
            target="Тушение пожара",
            departure_time=time(14, 0, 0),
            arrival_time=time(15, 30, 0),
            odometer_after=50020,
            time_with_pump=30,
            time_without_pump=10,
            fuel_refueled=Decimal('0.000'),
            fuel_used=Decimal('9.500'),
        )

        FireTruckWaybillRecord.objects.create(
            fire_truck_waybill=fw2,
            driving_route="ул. Мира 10",
            target="Учения",
            departure_time=time(10, 0, 0),
            arrival_time=time(11, 15, 0),
            odometer_after=80010,
            time_with_pump=15,
            time_without_pump=5,
            fuel_refueled=Decimal('20.000'),
            fuel_used=Decimal('6.000'),
        )

        self.stdout.write(self.style.SUCCESS("Записи пожарных путевых созданы"))

        # ---------------- ДОКУМЕНТЫ ТО ----------------
        TechnicalMaintenance.objects.create(
            date=date(2025, 2, 15),
            car_type='passenger',
            passenger_car=passenger_car_1,
            fire_truck=None,
            maintenance_type='engine_oil',
            spent=Decimal('2.000'),
            received=Decimal('2.500'),
            operating_hours=Decimal('0.000'),
        )

        TechnicalMaintenance.objects.create(
            date=date(2025, 2, 16),
            car_type='fire_truck',
            passenger_car=None,
            fire_truck=fire_truck_1,
            maintenance_type='air_filter',
            spent=Decimal('1.000'),
            received=Decimal('1.000'),
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