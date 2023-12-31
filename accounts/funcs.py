import random
from datetime import datetime, timedelta

from django.db.models import F
from bmstu_lab.models import Account, CustomUser, Applications, AccountApplication, CardTerms, CreditTerms, DepositTerms, SaveTerms
import bmstu_lab.serializers as serial
import requests

from django.db.models import Max
from django.db.models import Q

def get_application_by_user(user_id):
    try:
        application = Applications.objects.get(
            Q(status=1) & Q(user_id=user_id)
        )
        return application
    except Applications.DoesNotExist:
        return None


def generate_unique_id():
    max_id = Account.objects.aggregate(Max('id'))['id__max']
    return max_id + 1 if max_id is not None else 1


def update_number(account_id, application_id):
    accApp = AccountApplication.objects.get(account_id=account_id, application_id=application_id)

    payload = {
        "account_id": accApp.account_id,
        "application_id": accApp.application_id,
        "number": accApp.number,
        "currency": "840"
    }
    headers = {
        "Authorization": "secret-async-key"
    }

    response = requests.post("http://localhost:8080/get_number", json=payload, headers=headers)

    if response.status_code == 200:
        print("Запрос успешно отправлен")
    else:
        print(f"Ошибка при отправке запроса: {response.status_code}")

def create_new_account(card_name, currency_name, card_type,summ, user_id):
    if card_type == "credit" or card_type =="deposit":
        amount = summ
    else:
        amount = 0
    number = random.randint(10**16, 10**18 - 1)
    bic = 321321
    refer = random.randint(10000, 99999)
    rand_id = generate_unique_id()
    account_status_refer = refer
    user = CustomUser.objects.get(id=user_id)
    icon = None
    available = False

    currencies = {"₽": 643, "$": 840, "€": 978}
    accTypes = {
        "card": "Карта",
        "credit": "Кредитный счет",
        "deposit": "Вклад",
        "save": "Сберегательный счет",
    }

    account_data = {
        "id": rand_id,
        "type": accTypes[card_type],
        "name": card_name,
        "amount": amount,
        "number": number,
        "currency": currencies[currency_name],
        "bic": bic,
        "account_status_refer": account_status_refer,
        "user_id_refer": user.id,
        "icon": icon,
        "available": available,
    }

    account_serializer = serial.AccountSerializer(data=account_data)

    if account_serializer.is_valid():
        account_serializer.save()
        return account_serializer.data
    else:
        return account_serializer.errors

def generate_credit_card_number():
    card_number = "4"  # Начальная цифра для Visa
    for _ in range(15):
        card_number += str(random.randint(0, 9))
    return int(card_number)

def create_new_card(first_name, last_name, ref):
    cvv = random.randint(100, 999)
    card_number = generate_credit_card_number()
    holder_first_name = "John"
    holder_last_name = "Doe"
    maintenance_cost = 100
    exp_date = datetime.now() + timedelta(days=1000)

    card_terms = CardTerms.objects.create(
        cvv=cvv,
        number=card_number,
        holder_first_name=first_name,
        holder_last_name=last_name,
        maintenance_cost=maintenance_cost,
        exp_date=exp_date,
        number_ref=ref
    )

    return card_terms

def create_new_credit(purpose,ref):
    interest_rate = 15.0
    payment_amount = 1000
    creation_date = datetime.now()
    end_date = datetime.now() + timedelta(days=730)
    payments_number = 12
    purpose = purpose

    credit_terms = CreditTerms.objects.create(
        interest_rate=interest_rate,
        payment_amount=payment_amount,
        creation_date=creation_date,
        payments_number=payments_number,
        purpose=purpose,
        end_date=end_date,
        number_ref=ref
    )

    return credit_terms

