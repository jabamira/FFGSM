from django.db import models, transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password, identify_hasher
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date


# --- Мягкое удаление ---------------------------------------------------------

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class SoftDeleteAllManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteAllManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


def next_doc_number(model_cls, length=6):
    """
    Автонумерация документов вида 000001, 000002, ...
    """
    last_obj = (
        model_cls.all_objects
        .exclude(number__isnull=True)
        .exclude(number='')
        .order_by('-number')
        .first()
    )

    if not last_obj:
        return str(1).zfill(length)

    try:
        last_num = int(last_obj.number)
    except (TypeError, ValueError):
        last_num = 0

    return str(last_num + 1).zfill(length)


# --- Общие таблицы -----------------------------------------------------------

class Role(SoftDeleteModel):
    name = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        help_text="название"
    )

    def __str__(self):
        return self.name


class Permission(SoftDeleteModel):
    role = models.OneToOneField(
        Role,
        on_delete=models.CASCADE,
        null=False,
        related_name="role"
    )

    can_use_mobile_booking = models.BooleanField(default=False)

    can_create_users = models.BooleanField(default=False)
    can_delete_users = models.BooleanField(default=False)
    can_update_users = models.BooleanField(default=False)
    view_users = models.BooleanField(default=False)
    view_drivers = models.BooleanField(default=False)

    can_create_roles = models.BooleanField(default=False)
    can_delete_roles = models.BooleanField(default=False)
    can_update_roles = models.BooleanField(default=False)
    can_view_roles = models.BooleanField(default=False)

    can_create_permissions = models.BooleanField(default=False)
    can_delete_permissisons = models.BooleanField(default=False)
    can_update_permissisons = models.BooleanField(default=False)
    can_view_permissisons = models.BooleanField(default=False)

    can_create_fire_trucks = models.BooleanField(default=False)
    can_delete_fire_trucks = models.BooleanField(default=False)
    can_update_fire_trucks = models.BooleanField(default=False)
    view_fire_trucks = models.BooleanField(default=False)

    can_create_fire_truck_waybills = models.BooleanField(default=False)
    can_delete_fire_truck_waybills = models.BooleanField(default=False)
    can_update_fire_truck_waybills = models.BooleanField(default=False)
    can_download_fire_truck_waybills = models.BooleanField(default=False)
    view_fire_truck_waybills = models.BooleanField(default=False)

    can_create_fire_truck_waybills_record = models.BooleanField(default=False)
    can_delete_fire_truck_waybills_record = models.BooleanField(default=False)
    can_update_fire_truck_waybills_record = models.BooleanField(default=False)

    can_create_fire_truck_norms = models.BooleanField(default=False)
    can_delete_fire_truck_norms = models.BooleanField(default=False)
    can_update_fire_truck_norms = models.BooleanField(default=False)
    view_fire_truck_norms = models.BooleanField(default=False)

    can_download_fire_truck_reports = models.BooleanField(default=False)
    view_fire_truck_reports = models.BooleanField(default=False)

    can_create_passenger_cars = models.BooleanField(default=False)
    can_delete_passenger_cars = models.BooleanField(default=False)
    can_update_passenger_cars = models.BooleanField(default=False)
    view_passenger_cars = models.BooleanField(default=False)

    can_create_passenger_cars_waybills = models.BooleanField(default=False)
    can_delete_passenger_cars_waybills = models.BooleanField(default=False)
    can_update_passenger_cars_waybills = models.BooleanField(default=False)
    can_download_passenger_cars_waybills = models.BooleanField(default=False)
    view_passenger_cars_waybills = models.BooleanField(default=False)

    can_create_passenger_cars_waybills_record = models.BooleanField(default=False)
    can_delete_passenger_cars_waybills_record = models.BooleanField(default=False)
    can_update_passenger_cars_waybills_record = models.BooleanField(default=False)

    can_create_passenger_cars_norms = models.BooleanField(default=False)
    can_delete_passenger_cars_norms = models.BooleanField(default=False)
    can_update_passenger_cars_norms = models.BooleanField(default=False)
    view_passenger_cars_norms = models.BooleanField(default=False)

    can_download_passenger_cars_reports = models.BooleanField(default=False)
    view_passenger_cars_reports = models.BooleanField(default=False)

    can_download_drivers_reports = models.BooleanField(default=False)
    view_drivers_reports = models.BooleanField(default=False)

    can_create_technical_maintenance = models.BooleanField(default=False)
    can_delete_technical_maintenance = models.BooleanField(default=False)
    can_update_technical_maintenance = models.BooleanField(default=False)
    view_technical_maintenance = models.BooleanField(default=False)

    can_view_operating_hourse = models.BooleanField(default=False)

    def __str__(self):
        return f"Права для роли {self.role.name}"


