from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, PermissionsMixin, AbstractBaseUser
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model_class(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Custom fields
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=30, default='')
    is_moderator = models.BooleanField(default=False)

    # Necessary fields for django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name

    # @property
    # def name(self):
    #     return f"{self.full_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Account(models.Model):
    type = models.TextField()
    name = models.TextField()
    amount = models.FloatField()
    number = models.BigIntegerField(unique=True)
    currency = models.IntegerField()
    bic = models.IntegerField()
    account_status_refer = models.BigIntegerField(unique=True)
    user_id_refer = models.ForeignKey(CustomUser, models.DO_NOTHING, db_column='user_id_refer')
    icon = models.BinaryField(blank=True, null=True)
    available = models.BooleanField(blank=True, null=True)

    def availability_status(self):
        account_status = AccountStatus.objects.get(id=Account.objects.get(name=self.name).account_status_refer)
        frozen_status = account_status.frozen
        return "Заморожен" if not frozen_status else "Доступен"

    def availability_display(self):
        account_status = AccountStatus.objects.get(id=Account.objects.get(name=self.name).account_status_refer)
        print(account_status.frozen)
        return account_status.frozen

    class Meta:
        managed = False
        db_table = 'account'

    def get_currency_symbol(self):
        currencyDct = {810: "₽", 840: "$", 978: "€"}
        return currencyDct.get(self.currency, '')

    def get_display_amount(self):
        if int(self.amount) == self.amount:
            return str(int(self.amount))
        else:
            return str(self.amount)


class AccountApplication(models.Model):
    application = models.OneToOneField('Applications', models.DO_NOTHING)
    account = models.OneToOneField(Account, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_application'


class AccountStatus(models.Model):
    frozen = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'account_status'


class ApplicationStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    status_mod = models.BooleanField(blank=True, null=True)
    status_create = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'application_status'



class Applications(models.Model):
    id = models.BigAutoField(primary_key=True)
    creation_date = models.DateField(blank=True, null=True)
    procession_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, models.DO_NOTHING)
    application_status_refer = models.BigIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'applications'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CardTerms(models.Model):
    number = models.BigIntegerField()
    cvv = models.IntegerField()
    holder_first_name = models.TextField()
    holder_last_name = models.TextField()
    maintenance_cost = models.IntegerField(blank=True, null=True)
    exp_date = models.DateField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'card_terms'


class CreditTerms(models.Model):
    interest_rate = models.FloatField()
    payment_amount = models.FloatField()
    creation_date = models.DateField()
    end_date = models.DateField()
    agreement = models.BinaryField(blank=True, null=True)
    payments_number = models.IntegerField()
    purpose = models.TextField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credit_terms'

    def get_payment_amount(self):
        if int(self.payment_amount) == self.payment_amount:
            return str(int(self.payment_amount))
        else:
            return str(self.payment_amount)


class DepositTerms(models.Model):
    interest_rate = models.FloatField()
    creation_date = models.DateField()
    end_date = models.DateField()
    agreement = models.BinaryField(blank=True, null=True)
    days = models.IntegerField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deposit_terms'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class SaveTerms(models.Model):
    interest_rate = models.FloatField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'save_terms'


#
# class Users(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     full_name = models.TextField()
#     email = models.TextField(blank=True, null=True)
#     password = models.TextField(blank=True, null=True)
#     is_staff = models.BooleanField(blank=True, null=True)
#     is_superuser = models.BooleanField(blank=True, null=True)
#
#     objects = CustomUserManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     # Добавьте related_name, чтобы избежать конфликтов
#     groups = models.ManyToManyField(
#         'auth.Group',
#         blank=True,
#         related_name='custom_user_groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         blank=True,
#         related_name='custom_user_permissions',
#     )
#
#
#     def __str__(self):
#         return self.email
#     class Meta:
#             managed = False
#             db_table = 'users'




