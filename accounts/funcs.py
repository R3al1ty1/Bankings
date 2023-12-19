import random
from django.db.models import F
from bmstu_lab.models import Account, CustomUser
import bmstu_lab.serializers as serial

def create_account(card_name, currency_name, user_id):
    amount = 0
    number = random.randint(10**16, 10**18 - 1)
    bic = 321321
    refer = random.randint(10000, 99999)
    rand_id = random.randint(10000, 99999)
    account_status_refer = refer
    user = CustomUser.objects.get(id=user_id)
    icon = None
    available = False

    dct = {"₽": 643, "$": 840, "€": 978}

    account_data = {
        "id": rand_id,
        "type": "Карта",
        "name": card_name,
        "amount": amount,
        "number": number,
        "currency": dct[currency_name],
        "bic": bic,
        "account_status_refer": account_status_refer,
        "user_id_refer": user,
        "icon": icon,
        "available": available,
    }

    account_serializer = serial.AccountSerializer(data=account_data)

    if account_serializer.is_valid():
        account_serializer.save()
        return account_serializer.data
    else:
        print(account_serializer.errors)
        return None



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
        else:
            # Если тип счета не соответствует ожидаемым, пропустить или выбрать другой подход
            continue

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