class User(SoftDeleteModel):
    name = models.CharField(max_length=40, null=False)
    surname = models.CharField(max_length=40, null=False)
    last_name = models.CharField(max_length=40, null=False)

    login = models.CharField(max_length=15, unique=True, null=False)
    password = models.CharField(max_length=300, null=False)

    phone = models.CharField(max_length=12, unique=True, null=False)

    driver_license = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return f"{self.surname} {self.name} {self.last_name} ({self.login})"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if self.password:
            try:
                identify_hasher(self.password)
            except ValueError:
                self.password = make_password(self.password)

        super().save(*args, **kwargs)


class Season(models.TextChoices):
    WINTER = 'winter', 'Зима'
    SUMMER = 'summer', 'Лето'


class FuelType(models.TextChoices):
    PETROL95 = 'petrol95', 'Бензин (АИ-95)'
    PETROL92 = 'petrol92', 'Бензин (АИ-92)'
    DIESEL = 'diesel', 'Дизельное топливо'


# --- Легковые автомобили -----------------------------------------------------

class PassengerCar(SoftDeleteModel):
    number = models.CharField(
        max_length=9,
        null=False,
        unique=True,
        help_text="гос. номер"
    )

    brand = models.CharField(
        max_length=60,
        null=False,
        help_text="марка"
    )

    model = models.CharField(
        max_length=60,
        null=False,
        help_text="модель"
    )

    def __str__(self):
        return f"Легковой автомобиль {self.number}"


class NormsPassengerCars(SoftDeleteModel):
    car = models.ForeignKey(
        PassengerCar,
        on_delete=models.CASCADE,
        related_name="norms",
    )

    season = models.CharField(
        max_length=10,
        choices=Season.choices,
        null=False,
        help_text="сезон",
    )

    city_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=False,
        help_text="норма на 1 км по городу, л/км",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    area_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=False,
        help_text="норма на 1 км по области, л/км",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата утверждения нормы",
    )

    def __str__(self):
        return f"Норма {self.car.number} {self.season} от {self.date}"


