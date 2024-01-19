from django.db import models


class Agreement(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.TextField()
    name = models.TextField()
    amount = models.FloatField()
    number = models.BigIntegerField(unique=True)
    currency = models.IntegerField()
    bic = models.IntegerField()
    Agreement_status_refer = models.BigIntegerField(unique=True)
    user_id_refer = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_id_refer')
    icon = models.BinaryField(blank=True, null=True)
    available = models.BooleanField(blank=True, null=True)

    def availability_status(self):
        return "Заморожена" if not self.available else "Доступна"

    def change_availability(self):
        self.available = not self.available
        self.save()
    class Meta:
        managed = False
        db_table = 'Agreement'

    def get_currency_symbol(self):
        currencyDct = {810: "₽", 840: "$", 978: "€"}
        return currencyDct.get(self.currency, '')

    def get_display_amount(self):
        if int(self.amount) == self.amount:
            return str(int(self.amount))
        else:
            return str(self.amount)


class AgreementApplication(models.Model):
    id = models.BigIntegerField(primary_key=True)
    application = models.OneToOneField('Applications', models.DO_NOTHING)
    Agreement = models.OneToOneField(Agreement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Agreement_application'


class AgreementStatus(models.Model):
    id = models.OneToOneField(Agreement, models.DO_NOTHING, db_column='id', primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'Agreement_status'


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
