from django.db import models, transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password, identify_hasher
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models import Q
from datetime import date
import logging

logger = logging.getLogger(__name__)


# --- Мягкое удаление ---
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
    
    class Meta:
        db_table = 'role'


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
    view_roles = models.BooleanField(default=False)

    can_create_permissions = models.BooleanField(default=False)
    can_delete_permissisons = models.BooleanField(default=False)
    can_update_permissisons = models.BooleanField(default=False)
    view_permissisons = models.BooleanField(default=False)

    can_create_fire_trucks = models.BooleanField(default=False)
    can_delete_fire_trucks = models.BooleanField(default=False)
    can_update_fire_trucks = models.BooleanField(default=False)
    view_fire_trucks = models.BooleanField(default=False)

    can_create_fire_truck_waybills = models.BooleanField(default=False)
    can_delete_fire_truck_waybills = models.BooleanField(default=False)
    can_update_fire_truck_waybills = models.BooleanField(default=False)
    can_download_fire_truck_waybills = models.BooleanField(default=False)
    view_fire_truck_waybills = models.BooleanField(default=False)

    can_create_fire_truck_waybills_records = models.BooleanField(default=False)
    can_delete_fire_truck_waybills_records = models.BooleanField(default=False)
    can_update_fire_truck_waybills_records = models.BooleanField(default=False)
    view_fire_truck_waybills_records = models.BooleanField(default=False)

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

    can_create_passenger_cars_waybills_records = models.BooleanField(default=False)
    can_delete_passenger_cars_waybills_records = models.BooleanField(default=False)
    can_update_passenger_cars_waybills_records = models.BooleanField(default=False)
    view_passenger_cars_waybills_records = models.BooleanField(default=False)

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

    view_operating_hours = models.BooleanField(default=False)

    def __str__(self):
        return f"Права для роли {self.role.name}"
    
    class Meta:
        db_table = 'permission'


class User(SoftDeleteModel):
    name = models.CharField(max_length=40, null=False)
    surname = models.CharField(max_length=40, null=False)
    last_name = models.CharField(max_length=40, null=False)

    login = models.CharField(max_length=15, unique=True, null=False)
    password = models.CharField(max_length=300, null=False)

    phone = models.CharField(max_length=11, validators=[MinLengthValidator(11)],  unique=True, null=False)

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
    
    class Meta:
        db_table = 'user'