class PassengerCarWaybill(SoftDeleteModel):
    number = models.CharField(
        max_length=6,
        null=False,
        blank=True,
        editable=False,
        help_text="номер путевого листа",
        unique=True,
    )

    car = models.ForeignKey(
        PassengerCar,
        on_delete=models.CASCADE,
        null=False,
        related_name="waybills",
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="passenger_car_driver",
        null=False,
        help_text="водитель"
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата путевого листа",
    )

    norm_season = models.CharField(
        max_length=10,
        choices=Season.choices,
        null=False,
        help_text="сезон нормы"
    )

    fuel_type = models.CharField(
        max_length=10,
        choices=FuelType.choices,
        null=False,
        help_text="тип топлива"
    )

    upon_issuance = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_spent = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_received = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    required_by_norm = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    availability_upon_delivery = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    savings = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    overrun = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))

    def __str__(self):
        return f"Путевой лист {self.car.number} от {self.date}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = next_doc_number(PassengerCarWaybill, length=6)
        super().save(*args, **kwargs)

    def recalc_totals(self, save=True):
        start_state = (
            OdometerFuelPassengerCar.objects
            .filter(car=self.car, date__lte=self.date)
            .order_by('-date', '-id')
            .first()
        )
        self.upon_issuance = start_state.fuel if start_state else Decimal('0.000')

        qs = self.records.all()

        agg = qs.aggregate(
            total_spent=Sum('fuel_used'),
            total_received=Sum('fuel_refueled'),
            required_by_norm=Sum('fuel_used_normal'),
        )

        self.total_spent = agg['total_spent'] or Decimal('0.000')
        self.total_received = agg['total_received'] or Decimal('0.000')
        self.required_by_norm = agg['required_by_norm'] or Decimal('0.000')

        last_record = qs.order_by('-id').first()
        self.availability_upon_delivery = (
            last_record.fuel_on_return if last_record else self.upon_issuance
        )

        diff = self.required_by_norm - self.total_spent
        if diff >= 0:
            self.savings = diff
            self.overrun = Decimal('0.000')
        else:
            self.savings = Decimal('0.000')
            self.overrun = -diff

        if save:
            self.save(update_fields=[
                'upon_issuance',
                'total_spent',
                'total_received',
                'required_by_norm',
                'availability_upon_delivery',
                'savings',
                'overrun',
            ])


class OdometerFuelPassengerCar(SoftDeleteModel):
    car = models.ForeignKey(
        PassengerCar,
        on_delete=models.CASCADE,
        related_name="odometer_fuel_records",
        null=False,
        blank=True,
        help_text="автомобиль",
    )

    odometer = models.PositiveIntegerField(
        null=False,
        blank=True,
        help_text="показания одометра, км",
        validators=[MaxValueValidator(999999)]
    )

    fuel = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        blank=True,
        help_text="остаток топлива, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата состояния",
    )

    waybill = models.ForeignKey(
        PassengerCarWaybill,
        on_delete=models.CASCADE,
        related_name="odometer_fuel_states",
        null=True,
        blank=True,
        help_text="путевой лист (если указан, данные подтянутся автоматически)",
    )

    def clean(self):
        super().clean()

        if self.waybill_id:
            if self.car_id is None:
                self.car = self.waybill.car

            last_rec = (
                self.waybill.records
                .order_by('-id')
                .first()
            )

            if last_rec is None and (self.odometer is None or self.fuel is None):
                raise ValidationError(
                    "У путевого листа нет записей. "
                    "Укажите одометр и остаток топлива вручную, либо создайте записи."
                )

            if self.odometer is None and last_rec is not None:
                self.odometer = last_rec.odometer_after

            if self.fuel is None and last_rec is not None:
                self.fuel = last_rec.fuel_on_return

            if self.date is None:
                self.date = self.waybill.date

        else:
            errors = {}
            if self.car_id is None:
                errors['car'] = "Обязательно, если не указан путевой лист"
            if self.odometer is None:
                errors['odometer'] = "Обязательно, если не указан путевой лист"
            if self.fuel is None:
                errors['fuel'] = "Обязательно, если не указан путевой лист"

            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.car.number} {self.date}: {self.odometer} км, {self.fuel} л"


