from django.db import models


class Account(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.TextField()
    name = models.TextField()
    amount = models.FloatField()
    number = models.BigIntegerField(unique=True)
    currency = models.IntegerField()
    bic = models.IntegerField()
    account_status_refer = models.BigIntegerField(unique=True)
    user_id_refer = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_id_refer')
    icon = models.BinaryField(blank=True, null=True)
    available = models.BooleanField(blank=True, null=True)

    def availability_status(self):
        return "Заморожен" if not self.available else "Доступен"

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
    id = models.BigIntegerField(primary_key=True)
    application = models.OneToOneField('Applications', models.DO_NOTHING)
    account = models.OneToOneField(Account, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_application'


class AccountStatus(models.Model):
    id = models.OneToOneField(Account, models.DO_NOTHING, db_column='id', primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'account_status'


class ApplicationStatus(models.Model):
    id = models.OneToOneField('Applications', models.DO_NOTHING, db_column='id', primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'application_status'


class Applications(models.Model):
    id = models.BigIntegerField(primary_key=True)
    creation_date = models.DateField(blank=True, null=True)
    procession_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    application_status_refer = models.BigIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'applications'


class CardTerms(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
    id = models.BigIntegerField(primary_key=True)
    interest_rate = models.FloatField()
    payment_amount = models.FloatField()
    creation_date = models.DateField()
    end_date = models.DateField()
    agreement = models.BinaryField(blank=True, null=True)
    payments_number = models.IntegerField()
    purpose = models.TextField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)


    def get_payment_amount(self):
        if int(self.payment_amount) == self.payment_amount:
            return str(int(self.payment_amount))
        else:
            return str(self.payment_amount)

    class Meta:
        managed = False
        db_table = 'credit_terms'


class DepositTerms(models.Model):
    id = models.BigIntegerField(primary_key=True)
    interest_rate = models.FloatField()
    creation_date = models.DateField()
    end_date = models.DateField()
    agreement = models.BinaryField(blank=True, null=True)
    days = models.IntegerField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deposit_terms'


class SaveTerms(models.Model):
    id = models.BigIntegerField(primary_key=True)
    interest_rate = models.FloatField()
    number_ref = models.ForeignKey(Account, models.DO_NOTHING, db_column='number_ref', to_field='number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'save_terms'


class Users(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    patronymic = models.TextField(blank=True, null=True)
    role = models.TextField()
    email = models.TextField(blank=True, null=True)
    password = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'