class Season(models.TextChoices):
    WINTER = 'winter', 'Зима'
    SUMMER = 'summer', 'Лето'

    @classmethod
    def get_display(cls, value):
        """Получить человеческое название сезона"""
        return dict(cls.choices).get(value, value)


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

    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
        null=False,
        help_text="тип топлива"
    )
    
    operating_hours = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        null=False,
        help_text="текущие моточасы (сумма всех часов из путевых листов)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )


    def __str__(self):
        return f"Легковой автомобиль {self.number}"
    
    class Meta:
        db_table = 'passenger_car'


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
    
    class Meta:
        db_table = 'norms_passenger_cars'


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

    upon_issuance = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_spent = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_received = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    required_by_norm = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    availability_upon_delivery = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    savings = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    overrun = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))

    def is_editable(self):
        """Проверяет, может ли путевой лист быть отредактирован (не более 7 дней с даты путевого листа)"""
        from django.utils import timezone
        from datetime import timedelta
        if not self.date:
            return False
        # Преобразуем date в datetime для сравнения
        date_datetime = timezone.make_aware(timezone.datetime.combine(self.date, timezone.datetime.min.time()))
        return (timezone.now() - date_datetime) <= timedelta(days=730)

    def __str__(self):
        return f"Путевой лист {self.car.number} от {self.date}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = next_doc_number(PassengerCarWaybill, length=6)
        super().save(*args, **kwargs)

    def recalc_totals(self, save=True):
        logger.warning('\n' + '=' * 80)
        logger.warning('[PassengerCarWaybill.recalc_totals] ВХОД В МЕТОД')
        logger.warning('=' * 80)
        
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

        # ════════════════════════════════════════════════════════════════
        # ЛОГИРОВАНИЕ ПЕРЕД СОХРАНЕНИЕМ В recalc_totals
        # ════════════════════════════════════════════════════════════════
        logger.warning('\n' + '=' * 80)
        logger.warning('[PassengerCarWaybill.recalc_totals] ПЕРЕД СОХРАНЕНИЕМ')
        logger.warning('=' * 80)
        logger.warning(f'upon_issuance: {self.upon_issuance} (max: 999.999)')
        logger.warning(f'total_spent: {self.total_spent} (max: 999.999)')
        logger.warning(f'total_received: {self.total_received} (max: 999.999)')
        logger.warning(f'required_by_norm: {self.required_by_norm} (max: 999.999)')
        logger.warning(f'availability_upon_delivery: {self.availability_upon_delivery} (max: 999.999)')
        logger.warning(f'savings: {self.savings} (max: 999.999)')
        logger.warning(f'overrun: {self.overrun} (max: 999.999)')
        
        # Проверяем какие превышают лимиты
        logger.warning('\n--- ПРОВЕРКА ЛИМИТОВ ---')
        errors = []
        
        if self.upon_issuance and self.upon_issuance > Decimal('999.999'):
            msg = f'❌ upon_issuance={self.upon_issuance} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        if self.total_spent and self.total_spent > Decimal('999.999'):
            msg = f'❌ total_spent={self.total_spent} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        if self.total_received and self.total_received > Decimal('999.999'):
            msg = f'❌ total_received={self.total_received} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        if self.required_by_norm and self.required_by_norm > Decimal('999.999'):
            msg = f'❌ required_by_norm={self.required_by_norm} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        if self.availability_upon_delivery and self.availability_upon_delivery > Decimal('999.999'):
            msg = f'❌ availability_upon_delivery={self.availability_upon_delivery} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        if self.savings and self.savings > Decimal('999.999'):
            msg = f'❌ savings={self.savings} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        if self.overrun and self.overrun > Decimal('999.999'):
            msg = f'❌ overrun={self.overrun} > 999.999'
            logger.error(msg)
            errors.append(msg)
        
        logger.warning('=' * 80)
        
        if errors:
            logger.error(f'\n⚠️  НАЙДЕНЫ ПЕРЕПОЛНЕНИЯ В recalc_totals:\n' + '\n'.join(errors))

        if save:
            logger.warning('[recalc_totals] ВЫЗЫВАЕМ self.save()')
            try:
                self.save(update_fields=[
                    'upon_issuance',
                    'total_spent',
                    'total_received',
                    'required_by_norm',
                    'availability_upon_delivery',
                    'savings',
                    'overrun',
                ])
                logger.warning('✅ recalc_totals УСПЕШНО СОХРАНЕНА')
            except Exception as e:
                logger.error(f'❌ ОШИБКА при save() в recalc_totals: {str(e)}')
                logger.error(f'[recalc_totals ERROR] Это ошибка из самого recalc_totals!')
                raise
    
    class Meta:
        db_table = 'passenger_car_waybill'


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
        validators=[MaxValueValidator(999999), MinValueValidator(0)]
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
    
    class Meta:
        db_table = 'odometer_fuel_passenger_car'


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
        validators=[MaxValueValidator(2000), MinValueValidator(0)]
    )

    distance_area_km = models.PositiveIntegerField(
        null=False,
        help_text="пройдено км по области",
        validators=[MaxValueValidator(2000), MinValueValidator(0)]
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
        validators=[MaxValueValidator(999999), MinValueValidator(0)]
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
        validators=[MaxValueValidator(999999), MinValueValidator(0)]
    )

    distance_total_km = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="всего пройдено км",
        validators=[MaxValueValidator(4000), MinValueValidator(0)]
    )

    fuel_used_city = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по городу, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_area = models.DecimalField(
        max_digits=7,
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
        max_digits=7,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по норме, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    
    operating_hours_record = models.ForeignKey(
        'OperatingHoursCars',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="passenger_car_waybill_records",
        help_text="записанные моточасы для этой поездки"
    )

    class Meta:
        ordering = ["id"]
        db_table = 'passenger_car_waybill_record'

    def is_editable(self):
        """Проверяет, может ли запись быть отредактирована (путевой лист не более 7 дней давности)"""
        from django.utils import timezone
        from datetime import timedelta
        wb_date = self.passenger_car_waybill.date
        if not wb_date:
            return False
        # Преобразуем date в datetime для сравнения
        date_datetime = timezone.make_aware(timezone.datetime.combine(wb_date, timezone.datetime.min.time()))
        return (timezone.now() - date_datetime) <= timedelta(days=730)

    def _fill_start_values(self):
        logger.warning('[_fill_start_values] НАЧАЛО')
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
        
        logger.warning(f'[_fill_start_values] odometer_before={self.odometer_before}')
        logger.warning(f'[_fill_start_values] fuel_before_departure={self.fuel_before_departure} (max: 999.999)')
        logger.warning('[_fill_start_values] КОНЕЦ')

    def _fill_start_values_from_prev(self, prev_record):
        """Заполнить начальные значения из предыдущей записи (для каскадного пересчета)"""
        self.odometer_before = prev_record.odometer_after
        self.fuel_before_departure = prev_record.fuel_on_return

    def _apply_norms(self):
        logger.warning('[_apply_norms] НАЧАЛО')
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
            season_display = Season.get_display(wb.norm_season)
            
            # Проверяем есть ли норма, но с датой позже даты путевого листа
            future_norm = (
                NormsPassengerCars.objects
                .filter(
                    car=car,
                    season=wb.norm_season,
                    date__gt=wb.date,
                )
                .order_by('date')
                .first()
            )
            
            if future_norm:
                raise ValidationError(
                    f"Норма для {car.number}, сезон {season_display} существует, но создана позже даты путевого листа. "
                    f"Дата норма: {future_norm.date.strftime('%d.%m.%Y')}, дата путевого листа: {wb.date.strftime('%d.%m.%Y')}. "
                    f"Укажите дату путевого листа раньше или измените дату нормы."
                )
            else:
                raise ValidationError(
                    f"Не найдена норма для {car.number}, сезон={season_display}"
                )

        self.distance_total_km = self.distance_city_km + self.distance_area_km
        self.odometer_after = self.odometer_before + self.distance_total_km

        self.fuel_used_city = Decimal(self.distance_city_km) * norm.city_norm
        self.fuel_used_area = Decimal(self.distance_area_km) * norm.area_norm
        self.fuel_used_normal = (self.fuel_used_city or 0) + (self.fuel_used_area or 0)
        
        logger.warning(f'[_apply_norms] distance_total_km={self.distance_total_km}')
        logger.warning(f'[_apply_norms] odometer_after={self.odometer_after} (max: 999999)')
        logger.warning(f'[_apply_norms] fuel_used_city={self.fuel_used_city} (max: 999.999)')
        logger.warning(f'[_apply_norms] fuel_used_area={self.fuel_used_area} (max: 999.999)')
        logger.warning(f'[_apply_norms] fuel_used_normal={self.fuel_used_normal} (max: 999.999)')
        logger.warning('[_apply_norms] КОНЕЦ')

    def _calc_fuel_on_return(self):
        logger.warning('[_calc_fuel_on_return] НАЧАЛО')
        logger.warning(f'[_calc_fuel_on_return] fuel_before_departure={self.fuel_before_departure}')
        logger.warning(f'[_calc_fuel_on_return] fuel_used={self.fuel_used}')
        logger.warning(f'[_calc_fuel_on_return] fuel_refueled={self.fuel_refueled}')
        
        self.fuel_on_return = (
            (self.fuel_before_departure or Decimal('0.000'))
            - (self.fuel_used or Decimal('0.000'))
            + (self.fuel_refueled or Decimal('0.000'))
        )
        
        logger.warning(f'[_calc_fuel_on_return] fuel_on_return={self.fuel_on_return} (max: 999.999)')
        
        # Проверка что топливо не может быть отрицательным
        if self.fuel_on_return < 0:
            raise ValidationError(
                f"Остаток топлива не может быть отрицательным! "
                f"Топливо перед: {self.fuel_before_departure} л, "
                f"израсходовано: {self.fuel_used} л, "
                f"заправлено: {self.fuel_refueled} л. "
                f"Результат: {self.fuel_on_return} л. "
                f"Пожалуйста, проверьте введенные значения."
            )
        
        logger.warning('[_calc_fuel_on_return] КОНЕЦ')

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

    def recalc_cascade(self):
        """Каскадный пересчет всех последующих записей во всех путевых листах этой машины"""
        wb = self.passenger_car_waybill
        car = wb.car
        logger.warning(f'\n\n========== КАСКАДНЫЙ ПЕРЕСЧЕТ НАЧАЛО (ЛА) ==========')
        logger.warning(f'[recalc_cascade] current record id={self.id}, date={wb.date}')
        
        # 🚗 ВАЖНО: Правильный порядок - сначала по дате путевого листа, потом по id записи
        all_future_records = (
            PassengerCarWaybillRecord.objects
            .filter(
                passenger_car_waybill__car=car,
                passenger_car_waybill__deleted_at__isnull=True
            )
            .filter(
                models.Q(passenger_car_waybill__date__gt=wb.date) |
                models.Q(passenger_car_waybill__date=wb.date, id__gt=self.id)
            )
            .select_related('passenger_car_waybill')
            .order_by('passenger_car_waybill__date', 'id')  # ← ВАЖНО: сначала дата, потом id
        )
        
        logger.warning(f'[recalc_cascade] найдено последующих записей: {all_future_records.count()}')
        
        # 🚗 ВАЖНО: Берем начальные значения ИЗ ТЕКУЩЕЙ ЗАПИСИ
        prev_odometer = self.odometer_after
        prev_fuel = self.fuel_on_return
        
        for next_record in all_future_records:
            logger.warning(f'\n[recalc_cascade] пересчитываем запись id={next_record.id}, waybill_date={next_record.passenger_car_waybill.date}')
            
            try:
                # 🚗 ВАЖНО: Не вызываем save() который снова запустит recalc_cascade
                # Вместо этого обновляем поля напрямую
                
                # Устанавливаем начальные значения из предыдущего состояния
                next_record.odometer_before = prev_odometer
                next_record.fuel_before_departure = prev_fuel
                
                # Пересчитываем нормы
                next_record._apply_norms()
                # Пересчитываем остаток топлива
                next_record._calc_fuel_on_return()
                
                # 🚗 ВАЖНО: Проверяем валидацию ДО сохранения
                if next_record.odometer_after < next_record.odometer_before:
                    raise ValidationError(
                        f"Ошибка при каскадном пересчете записи {next_record.id}: "
                        f"одометр после ({next_record.odometer_after}) < одометр до ({next_record.odometer_before})"
                    )
                
                # Сохраняем ТОЛЬКО нужные поля, НЕ вызывая recalc_cascade повторно
                PassengerCarWaybillRecord.objects.filter(pk=next_record.id).update(
                    odometer_before=next_record.odometer_before,
                    odometer_after=next_record.odometer_after,
                    distance_total_km=next_record.distance_total_km,
                    fuel_before_departure=next_record.fuel_before_departure,
                    fuel_used_city=next_record.fuel_used_city,
                    fuel_used_area=next_record.fuel_used_area,
                    fuel_on_return=next_record.fuel_on_return,
                    fuel_used_normal=next_record.fuel_used_normal,
                )
                logger.warning(f'✅ запись id={next_record.id} пересчитана успешно (без вызова save)')
                
                # Обновляем состояние для следующей итерации
                prev_odometer = next_record.odometer_after
                prev_fuel = next_record.fuel_on_return
                
                # Обновляем OdometerFuel для этого путевого листа
                OdometerFuelPassengerCar.objects.filter(
                    waybill=next_record.passenger_car_waybill
                ).delete()
                
                OdometerFuelPassengerCar.objects.create(
                    car=car,
                    odometer=next_record.odometer_after,
                    fuel=next_record.fuel_on_return,
                    date=next_record.passenger_car_waybill.date,
                    waybill=next_record.passenger_car_waybill,
                )
                logger.warning(f'✅ OdometerFuel для waybill id={next_record.passenger_car_waybill_id} обновлена')
                
                # 🚗 ВАЖНО: Пересчитываем моточасы для этой записи
                norm = NormsOperatingHoursPassengerCar.objects.filter(
                    car=car, date__lte=next_record.passenger_car_waybill.date
                ).order_by('-date', '-id').first()
                
                if norm:
                    increment = (
                        Decimal(next_record.distance_city_km) * norm.city_norm +
                        Decimal(next_record.distance_area_km) * norm.area_norm
                    )
                else:
                    increment = Decimal('0.000')
                
                # Обновляем OperatingHoursCars
                if next_record.operating_hours_record:
                    OperatingHoursCars.objects.filter(pk=next_record.operating_hours_record_id).update(
                        operating_hours=increment
                    )
                else:
                    operating_hours_record = OperatingHoursCars.objects.create(
                        passenger_car=car,
                        date=next_record.passenger_car_waybill.date,
                        operating_hours=increment,
                    )
                    PassengerCarWaybillRecord.objects.filter(pk=next_record.id).update(
                        operating_hours_record=operating_hours_record
                    )
                logger.warning(f'✅ Моточасы для записи id={next_record.id} обновлены: {increment}')
                
                # Пересчет totals в waybill
                next_record.passenger_car_waybill.recalc_totals()
                
            except Exception as e:
                logger.error(f'❌ ОШИБКА в каскадном пересчете для записи id={next_record.id}: {str(e)}')
                raise ValidationError(f'Ошибка при пересчете записи {next_record.id}: {str(e)}')
        
        # 🚗 ВАЖНО: Пересчет total hours в машине ПОСЛЕ всех обновлений
        from django.db.models import Sum
        total_hours = (
            OperatingHoursCars.objects
            .filter(passenger_car=car, fire_truck__isnull=True)
            .aggregate(total=Sum('operating_hours'))['total']
        ) or Decimal('0.000')
        
        car.operating_hours = total_hours
        car.save(update_fields=['operating_hours'])
        logger.warning(f'✅ машина {car.number}: operating_hours = {total_hours}')
        logger.warning(f'========== КАСКАДНЫЙ ПЕРЕСЧЕТ КОНЕЦ ==========\n')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Заполнять начальные значения только при СОЗДАНИИ новой записи
            # При редактировании (UPDATE) одометр и топливо уже заполнены и не должны меняться
            if self.pk is None:  # Только для новых записей
                self._fill_start_values()
            
            self._apply_norms()
            self._calc_fuel_on_return()
            
            # Валидация одометра только при СОЗДАНИИ новой записи
            # При редактировании старой записи одометр НЕ ДОЛЖЕН менять (см. serializer read_only_fields)
            if self.pk is None:  # Только для новых записей
                # Валидация: одометр не может идти назад!
                if self.odometer_after < self.odometer_before:
                    raise ValidationError(
                        f"Ошибка: одометр после поездки ({self.odometer_after}) не может быть меньше чем одометр перед поездкой ({self.odometer_before}). "
                        f"Проверьте значение км по городу и по области."
                    )
                if self.odometer_after - self.odometer_before > 2000:
                    raise ValidationError(
                        f"Ошибка: одометр не может увеличиться за раз более чем на 2000 км. "
                        f"Проверьте значение км по городу и по области."
                    )
            
            # ════════════════════════════════════════════════════════════════
            # ЛОГИРОВАНИЕ ВСЕ DECIMAL ПОЛЕЙ ПЕРЕД СОХРАНЕНИЕМ
            # ════════════════════════════════════════════════════════════════
            logger.warning('\n' + '=' * 80)
            logger.warning('[PassengerCarWaybillRecord.save] ВСЕ ПОЛЯ ПЕРЕД super().save()')
            logger.warning('=' * 80)
            logger.warning(f'distance_city_km: {self.distance_city_km} (max: 999999, тип: {type(self.distance_city_km).__name__})')
            logger.warning(f'distance_area_km: {self.distance_area_km} (max: 999999, тип: {type(self.distance_area_km).__name__})')
            logger.warning(f'fuel_refueled: {self.fuel_refueled} (max: 999.999, тип: {type(self.fuel_refueled).__name__})')
            logger.warning(f'fuel_used: {self.fuel_used} (max: 999.999, тип: {type(self.fuel_used).__name__})')
            logger.warning(f'fuel_before_departure: {self.fuel_before_departure} (max: 999.999, тип: {type(self.fuel_before_departure).__name__})')
            logger.warning(f'odometer_before: {self.odometer_before} (max: 999999, тип: {type(self.odometer_before).__name__})')
            logger.warning(f'distance_total_km: {self.distance_total_km} (max: 999999, тип: {type(self.distance_total_km).__name__})')
            logger.warning(f'fuel_used_city: {self.fuel_used_city} (max: 999.999, тип: {type(self.fuel_used_city).__name__})')
            logger.warning(f'fuel_used_area: {self.fuel_used_area} (max: 999.999, тип: {type(self.fuel_used_area).__name__})')
            logger.warning(f'fuel_on_return: {self.fuel_on_return} (max: 999.999, тип: {type(self.fuel_on_return).__name__})')
            logger.warning(f'fuel_used_normal: {self.fuel_used_normal} (max: 999.999, тип: {type(self.fuel_used_normal).__name__})')
            logger.warning(f'odometer_after: {self.odometer_after} (max: 999999, тип: {type(self.odometer_after).__name__})')
            
            # Проверяем какие превышают лимиты
            logger.warning('\n--- ПРОВЕРКА ЛИМИТОВ ---')
            errors = []
            
            if self.fuel_refueled and self.fuel_refueled > Decimal('999.999'):
                msg = f'❌ fuel_refueled={self.fuel_refueled} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.fuel_used and self.fuel_used > Decimal('999.999'):
                msg = f'❌ fuel_used={self.fuel_used} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.fuel_before_departure and self.fuel_before_departure > Decimal('999.999'):
                msg = f'❌ fuel_before_departure={self.fuel_before_departure} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.fuel_used_city and self.fuel_used_city > Decimal('999.999'):
                msg = f'❌ fuel_used_city={self.fuel_used_city} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.fuel_used_area and self.fuel_used_area > Decimal('999.999'):
                msg = f'❌ fuel_used_area={self.fuel_used_area} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.fuel_on_return and self.fuel_on_return > Decimal('999.999'):
                msg = f'❌ fuel_on_return={self.fuel_on_return} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.fuel_used_normal and self.fuel_used_normal > Decimal('999.999'):
                msg = f'❌ fuel_used_normal={self.fuel_used_normal} > 999.999'
                logger.error(msg)
                errors.append(msg)
            
            if self.odometer_after and self.odometer_after > 999999:
                msg = f'❌ odometer_after={self.odometer_after} > 999999'
                logger.error(msg)
                errors.append(msg)
            
            if self.distance_total_km and self.distance_total_km > 999999:
                msg = f'❌ distance_total_km={self.distance_total_km} > 999999'
                logger.error(msg)
                errors.append(msg)
            
            logger.warning('=' * 80)
            
            if errors:
                logger.error(f'\n⚠️  НАЙДЕНЫ ПЕРЕПОЛНЕНИЯ:\n' + '\n'.join(errors))
            
            try:
                super().save(*args, **kwargs)
                logger.warning('✅ PassengerCarWaybillRecord УСПЕШНО СОХРАНЕНА')
            except Exception as e:
                logger.error(f'❌ ОШИБКА при super().save(): {str(e)}')
                raise

            # ОТЛАДКА перед созданием OdometerFuelPassengerCar
            logger.warning('=' * 80)
            logger.warning('[PassengerCarWaybillRecord.save] ПЕРЕД СОЗДАНИЕМ OdometerFuelPassengerCar')
            logger.warning('=' * 80)
            logger.warning(f'odometer_after: {self.odometer_after} (тип: {type(self.odometer_after).__name__}, max: 999999)')
            logger.warning(f'fuel_on_return: {self.fuel_on_return} (тип: {type(self.fuel_on_return).__name__}, max: 999.999)')
            
            # Проверяем лимиты перед созданием
            if self.fuel_on_return > Decimal('999.999'):
                logger.error(f'❌ ОШИБКА: fuel_on_return={self.fuel_on_return} превышает максимум 999.999!')
            if self.odometer_after > 999999:
                logger.error(f'❌ ОШИБКА: odometer_after={self.odometer_after} превышает максимум 999999!')
            
            logger.warning('=' * 80)

            # Пробуем создать с явным логированием ошибок
            try:
                OdometerFuelPassengerCar.objects.create(
                    car=self.passenger_car_waybill.car,
                    odometer=self.odometer_after,
                    fuel=self.fuel_on_return,
                    date=self.passenger_car_waybill.date,
                    waybill=self.passenger_car_waybill,
                )
                logger.warning('✅ OdometerFuelPassengerCar создана успешно')
            except Exception as e:
                logger.error(f'❌ ОШИБКА при создании OdometerFuelPassengerCar: {str(e)}')
                logger.error(f'VALUES:')
                logger.error(f'  car: {self.passenger_car_waybill.car}')
                logger.error(f'  odometer: {self.odometer_after}')
                logger.error(f'  fuel: {self.fuel_on_return}')
                logger.error(f'  date: {self.passenger_car_waybill.date}')
                raise

            # ════════════════════════════════════════════════════════════════
            # РАСЧЁТ OPERATING HOURS (просто increment, не cumulative!)
            # ════════════════════════════════════════════════════════════════
            logger.warning('=' * 80)
            logger.warning('[PassengerCarWaybillRecord.save] РАСЧЁТ МОТОЧАСОВ')
            logger.warning('=' * 80)
            
            # Вычисляем increment (сколько часов за ЭТУ поездку)
            wb = self.passenger_car_waybill
            car = wb.car
            norm = (
                NormsOperatingHoursPassengerCar.objects
                .filter(car=car, date__lte=wb.date)
                .order_by('-date', '-id')
                .first()
            )
            
            if norm:
                increment = (
                    Decimal(self.distance_city_km) * norm.city_norm +
                    Decimal(self.distance_area_km) * norm.area_norm
                )
            else:
                increment = Decimal('0.000')
            
            logger.warning(f'increment за эту поездку = {increment}')
            
            # Создаём или обновляем OperatingHoursCars с ТОЛЬКО этим increment
            # (не cumulative - просто часы этой поездки!)
            try:
                # ВАЖНО: Используем FK самого record, а не update_or_create с (car, date),
                # чтобы избежать MultipleObjectsReturned когда много поездок в один день
                if self.operating_hours_record:
                    # Уже существует - обновляем его
                    self.operating_hours_record.operating_hours = increment
                    self.operating_hours_record.save(update_fields=['operating_hours'])
                    logger.warning(f'✅ OperatingHoursCars обновлена (id={self.operating_hours_record.id}) с hours = {increment}')
                else:
                    # Не существует - создаём новый
                    operating_hours_record = OperatingHoursCars.objects.create(
                        passenger_car=car,
                        date=wb.date,
                        operating_hours=increment,
                    )
                    logger.warning(f'✅ OperatingHoursCars создана (id={operating_hours_record.id}) с hours = {increment}')
                    
                    # Сохраняем FK на этот WaybillRecord
                    self.operating_hours_record = operating_hours_record
                    logger.warning(f'✅ FK operating_hours_record установлена на {operating_hours_record.id}')
                    
                    # ВАЖНО: Сохраняем FK в БД
                    PassengerCarWaybillRecord.objects.filter(pk=self.pk).update(
                        operating_hours_record=operating_hours_record
                    )
                    logger.warning(f'✅ FK сохранена в БД для record {self.pk}')
            except Exception as e:
                logger.error(f'❌ ОШИБКА при создании OperatingHoursCars: {str(e)}')
                raise
            
            # ════════════════════════════════════════════════════════════════
            # ПЕРЕСЧЁТ TOTAL HOURS В МАШИНЕ
            # ════════════════════════════════════════════════════════════════
            from django.db.models import Sum
            total_hours = (
                OperatingHoursCars.objects
                .filter(passenger_car=car, fire_truck__isnull=True)
                .aggregate(total=Sum('operating_hours'))['total']
            ) or Decimal('0.000')
            
            # Обновляем поле в машине
            car.operating_hours = total_hours
            car.save(update_fields=['operating_hours'])
            logger.warning(f'✅ машина {car.number}: operating_hours = {total_hours}')
            logger.warning('=' * 80)

            # Пересчёт итогов путевого листа
            self.passenger_car_waybill.recalc_totals()
            
            # 🔥 ВАЖНО: Каскадный пересчет ПОСЛЕ всех обновлений
            self.recalc_cascade()
            logger.warning('[save] ✅ Все операции завершены успешно')


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

    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
        null=False,
        help_text="тип топлива"
    )
    
    operating_hours = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        null=False,
        help_text="текущие моточасы (сумма всех часов из путевых листов)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )


    def __str__(self):
        return f"Пожарный автомобиль с гос. номером {self.number}"
    
    class Meta:
        db_table = 'fire_truck'


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
    
    class Meta:
        db_table = 'norms_fire_truck'


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

    upon_issuance = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_spent = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    total_received = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    required_by_norm = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    availability_upon_delivery = models.DecimalField(max_digits=6, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    savings = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))
    overrun = models.DecimalField(max_digits=9, decimal_places=3, null=False, editable=False, default=Decimal('0.000'))

    def is_editable(self):
        """Проверяет, может ли путевой лист быть отредактирован (не более 7 дней с даты путевого листа)"""
        from django.utils import timezone
        from datetime import timedelta
        if not self.date:
            return False
        # Преобразуем date в datetime для сравнения
        date_datetime = timezone.make_aware(timezone.datetime.combine(self.date, timezone.datetime.min.time()))
        return (timezone.now() - date_datetime) <= timedelta(days=730)

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
    
    class Meta:
        db_table = 'fire_truck_waybill'


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
        validators=[MaxValueValidator(999999), MinValueValidator(0)]
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
    
    class Meta:
        db_table = 'odometer_fuel_fire_truck'


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
        validators=[MaxValueValidator(999999), MinValueValidator(0)]
    )

    time_with_pump = models.PositiveIntegerField(
        null=False,
        help_text="время работы с насосом, мин",
        validators=[MaxValueValidator(2000), MinValueValidator(0)]
    )

    time_without_pump = models.PositiveIntegerField(
        null=False,
        help_text="время работы без насоса, мин",
        validators=[MaxValueValidator(2000), MinValueValidator(0)]
    )

    fuel_refueled = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0,
        help_text="заправка, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used = models.DecimalField(
        max_digits=7,
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
        validators=[MaxValueValidator(999999), MinValueValidator(0)]
    )

    distance_km = models.PositiveIntegerField(
        null=False,
        editable=False,
        help_text="пробег, км",
        validators=[MaxValueValidator(2000), MinValueValidator(0)]
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
        max_digits=7,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="Топливо по пробегу, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_with_pump = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="Топливо при работе с насосом, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_without_pump = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="Топливо при работе без насоса, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    fuel_used_normal = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=False,
        editable=False,
        help_text="израсходовано по норме, л",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    operating_hours_record = models.ForeignKey(
        'OperatingHoursCars',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fire_truck_waybill_records",
        help_text="записанные моточасы для этой поездки"
    )

    class Meta:
        ordering = ["id"]
        db_table = 'fire_truck_waybill_record'

    def is_editable(self):
        """Проверяет, может ли запись быть отредактирована (путевой лист не более 7 дней давности)"""
        from django.utils import timezone
        from datetime import timedelta
        wb_date = self.fire_truck_waybill.date
        if not wb_date:
            return False
        # Преобразуем date в datetime для сравнения
        date_datetime = timezone.make_aware(timezone.datetime.combine(wb_date, timezone.datetime.min.time()))
        return (timezone.now() - date_datetime) <= timedelta(days=730)

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

    def _fill_start_values_from_prev(self, prev_record):
        """Заполнить начальные значения из предыдущей записи (для каскадного пересчета)"""
        self.odometer_before = prev_record.odometer_after
        self.fuel_before_departure = prev_record.fuel_on_return

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
            season_display = Season.get_display(wb.norm_season)
            
            # Проверяем есть ли норма, но с датой позже даты путевого листа
            future_norm = (
                NormsFireTruck.objects
                .filter(
                    car=car,
                    season=wb.norm_season,
                    date__gt=wb.date,
                )
                .order_by('date')
                .first()
            )
            
            if future_norm:
                raise ValidationError(
                    f"Норма для {car.number}, сезон {season_display} существует, но создана позже даты путевого листа. "
                    f"Дата норма: {future_norm.date.strftime('%d.%m.%Y')}, дата путевого листа: {wb.date.strftime('%d.%m.%Y')}. "
                    f"Укажите дату путевого листа раньше или измените дату нормы."
                )
            else:
                raise ValidationError(
                    f"Не найдена норма для {car.number}, сезон={season_display}"
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
        
        # Проверка что топливо не может быть отрицательным
        if self.fuel_on_return < 0:
            raise ValidationError(
                f"Остаток топлива не может быть отрицательным! "
                f"Топливо перед: {self.fuel_before_departure} л, "
                f"израсходовано: {self.fuel_used} л, "
                f"заправлено: {self.fuel_refueled} л. "
                f"Результат: {self.fuel_on_return} л. "
                f"Пожалуйста, проверьте введенные значения."
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
            Decimal(self.time_with_pump / 60.0) * norm.with_pump_norm +
            Decimal(self.time_without_pump / 60.0)
        )

        last_hours = (
            OperatingHoursCars.objects
            .filter(fire_truck=car)
            .order_by('-date', '-id')
            .first()
        )

        prev_total = last_hours.operating_hours if last_hours else Decimal('0.000')
        return prev_total + increment

    def recalc_cascade(self):
        """Каскадный пересчет всех последующих записей во всех путевых листах этой машины"""
        wb = self.fire_truck_waybill
        car = wb.car
        logger.warning(f'\n\n========== КАСКАДНЫЙ ПЕРЕСЧЕТ НАЧАЛО (ПА) ==========')
        logger.warning(f'[recalc_cascade] current record id={self.id}, date={wb.date}')
        
        # 🔥 ВАЖНО: Правильный порядок - сначала по дате путевого листа, потом по id записи
        all_future_records = (
            FireTruckWaybillRecord.objects
            .filter(
                fire_truck_waybill__car=car,
                fire_truck_waybill__deleted_at__isnull=True
            )
            .filter(
                models.Q(fire_truck_waybill__date__gt=wb.date) |
                models.Q(fire_truck_waybill__date=wb.date, id__gt=self.id)
            )
            .select_related('fire_truck_waybill')
            .order_by('fire_truck_waybill__date', 'id')  # ← ВАЖНО: сначала дата, потом id
        )
        
        logger.warning(f'[recalc_cascade] найдено последующих записей: {all_future_records.count()}')
        
        # 🔥 ВАЖНО: Берем начальные значения ИЗ ТЕКУЩЕЙ ЗАПИСИ
        prev_odometer = self.odometer_after
        prev_fuel = self.fuel_on_return
        
        for next_record in all_future_records:
            logger.warning(f'\n[recalc_cascade] пересчитываем запись id={next_record.id}, waybill_date={next_record.fire_truck_waybill.date}')
            
            try:
                # 🔥 ВАЖНО: Не вызываем save() который снова запустит recalc_cascade
                # Вместо этого обновляем поля напрямую
                
                # Устанавливаем начальные значения из предыдущего состояния
                next_record.odometer_before = prev_odometer
                next_record.fuel_before_departure = prev_fuel
                
                # Пересчитываем нормы
                next_record._apply_norms()
                # Пересчитываем остаток топлива
                next_record._calc_fuel_on_return()
                
                # 🔥 ВАЖНО: Проверяем валидацию ДО сохранения
                if next_record.odometer_after < next_record.odometer_before:
                    raise ValidationError(
                        f"Ошибка при каскадном пересчете записи {next_record.id}: "
                        f"одометр после ({next_record.odometer_after}) < одометр до ({next_record.odometer_before})"
                    )
                
                # Сохраняем ТОЛЬКО нужные поля, НЕ вызывая recalc_cascade повторно
                FireTruckWaybillRecord.objects.filter(pk=next_record.id).update(
                    odometer_before=next_record.odometer_before,
                    odometer_after=next_record.odometer_after,
                    distance_km=next_record.distance_km,
                    fuel_before_departure=next_record.fuel_before_departure,
                    fuel_used_by_distance=next_record.fuel_used_by_distance,
                    fuel_used_with_pump=next_record.fuel_used_with_pump,
                    fuel_used_without_pump=next_record.fuel_used_without_pump,
                    fuel_on_return=next_record.fuel_on_return,
                    fuel_used_normal=next_record.fuel_used_normal,
                )
                logger.warning(f'✅ запись id={next_record.id} пересчитана успешно (без вызова save)')
                
                # Обновляем состояние для следующей итерации
                prev_odometer = next_record.odometer_after
                prev_fuel = next_record.fuel_on_return
                
                # Обновляем OdometerFuel для этого путевого листа
                OdometerFuelFireTruck.objects.filter(
                    waybill=next_record.fire_truck_waybill
                ).delete()
                
                OdometerFuelFireTruck.objects.create(
                    car=car,
                    odometer=next_record.odometer_after,
                    fuel=next_record.fuel_on_return,
                    date=next_record.fire_truck_waybill.date,
                    waybill=next_record.fire_truck_waybill,
                )
                logger.warning(f'✅ OdometerFuel для waybill id={next_record.fire_truck_waybill_id} обновлена')
                
                # 🔥 ВАЖНО: Пересчитываем моточасы для этой записи
                norm = NormsOperatingHoursFireTruck.objects.filter(
                    car=car, date__lte=next_record.fire_truck_waybill.date
                ).order_by('-date', '-id').first()
                
                if norm:
                    increment = (
                        Decimal(next_record.distance_km) * norm.km_norm +
                        Decimal(next_record.time_with_pump / 60.0) * norm.with_pump_norm +
                        Decimal(next_record.time_without_pump / 60.0)
                    )
                else:
                    increment = Decimal('0.000')
                
                # Обновляем OperatingHoursCars
                if next_record.operating_hours_record:
                    OperatingHoursCars.objects.filter(pk=next_record.operating_hours_record_id).update(
                        operating_hours=increment
                    )
                else:
                    operating_hours_record = OperatingHoursCars.objects.create(
                        fire_truck=car,
                        date=next_record.fire_truck_waybill.date,
                        operating_hours=increment,
                    )
                    FireTruckWaybillRecord.objects.filter(pk=next_record.id).update(
                        operating_hours_record=operating_hours_record
                    )
                logger.warning(f'✅ Моточасы для записи id={next_record.id} обновлены: {increment}')
                
                # Пересчет totals в waybill
                next_record.fire_truck_waybill.recalc_totals()
                
            except Exception as e:
                logger.error(f'❌ ОШИБКА в каскадном пересчете для записи id={next_record.id}: {str(e)}')
                raise ValidationError(f'Ошибка при пересчете записи {next_record.id}: {str(e)}')
        
        # 🔥 ВАЖНО: Пересчет total hours в машине ПОСЛЕ всех обновлений
        from django.db.models import Sum
        total_hours = (
            OperatingHoursCars.objects
            .filter(fire_truck=car, passenger_car__isnull=True)
            .aggregate(total=Sum('operating_hours'))['total']
        ) or Decimal('0.000')
        
        car.operating_hours = total_hours
        car.save(update_fields=['operating_hours'])
        logger.warning(f'✅ машина {car.number}: operating_hours = {total_hours}')
        
        logger.warning(f'✅ [recalc_cascade] ВСЕ ЗАПИСИ ПЕРЕСЧИТАНЫ\n========== КАСКАДНЫЙ ПЕРЕСЧЕТ КОНЕЦ ==========\n')
        
    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        with transaction.atomic():
            # 🔥 Определяем odometer_before
            if self.pk is not None:
                # Это редактирование существующей записи
                wb = self.fire_truck_waybill
                car = wb.car
                
                # Найти текущую запись OdometerFuel для этого waybill
                current_odometer = (
                    OdometerFuelFireTruck.objects
                    .filter(waybill=wb)
                    .first()
                )
                
                if current_odometer:
                    # Найти ПРЕДЫДУЩУЮ запись OdometerFuel (с id меньше чем у текущей)
                    prev_odometer_state = (
                        OdometerFuelFireTruck.objects
                        .filter(car=car, id__lt=current_odometer.id)
                        .order_by('-id')
                        .first()
                    )
                    
                    if prev_odometer_state:
                        self.odometer_before = prev_odometer_state.odometer
                        self.fuel_before_departure = prev_odometer_state.fuel
                        logger.warning(f'[save] РЕДАКТИРОВАНИЕ: odometer_before={self.odometer_before} взят из OdometerFuel id={prev_odometer_state.id}')
                    else:
                        raise ValidationError(
                            f"Не найдены предыдущие показания одометра/топлива для {car.number}. "
                            "Это первая запись в системе."
                        )
                else:
                    # Если нет OdometerFuel для этого waybill - берем последнюю запись для машины
                    last_odometer_state = (
                        OdometerFuelFireTruck.objects
                        .filter(car=car)
                        .order_by('-id')
                        .first()
                    )
                    
                    if last_odometer_state:
                        self.odometer_before = last_odometer_state.odometer
                        self.fuel_before_departure = last_odometer_state.fuel
                        logger.warning(f'[save] РЕДАКТИРОВАНИЕ: odometer_before={self.odometer_before} взят из последней OdometerFuel id={last_odometer_state.id}')
                    else:
                        raise ValidationError(
                            f"Не найдены показания одометра/топлива для {car.number}."
                        )
            else:
                # Это новая запись
                self._fill_start_values()
                logger.warning(f'[save] СОЗДАНИЕ: odometer_before={self.odometer_before}')
            
            self._apply_norms()
            self._calc_fuel_on_return()
            
            # 🔥 Валидация одометра ВСЕГДА
            if self.odometer_after < self.odometer_before:
                raise ValidationError(
                    f"Ошибка: одометр после поездки ({self.odometer_after}) не может быть меньше чем одометр перед поездкой ({self.odometer_before}). "
                    f"Проверьте значение одометра после возвращения (км)."
                )
            if self.odometer_after - self.odometer_before > 2000:
                raise ValidationError(
                    f"Ошибка: одометр не может увеличиться за раз более чем на 2000 км. "
                    f"Проверьте значение одометра после возвращения (км)."
                )
            
            # Логирование всех полей перед сохранением
            logger.warning(f'\n\n========== ПЕРЕД СОХРАНЕНИЕМ В БД ==========')
            logger.warning(f'odometer_before: {self.odometer_before} (type: {type(self.odometer_before).__name__})')
            logger.warning(f'odometer_after: {self.odometer_after} (type: {type(self.odometer_after).__name__})')
            logger.warning(f'distance_km: {self.distance_km} (type: {type(self.distance_km).__name__})')
            logger.warning(f'fuel_before_departure: {self.fuel_before_departure} (type: {type(self.fuel_before_departure).__name__})')
            logger.warning(f'fuel_refueled: {self.fuel_refueled} (type: {type(self.fuel_refueled).__name__})')
            logger.warning(f'fuel_used: {self.fuel_used} (type: {type(self.fuel_used).__name__})')
            logger.warning(f'fuel_used_by_distance: {self.fuel_used_by_distance} (type: {type(self.fuel_used_by_distance).__name__})')
            logger.warning(f'fuel_used_with_pump: {self.fuel_used_with_pump} (type: {type(self.fuel_used_with_pump).__name__})')
            logger.warning(f'fuel_used_without_pump: {self.fuel_used_without_pump} (type: {type(self.fuel_used_without_pump).__name__})')
            logger.warning(f'fuel_used_normal: {self.fuel_used_normal} (type: {type(self.fuel_used_normal).__name__})')
            logger.warning(f'fuel_on_return: {self.fuel_on_return} (type: {type(self.fuel_on_return).__name__})')
            logger.warning(f'time_with_pump: {self.time_with_pump} (type: {type(self.time_with_pump).__name__})')
            logger.warning(f'time_without_pump: {self.time_without_pump} (type: {type(self.time_without_pump).__name__})')
            logger.warning(f'==========================================\n')
            
            try:
                super().save(*args, **kwargs)
                logger.warning('[save] УСПЕШНО СОХРАНЕНО В БД')
            except Exception as e:
                logger.error(f'[save] ОШИБКА ПРИ СОХРАНЕНИИ: {str(e)}')
                logger.error(f'[save] Тип ошибки: {type(e).__name__}')
                raise

            # 1. Обновляем или создаем OdometerFuel
            OdometerFuelFireTruck.objects.filter(waybill=self.fire_truck_waybill).delete()
            OdometerFuelFireTruck.objects.create(
                car=self.fire_truck_waybill.car,
                odometer=self.odometer_after,
                fuel=self.fuel_on_return,
                date=self.fire_truck_waybill.date,
                waybill=self.fire_truck_waybill,
            )

            # 2. Расчет моточасов
            logger.warning('=' * 80)
            logger.warning('[FireTruckWaybillRecord.save] РАСЧЁТ МОТОЧАСОВ')
            logger.warning('=' * 80)
            
            wb = self.fire_truck_waybill
            car = wb.car
            norm = NormsOperatingHoursFireTruck.objects.filter(
                car=car, date__lte=wb.date
            ).order_by('-date', '-id').first()
            
            if norm:
                increment = (
                    Decimal(self.distance_km) * norm.km_norm +
                    Decimal(self.time_with_pump / 60.0) * norm.with_pump_norm +
                    Decimal(self.time_without_pump / 60.0)
                )
            else:
                increment = Decimal('0.000')
            
            logger.warning(f'increment за эту поездку = {increment}')
            
            try:
                if self.operating_hours_record:
                    self.operating_hours_record.operating_hours = increment
                    self.operating_hours_record.save(update_fields=['operating_hours'])
                    logger.warning(f'✅ OperatingHoursCars обновлена (id={self.operating_hours_record.id}) с hours = {increment}')
                else:
                    operating_hours_record = OperatingHoursCars.objects.create(
                        fire_truck=car,
                        date=wb.date,
                        operating_hours=increment,
                    )
                    logger.warning(f'✅ OperatingHoursCars создана (id={operating_hours_record.id}) с hours = {increment}')
                    
                    self.operating_hours_record = operating_hours_record
                    logger.warning(f'✅ FK operating_hours_record установлена на {operating_hours_record.id}')
                    
                    FireTruckWaybillRecord.objects.filter(pk=self.pk).update(
                        operating_hours_record=operating_hours_record
                    )
                    logger.warning(f'✅ FK сохранена в БД для record {self.pk}')
            except Exception as e:
                logger.error(f'❌ ОШИБКА при создании OperatingHoursCars: {str(e)}')
                raise
            
            # 3. Пересчет total hours в машине
            from django.db.models import Sum
            total_hours = (
                OperatingHoursCars.objects
                .filter(fire_truck=car, passenger_car__isnull=True)
                .aggregate(total=Sum('operating_hours'))['total']
            ) or Decimal('0.000')
            
            car.operating_hours = total_hours
            car.save(update_fields=['operating_hours'])
            logger.warning(f'✅ машина {car.number}: operating_hours = {total_hours}')
            logger.warning('=' * 80)

            # 4. Пересчет totals в waybill
            self.fire_truck_waybill.recalc_totals()
            
            # 5. Каскадный пересчет ПОСЛЕ всех обновлений
            self.recalc_cascade()
            logger.warning('[save] ✅ Все операции завершены успешно')


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
        max_digits=6,
        decimal_places=3,
        null=False,
        help_text="израсходовано",
        validators=[MinValueValidator(Decimal('0.000')), MaxValueValidator(Decimal('100.000'))]
    )

    received = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=False,
        help_text="получено",
        validators=[MinValueValidator(Decimal('0.000')), MaxValueValidator(Decimal('100.000'))]
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

        # operating_hours всегда берется из поля машины (car.operating_hours)
        # Если operating_hours не передана (и это новая запись),
        # берем из PassengerCar.operating_hours или FireTruck.operating_hours
        if not self.operating_hours:
            if self.passenger_car_id:
                self.operating_hours = self.passenger_car.operating_hours
            else:
                self.operating_hours = self.fire_truck.operating_hours

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.date} - {self.maintenance_type} - {self.car_type}"
    
    class Meta:
        db_table = 'technical_maintenance'