class PassengerCarWaybillRecord(SoftDeleteModel):
    passenger_car_waybill = models.ForeignKey(
        PassengerCarWaybill,
        on_delete=models.CASCADE,
        null=False,
        related_name="records",
        help_text="Путевой лист легкового автомобиля",
    )

    target = models.CharField(
        max_length=255,
        null=False,
        help_text="цель выезда"
    )

    departure_time = models.TimeField(
        null=False,
        help_text="время убытия"
    )

    arrival_time = models.TimeField(
        null=False,
        help_text="время прибытия"
    )

    distance_city_km = models.PositiveIntegerField(
        null=False,
        help_text="пройдено км по городу",
        validators=[MaxValueValidator(999999)]
    )

    distance_area_km = models.PositiveIntegerField(
        null=False,
        help_text="пройдено км по области",
        validators=[MaxValueValidator(999999)]
    )

    fuel_refueled = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0,
        help_text="заправка, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        help_text="израсходовано топлива, л (фактически)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    odometer_after = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="одометр после возвращения, км",
        validators=[MaxValueValidator(999999)]
    )

    fuel_before_departure = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="топливо перед выездом, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    odometer_before = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="одометр перед выездом, км",
        validators=[MaxValueValidator(999999)]
    )

    distance_total_km = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="всего пройдено км",
        validators=[MaxValueValidator(999999)]
    )

    fuel_used_city = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по городу, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_area = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по области, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_on_return = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="остаток топлива при возвращении, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_normal = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по норме, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    class Meta:
        ordering = ["id"]

    def _fill_start_values(self):
        wb = self.passenger_car_waybill
        car = wb.car

        last_state = (
            OdometerFuelPassengerCar.objects
            .filter(car=car)
            .order_by('-date', '-id')
            .first()
        )
        if not last_state:
            raise ValidationError(
                f"Не найдены последние показания одометра/топлива для {car.number}. "
                "Сначала создайте запись в OdometerFuelPassengerCar."
            )

        self.odometer_before = last_state.odometer
        self.fuel_before_departure = last_state.fuel

    def _apply_norms(self):
        wb = self.passenger_car_waybill
        car = wb.car

        norm = (
            NormsPassengerCars.objects
            .filter(
                car=car,
                season=wb.norm_season,
                date__lte=wb.date,
            )
            .order_by('-date', '-id')
            .first()
        )
        if not norm:
            raise ValidationError(
                f"Не найдена норма для {car.number}, сезон={wb.norm_season}"
            )

        self.distance_total_km = self.distance_city_km + self.distance_area_km
        self.odometer_after = self.odometer_before + self.distance_total_km

        self.fuel_used_city = Decimal(self.distance_city_km) * norm.city_norm
        self.fuel_used_area = Decimal(self.distance_area_km) * norm.area_norm
        self.fuel_used_normal = (self.fuel_used_city or 0) + (self.fuel_used_area or 0)

    def _calc_fuel_on_return(self):
        self.fuel_on_return = (
            (self.fuel_before_departure or Decimal('0.000'))
            - (self.fuel_used or Decimal('0.000'))
            + (self.fuel_refueled or Decimal('0.000'))
        )

    def _calc_operating_hours_total(self):
        wb = self.passenger_car_waybill
        car = wb.car

        norm = (
            NormsOperatingHoursPassengerCar.objects
            .filter(car=car, date__lte=wb.date)
            .order_by('-date', '-id')
            .first()
        )
        if not norm:
            raise ValidationError(
                f"Не найдена норма перевода в моточасы для {car.number}"
            )

        increment = (
            Decimal(self.distance_city_km) * norm.city_norm +
            Decimal(self.distance_area_km) * norm.area_norm
        )

        last_hours = (
            OperatingHoursCars.objects
            .filter(passenger_car=car)
            .order_by('-date', '-id')
            .first()
        )

        prev_total = last_hours.operating_hours if last_hours else Decimal('0.000')
        return prev_total + increment

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self._fill_start_values()
            self._apply_norms()
            self._calc_fuel_on_return()
            super().save(*args, **kwargs)

            OdometerFuelPassengerCar.objects.create(
                car=self.passenger_car_waybill.car,
                odometer=self.odometer_after,
                fuel=self.fuel_on_return,
                date=self.passenger_car_waybill.date,
                waybill=self.passenger_car_waybill,
            )

            total_hours = self._calc_operating_hours_total()

            OperatingHoursCars.objects.create(
                passenger_car=self.passenger_car_waybill.car,
                operating_hours=total_hours,
                date=self.passenger_car_waybill.date,
            )

            self.passenger_car_waybill.recalc_totals()