def create_new_deposit(days,ref):
    depDays = int(days)
    interest_rate = 7.0
    creation_date = datetime.now()
    end_date = datetime.now() + timedelta(days=depDays)
    days = depDays

    deposit_terms = DepositTerms.objects.create(
        interest_rate=interest_rate,
        creation_date=creation_date,
        end_date=end_date,
        days=days,
        number_ref=ref
    )

    return deposit_terms

def create_new_save(ref):
    interest_rate = 0.1

    save_terms = SaveTerms.objects.create(
        interest_rate=interest_rate,
        number_ref=ref
    )

    return save_terms


def getApplications():
    applications = Applications.objects.get()

def getAccountsMod():
    cards = Account.objects.filter(
        cardterms__number_ref=F('number')
    )

    credits = Account.objects.filter(
        creditterms__number_ref=F('number')
    )

    deposits = Account.objects.filter(
        depositterms__number_ref=F('number')
    )

    saves = Account.objects.filter(
        saveterms__number_ref=F('number')
    )

    # cards = Account.objects.filter(
    #     cardterms__number_ref=F('number')
    # )[:10]
    #
    # credits = Account.objects.filter(
    #     creditterms__number_ref=F('number')
    # )[:10]
    #
    # deposits = Account.objects.filter(
    #     depositterms__number_ref=F('number')
    # )[:10]
    #
    # saves = Account.objects.filter(
    #     saveterms__number_ref=F('number')
    # )[:10]

    merged_data = []
    merged_data.extend(serial.AccountCardSerializer(cards, many=True).data)
    merged_data.extend(serial.AccountCreditSerializer(credits, many=True).data)
    merged_data.extend(serial.AccountDepositSerializer(deposits, many=True).data)
    merged_data.extend(serial.AccountSaveSerializer(saves, many=True).data)

    return merged_data


def getAccounts(user_id):
    cards = Account.objects.filter(
        cardterms__number_ref=F('number'),
        available=True,
        user_id_refer=user_id
    )
    credits = Account.objects.filter(
        creditterms__number_ref=F('number'),
        available=True,
        user_id_refer=user_id
    )
    deposits = Account.objects.filter(
        depositterms__number_ref=F('number'),
        available=True,
        user_id_refer=user_id
    )
    saves = Account.objects.filter(
        saveterms__number_ref=F('number'),
        available=True,
        user_id_refer=user_id
    )

    merged_data = []
    merged_data.extend(serial.AccountCardSerializer(cards, many=True).data)
    merged_data.extend(serial.AccountCreditSerializer(credits, many=True).data)
    merged_data.extend(serial.AccountDepositSerializer(deposits, many=True).data)
    merged_data.extend(serial.AccountSaveSerializer(saves, many=True).data)

    return merged_data

def typeCheck(queryset):
    serialized_data = []

    for account in queryset:
        account_type = account.type

        if account_type == "Карта":
            serializer = serial.AccountCardSerializer(account)
        elif account_type == "Кредитный счет":
            serializer = serial.AccountCreditSerializer(account)
        elif account_type == "Вклад":
            serializer = serial.AccountDepositSerializer(account)
        elif account_type == "Сберегательный счет":
            serializer = serial.AccountSaveSerializer(account)

        serialized_data.append(serializer.data)

    return serialized_data

def accsList(account_ids):
    cards = Account.objects.filter(id__in=account_ids, cardterms__number_ref=F('number'))
    credits = Account.objects.filter(id__in=account_ids, creditterms__number_ref=F('number'))
    deposits = Account.objects.filter(id__in=account_ids, depositterms__number_ref=F('number'))
    saves = Account.objects.filter(id__in=account_ids, saveterms__number_ref=F('number'))
    accs = []
    accs.extend(serial.AccountCardSerializer(cards, many=True).data)
    accs.extend(serial.AccountCreditSerializer(credits, many=True).data)
    accs.extend(serial.AccountDepositSerializer(deposits, many=True).data)
    accs.extend(serial.AccountSaveSerializer(saves, many=True).data)

    return accs