class NormsOperatingHoursFireTruck(SoftDeleteModel):
    car = models.ForeignKey(
        FireTruck,
        on_delete=models.CASCADE,
        related_name="norms_operating_hours",
    )

    km_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="норма по переводу в моточасы км(ч/км)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    with_pump_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        help_text="норма по переводу в моточасы с насосом(просто коэффициент)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата утверждения нормы"
    )

    def __str__(self):
        return f"Норма моточасов {self.car.number} от {self.date}"
    
    class Meta:
        db_table = 'norms_operating_hours_fire_truck'


class NormsOperatingHoursPassengerCar(SoftDeleteModel):
    car = models.ForeignKey(
        PassengerCar,
        on_delete=models.CASCADE,
        related_name="norms_operating_hours",
    )

    city_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=False,
        help_text="норма по переводу в моточасы по городу(ч/км)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    area_norm = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=False,
        help_text="норма по переводу в моточасы по области(ч/км)",
        validators=[MinValueValidator(Decimal('0.000'))]
    )

    date = models.DateField(
        default=date.today,
        null=False,
        help_text="дата утверждения нормы",
    )

    def __str__(self):
        return f"Норма моточасов {self.car.number} от {self.date}"
    
    class Meta:
        db_table = 'norms_operating_hours_passenger_car'


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
        
    class Meta:
        db_table = 'norms_technical_maintenance'


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
        
    class Meta:
        db_table = 'operating_hours_cars'