# --- Пожарные автомобили -----------------------------------------------------

class FireTruck(SoftDeleteModel):
    number = models.CharField(
        max_length=9,
        null=False,
        unique=True,
        help_text="гос. номер"
    )

    brand = models.CharField(
        max_length=60,
        null=False,
        help_text="марка"
    )

    model = models.CharField(
        max_length=60,
        null=False,
        help_text="модель"
    )

    type = models.CharField(
        max_length=60,
        null=False,
        help_text="тип"
    )

    def __str__(self):
        return f"Пожарный автомобиль с гос. номером {self.number}"


class NormsFireTruck(SoftDeleteModel):
    car = models.ForeignKey(
        FireTruck,
        on_delete=models.CASCADE,
        related_name="norms",
    )

    season = models.CharField(
        max_length=10,
        choices=Season.choices,
        null=False,
        help_text="сезон"
    )

    with_pump_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="норма с насосом, л/мин (или др.ед.)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    without_pump_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="норма без насоса, л/мин (или др.ед.)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    km_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="норма по пробегу, л/км",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата утверждения нормы"
    )

    def __str__(self):
        return f"Норма {self.car.number} {self.season} от {self.date}"


class FireTruckWaybill(SoftDeleteModel):
    number = models.CharField(
        max_length=6,
        null=False,
        blank=True,
        editable=False,
        help_text="номер путевого листа",
        unique=True,
    )

    car = models.ForeignKey(
        FireTruck,
        null=False,
        on_delete=models.CASCADE,
        related_name="waybills",
    )

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fire_truck_driver",
        null=False,
        help_text="водитель"
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата путевого листа",
    )

    norm_season = models.CharField(
        max_length=10,
        choices=Season.choices,
        null=False,
        help_text="сезон нормы"
    )

    fuel_type = models.CharField(
        max_length=10,
        choices=FuelType.choices,
        null=False,
        help_text="тип топлива"
    )

    upon_issuance = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_spent = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_received = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    required_by_norm = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    availability_upon_delivery = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    savings = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    overrun = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))

    def __str__(self):
        return f"Путевой лист ПА {self.car.number} от {self.date}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = next_doc_number(FireTruckWaybill, length=6)
        super().save(*args, **kwargs)

    def recalc_totals(self, save=True):
        start_state = (
            OdometerFuelFireTruck.objects
            .filter(car=self.car, date__lte=self.date)
            .order_by('-date', '-id')
            .first()
        )
        self.upon_issuance = start_state.fuel if start_state else Decimal('0.000')

        qs = self.records.all()
        agg = qs.aggregate(
            total_spent=Sum('fuel_used'),
            total_received=Sum('fuel_refueled'),
            required_by_norm=Sum('fuel_used_normal'),
        )

        self.total_spent = agg['total_spent'] or Decimal('0.000')
        self.total_received = agg['total_received'] or Decimal('0.000')
        self.required_by_norm = agg['required_by_norm'] or Decimal('0.000')

        last_record = qs.order_by('-id').first()
        self.availability_upon_delivery = (
            last_record.fuel_on_return if last_record else self.upon_issuance
        )

        diff = self.required_by_norm - self.total_spent
        if diff >= 0:
            self.savings = diff
            self.overrun = Decimal('0.000')
        else:
            self.savings = Decimal('0.000')
            self.overrun = -diff

        if save:
            self.save(update_fields=[
                'upon_issuance', 'total_spent', 'total_received',
                'required_by_norm', 'availability_upon_delivery',
                'savings', 'overrun'
            ])


