# Generated by Django 4.2.5 on 2023-10-06 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('type', models.TextField()),
                ('name', models.TextField()),
                ('amount', models.FloatField()),
                ('number', models.BigIntegerField(unique=True)),
                ('currency', models.IntegerField()),
                ('bic', models.IntegerField()),
                ('account_status_refer', models.BigIntegerField(unique=True)),
                ('icon', models.BinaryField(blank=True, null=True)),
                ('available', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'account',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AccountApplication',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'account_application',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Applications',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('creation_date', models.DateField(blank=True, null=True)),
                ('procession_date', models.DateField(blank=True, null=True)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('application_status_refer', models.BigIntegerField(unique=True)),
            ],
            options={
                'db_table': 'applications',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CardTerms',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('number', models.BigIntegerField()),
                ('cvv', models.IntegerField()),
                ('holder_first_name', models.TextField()),
                ('holder_last_name', models.TextField()),
                ('maintenance_cost', models.IntegerField(blank=True, null=True)),
                ('exp_date', models.DateField()),
            ],
            options={
                'db_table': 'card_terms',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CreditTerms',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('interest_rate', models.FloatField()),
                ('payment_amount', models.FloatField()),
                ('creation_date', models.DateField()),
                ('end_date', models.DateField()),
                ('agreement', models.BinaryField(blank=True, null=True)),
                ('payments_number', models.IntegerField()),
                ('purpose', models.TextField()),
            ],
            options={
                'db_table': 'credit_terms',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DepositTerms',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('interest_rate', models.FloatField()),
                ('creation_date', models.DateField()),
                ('end_date', models.DateField()),
                ('agreement', models.BinaryField(blank=True, null=True)),
                ('days', models.IntegerField()),
            ],
            options={
                'db_table': 'deposit_terms',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SaveTerms',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('interest_rate', models.FloatField()),
            ],
            options={
                'db_table': 'save_terms',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('first_name', models.TextField()),
                ('last_name', models.TextField()),
                ('patronymic', models.TextField(blank=True, null=True)),
                ('role', models.TextField()),
                ('email', models.TextField(blank=True, null=True)),
                ('password', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AccountStatus',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bmstu_lab.account')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'account_status',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ApplicationStatus',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bmstu_lab.applications')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'application_status',
                'managed': False,
            },
        ),
    ]