class OdometerFuelFireTruck(SoftDeleteModel):
    car = models.ForeignKey(
        FireTruck,
        on_delete=models.CASCADE,
        related_name="odometer_fuel_records",
        null=False,
        blank=True,
    )
    odometer = models.PositiveIntegerField(
        null=False,
        blank=True,
        validators=[MaxValueValidator(999999)]
    )
    fuel = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        blank=True,
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    date = models.DateField(
        default=date.today,
        null=False,
    )
    waybill = models.ForeignKey(
        FireTruckWaybill,
        on_delete=models.CASCADE,
        related_name="odometer_fuel_states",
        null=True,
        blank=True,
    )

    def clean(self):
        super().clean()

        if self.waybill_id:
            if self.car_id is None:
                self.car = self.waybill.car

            last_rec = (
                self.waybill.records
                .order_by('-id')
                .first()
            )

            if last_rec is None and (self.odometer is None or self.fuel is None):
                raise ValidationError(
                    "У путевого листа ПА нет записей. "
                    "Укажите одометр и топливо вручную, либо создайте записи."
                )

            if self.odometer is None and last_rec is not None:
                self.odometer = last_rec.odometer_after

            if self.fuel is None and last_rec is not None:
                self.fuel = last_rec.fuel_on_return

            if self.date is None:
                self.date = self.waybill.date
        else:
            errors = {}
            if self.car_id is None:
                errors['car'] = "Обязательно, если не указан путевой лист"
            if self.odometer is None:
                errors['odometer'] = "Обязательно, если не указан путевой лист"
            if self.fuel is None:
                errors['fuel'] = "Обязательно, если не указан путевой лист"

            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.car.number} {self.date}: {self.odometer} км, {self.fuel} л"


class FireTruckWaybillRecord(SoftDeleteModel):
    fire_truck_waybill = models.ForeignKey(
        FireTruckWaybill,
        on_delete=models.CASCADE,
        null=False,
        related_name="records",
        help_text="Эксплуатационная карточка",
    )

    driving_route = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Маршрут движения"
    )

    target = models.CharField(
        max_length=255,
        null=False,
        help_text="цель выезда"
    )

    departure_time = models.TimeField(
        null=False,
        help_text="время убытия"
    )

    arrival_time = models.TimeField(
        null=False,
        help_text="время прибытия"
    )

    odometer_after = models.PositiveIntegerField(
        null=False,
        help_text="одометр после возвращения, км",
        validators=[MaxValueValidator(999999)]
    )

    time_with_pump = models.PositiveIntegerField(
        null=False,
        help_text="время работы с насосом, мин",
        validators=[MaxValueValidator(999999)]
    )

    time_without_pump = models.PositiveIntegerField(
        null=False,
        help_text="время работы без насоса, мин",
        validators=[MaxValueValidator(999999)]
    )

    fuel_refueled = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0,
        help_text="заправка, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        help_text="фактически израсходовано, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_before_departure = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="топливо перед выездом, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    odometer_before = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="одометр перед выездом, км",
        validators=[MaxValueValidator(999999)]
    )

    distance_km = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="пробег, км",
        validators=[MaxValueValidator(999999)]
    )

    fuel_on_return = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="остаток топлива при возвращении, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_by_distance = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="Топливо по пробегу, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_with_pump = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="Топливо при работе с насосом, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_without_pump = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="Топливо при работе без насоса, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_normal = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по норме, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    class Meta:
        ordering = ["id"]

    def _fill_start_values(self):
        wb = self.fire_truck_waybill
        car = wb.car

        last_state = (
            OdometerFuelFireTruck.objects
            .filter(car=car)
            .order_by('-date', '-id')
            .first()
        )
        if not last_state:
            raise ValidationError(
                f"Не найдены последние показания для ПА {car.number}. "
                "Сначала создайте запись в OdometerFuelFireTruck."
            )

        self.odometer_before = last_state.odometer
        self.fuel_before_departure = last_state.fuel

    def _apply_norms(self):
        wb = self.fire_truck_waybill
        car = wb.car

        norm = (
            NormsFireTruck.objects
            .filter(car=car, season=wb.norm_season, date__lte=wb.date)
            .order_by('-date', '-id')
            .first()
        )
        if not norm:
            raise ValidationError(
                f"Не найдена норма для ПА {car.number}, сезон={wb.norm_season}"
            )

        self.distance_km = self.odometer_after - self.odometer_before

        self.fuel_used_by_distance = Decimal(self.distance_km) * norm.km_norm
        self.fuel_used_with_pump = Decimal(self.time_with_pump) * norm.with_pump_norm
        self.fuel_used_without_pump = Decimal(self.time_without_pump) * norm.without_pump_norm

        self.fuel_used_normal = (
            (self.fuel_used_by_distance or 0) +
            (self.fuel_used_with_pump or 0) +
            (self.fuel_used_without_pump or 0)
        )

    def _calc_fuel_on_return(self):
        self.fuel_on_return = (
            (self.fuel_before_departure or Decimal('0.000'))
            - (self.fuel_used or Decimal('0.000'))
            + (self.fuel_refueled or Decimal('0.000'))
        )

    def _calc_operating_hours_total(self):
        wb = self.fire_truck_waybill
        car = wb.car

        norm = (
            NormsOperatingHoursFireTruck.objects
            .filter(car=car, date__lte=wb.date)
            .order_by('-date', '-id')
            .first()
        )
        if not norm:
            raise ValidationError(
                f"Не найдена норма перевода в моточасы для ПА {car.number}"
            )

        increment = (
            Decimal(self.distance_km) * norm.km_norm +
            Decimal(self.time_with_pump) * norm.with_pump_norm +
            Decimal(self.time_without_pump) * norm.without_pump_norm
        )

        last_hours = (
            OperatingHoursCars.objects
            .filter(fire_truck=car)
            .order_by('-date', '-id')
            .first()
        )

        prev_total = last_hours.operating_hours if last_hours else Decimal('0.000')
        return prev_total + increment

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self._fill_start_values()
            self._apply_norms()
            self._calc_fuel_on_return()
            super().save(*args, **kwargs)

            OdometerFuelFireTruck.objects.create(
                car=self.fire_truck_waybill.car,
                odometer=self.odometer_after,
                fuel=self.fuel_on_return,
                date=self.fire_truck_waybill.date,
                waybill=self.fire_truck_waybill,
            )

            total_hours = self._calc_operating_hours_total()

            OperatingHoursCars.objects.create(
                fire_truck=self.fire_truck_waybill.car,
                operating_hours=total_hours,
                date=self.fire_truck_waybill.date,
            )

            self.fire_truck_waybill.recalc_totals()


# --- Моточасы и ТО -----------------------------------------------------------

class MaintenanceType(models.TextChoices):
    ENGINE_OIL = 'engine_oil', 'Замена моторного масла и фильтра'
    AIR_FILTER = 'air_filter', 'Замена воздушного фильтра'
    CABINE_FILTER = 'cabine_filter', 'Замена салонного фильтра'
    ANTIFREEZE = 'antifreeze', 'Замена антифриза'


class TechnicalMaintenance(SoftDeleteModel):
    number = models.CharField(
        max_length=6,
        null=False,
        blank=True,
        editable=False,
        help_text="номер документа о техническом обслуживании",
        unique=True,
    )

    date = models.DateField(
        null=False,
        help_text="дата"
    )

    TYPE_CHOICES = (
        ('passenger', 'Легковой'),
        ('fire_truck', 'Пожарный'),
    )

    car_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    passenger_car = models.ForeignKey(PassengerCar, null=True, blank=True, on_delete=models.CASCADE)
    fire_truck = models.ForeignKey(FireTruck, null=True, blank=True, on_delete=models.CASCADE)

    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.choices,
        null=False,
        help_text="вид ТО"
    )

    spent = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        null=False,
        help_text="израсходовано"
    )

    received = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        null=False,
        help_text="получено"
    )

    operating_hours = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=False,
        help_text="моточасы на момент ТО",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    def clean(self):
        super().clean()

        if not self.passenger_car and not self.fire_truck:
            raise ValidationError("Нужно указать либо легковой, либо пожарный автомобиль.")
        if self.passenger_car and self.fire_truck:
            raise ValidationError("Нельзя указывать оба типа автомобиля одновременно.")

        if self.car_type == 'passenger' and self.fire_truck:
            raise ValidationError("Для легкового автомобиля нельзя заполнять поле fire_truck.")
        if self.car_type == 'fire_truck' and self.passenger_car:
            raise ValidationError("Для пожарного автомобиля нельзя заполнять passenger_car.")

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = next_doc_number(TechnicalMaintenance, length=6)

        if self.passenger_car_id:
            last_hours = (
                OperatingHoursCars.objects
                .filter(passenger_car=self.passenger_car)
                .order_by('-date', '-id')
                .first()
            )
        else:
            last_hours = (
                OperatingHoursCars.objects
                .filter(fire_truck=self.fire_truck)
                .order_by('-date', '-id')
                .first()
            )

        self.operating_hours = last_hours.operating_hours if last_hours else Decimal('0.000')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.date} - {self.maintenance_type} - {self.car_type}"


class NormsOperatingHoursFireTruck(SoftDeleteModel):
    car = models.ForeignKey(
        FireTruck,
        on_delete=models.CASCADE,
        related_name="norms_operating_hours",
    )

    km_norm = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="норма по переводу в моточасы км",
        validators=[MinValueValidator(Decimal('0.0000'))]
    )

    with_pump_norm = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="норма по переводу в моточасы с насосом",
        validators=[MinValueValidator(Decimal('0.0000'))]
    )

    without_pump_norm = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="норма по переводу в моточасы без насоса",
        validators=[MinValueValidator(Decimal('0.0000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата утверждения нормы"
    )

    def __str__(self):
        return f"Норма моточасов {self.car.number} от {self.date}"


class NormsOperatingHoursPassengerCar(SoftDeleteModel):
    car = models.ForeignKey(
        PassengerCar,
        on_delete=models.CASCADE,
        related_name="norms_operating_hours",
    )

    city_norm = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=False,
        help_text="норма по переводу в моточасы по городу",
        validators=[MinValueValidator(Decimal('0.0000'))]
    )

    area_norm = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=False,
        help_text="норма по переводу в моточасы по области",
        validators=[MinValueValidator(Decimal('0.0000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата утверждения нормы",
    )

    def __str__(self):
        return f"Норма моточасов {self.car.number} от {self.date}"


class NormsTechnicalMaintenance(SoftDeleteModel):
    passenger_car = models.ForeignKey(PassengerCar, null=True, blank=True, on_delete=models.CASCADE)
    fire_truck = models.ForeignKey(FireTruck, null=True, blank=True, on_delete=models.CASCADE)

    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.choices,
        null=False,
        help_text="вид ТО"
    )

    norm = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        null=False,
        help_text="норма",
        validators=[MinValueValidator(Decimal('0.0000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата"
    )

    def clean(self):
        super().clean()

        if not self.passenger_car and not self.fire_truck:
            raise ValidationError("Нужно указать либо легковой, либо пожарный автомобиль.")
        if self.passenger_car and self.fire_truck:
            raise ValidationError("Нельзя указывать оба типа автомобиля одновременно.")


class OperatingHoursCars(SoftDeleteModel):
    passenger_car = models.ForeignKey(PassengerCar, null=True, blank=True, on_delete=models.CASCADE)
    fire_truck = models.ForeignKey(FireTruck, null=True, blank=True, on_delete=models.CASCADE)

    operating_hours = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=False,
        help_text="моточасы",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата"
    )

    def clean(self):
        super().clean()

        if not self.passenger_car and not self.fire_truck:
            raise ValidationError("Нужно указать либо легковой, либо пожарный автомобиль.")
        if self.passenger_car and self.fire_truck:
            raise ValidationError("Нельзя указывать оба типа автомобиля одновременно.")