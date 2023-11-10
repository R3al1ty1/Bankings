import json

from django.db.models import Q, F, Subquery, OuterRef, IntegerField, Exists
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from datetime import date
from django.shortcuts import redirect, render
from psycopg2 import Error
from operator import itemgetter

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from bmstu.db_query import get_account_by_name, connection, change_avaialability
from bmstu_lab.models import Account, AccountStatus, ApplicationStatus, Applications, Users, SaveTerms, CardTerms, \
    CreditTerms, DepositTerms, AccountApplication
import bmstu_lab.serializers as serial

@api_view(['GET'])
def get_accounts(request, format=None):
    cards = Account.objects.filter(cardterms__number_ref=F('number'))
    credits = Account.objects.filter(creditterms__number_ref=F('number'))
    deposits = Account.objects.filter(depositterms__number_ref=F('number'))
    saves = Account.objects.filter(saveterms__number_ref=F('number'))

    merged_data = []
    merged_data.extend(serial.AccountCardSerializer(cards, many=True).data)
    merged_data.extend(serial.AccountCreditSerializer(credits, many=True).data)
    merged_data.extend(serial.AccountDepositSerializer(deposits, many=True).data)
    merged_data.extend(serial.AccountSaveSerializer(saves, many=True).data)

    return Response(merged_data)

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


@api_view(["GET"])
def get_accounts_search(request):
    query = itemgetter('query')(request.GET)
    flag = True
    query = query.capitalize()
    if query == "":
        cards = Account.objects.filter(cardterms__number_ref=F('number'))
        credits = Account.objects.filter(creditterms__number_ref=F('number'))
        deposits = Account.objects.filter(depositterms__number_ref=F('number'))
        saves = Account.objects.filter(saveterms__number_ref=F('number'))

        merged_data = []
        merged_data.extend(serial.AccountCardSerializer(cards, many=True).data)
        merged_data.extend(serial.AccountCreditSerializer(credits, many=True).data)
        merged_data.extend(serial.AccountDepositSerializer(deposits, many=True).data)
        merged_data.extend(serial.AccountSaveSerializer(saves, many=True).data)

        return Response(merged_data)
    else:
        if not Account.objects.filter(name__icontains=query).exists():
            flag = False
            #return Response(f"Такого счета нет!")
        if not Account.objects.filter(type__icontains=query).exists() and flag == False:
            return Response(f"Такого счета нет!")
        if not flag:
            resp = Account.objects.filter(type__icontains=query)
        if flag:
            resp = Account.objects.filter(name__icontains=query)
        serializer = typeCheck(resp)
        return Response(serializer)

@api_view(['POST'])
def post_card(request, format=None):
    serializer = serial.AccountCardSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def post_credit(request, format=None):
    serializer = serial.AccountCreditSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def post_deposit(request, format=None):
    serializer = serial.AccountDepositSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def post_save(request, format=None):
    serializer = serial.AccountSaveSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_account(request, id, format=None):
    account = get_object_or_404(Account, id=id)
    if account.type == "Карта":
        serialized_data = serial.AccountCardSerializer(account).data
    elif account.type == "Кредитный счет":
        serialized_data = serial.AccountCreditSerializer(account).data
    elif account.type == "Вклад":
        serialized_data = serial.AccountDepositSerializer(account).data
    elif account.type == "Сберегательный счет":
        serialized_data = serial.AccountSaveSerializer(account).data
    return Response(serialized_data)

@api_view(['PUT'])
def put_detail(request, id, format=None):
    account = get_object_or_404(Account, id=id)
    if account.type == "Карта":
        serializer = serial.AccountCardSerializer(account, data=request.data, partial=True)
    elif account.type == "Кредитный счет":
        serializer = serial.AccountCreditSerializer(account, data=request.data, partial=True)
    elif account.type == "Вклад":
        serializer = serial.AccountDepositSerializer(account, data=request.data, partial=True)
    elif account.type == "Сберегательный счет":
        serializer = serial.AccountSaveSerializer(account, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def delete_detail(request, id, format=None):
    account = get_object_or_404(Account, id=id)
    account.available = False
    account.save()
    serializer = serial.AccountSerializer(account)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_detail_forever(request, id, format=None):
    account = get_object_or_404(Account, id=id)
    stat = get_object_or_404(AccountStatus, id=account.account_status_refer)
    stat.delete()
    account.delete()
    app_acc = AccountApplication.objects.filter(AccountApplication, account_id=account.id)
    app_acc.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def add_account_to_application(request):
    user = get_object_or_404(Users, id=1)
    data = json.loads(request.body)
    accId = data.get('id')
    if accId is None:
        return JsonResponse({'error': 'Missing required fields in JSON data'}, status=400)
    try:
        falseStatus = ApplicationStatus.objects.get(status_create=False)
        appId = falseStatus.id
        apps = Applications.objects.filter(application_status_refer=appId)
        first_app = apps.first()
        app_id = first_app.id
    except:
        app_id = -1
    if app_id != -1:
        appAccs = AccountApplication(application_id=app_id, account_id=accId)
        appAccs.save()
    else:
        latest = Applications.objects.last()
        applic = Applications(id=latest.id+1,user_id=1, application_status_refer=latest.id + 1)
        applic.save()
        appAccs = AccountApplication(application_id=latest.id+1, account_id=accId)
        appAccs.save()
        applicStat = ApplicationStatus(id=latest.id+1,status_create=False)
        applicStat.save()

    return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_applications(request, format=None):
    applications = Applications.objects.all()
    serialized_applications = serial.ApplicationsSerializer(applications, many=True).data

    for application in serialized_applications:
        account_applications = AccountApplication.objects.filter(application_id=application['id'])
        vals = account_applications.values()
        account_ids = [item['account_id'] for item in vals]
        if len(account_ids) > 0:
            cards = Account.objects.filter(id__in=account_ids, cardterms__number_ref=F('number'))
            credits = Account.objects.filter(id__in=account_ids, creditterms__number_ref=F('number'))
            deposits = Account.objects.filter(id__in=account_ids, depositterms__number_ref=F('number'))
            saves = Account.objects.filter(id__in=account_ids, saveterms__number_ref=F('number'))
            accs = []
            accs.extend(serial.AccountCardSerializer(cards, many=True).data)
            accs.extend(serial.AccountCreditSerializer(credits, many=True).data)
            accs.extend(serial.AccountDepositSerializer(deposits, many=True).data)
            accs.extend(serial.AccountSaveSerializer(saves, many=True).data)

        else:
            accs = []
        application['accounts'] = accs


    return Response(serialized_applications)


@api_view(['GET'])
def get_application(request, pk, format=None):
    application = get_object_or_404(Applications, id=pk)

    if request.method == 'GET':
        serialized_application = serial.ApplicationsSerializer(application).data

        account_applications = AccountApplication.objects.filter(application_id=application.id)
        vals = account_applications.values()
        account_ids = [item['account_id'] for item in vals]
        if len(account_ids) > 0:
            cards = Account.objects.filter(id__in=account_ids, cardterms__number_ref=F('number'))
            credits = Account.objects.filter(id__in=account_ids, creditterms__number_ref=F('number'))
            deposits = Account.objects.filter(id__in=account_ids, depositterms__number_ref=F('number'))
            saves = Account.objects.filter(id__in=account_ids, saveterms__number_ref=F('number'))
            accs = []
            accs.extend(serial.AccountCardSerializer(cards, many=True).data)
            accs.extend(serial.AccountCreditSerializer(credits, many=True).data)
            accs.extend(serial.AccountDepositSerializer(deposits, many=True).data)
            accs.extend(serial.AccountSaveSerializer(saves, many=True).data)

        else:
            accs = []
        serialized_application['accounts'] = accs

        return Response(serialized_application)

@api_view(['PUT'])
def put_application(request, pk, format=None):
    application = get_object_or_404(Applications, id=pk)
    serializer = serial.ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_application(request, pk, format=None):
    application = get_object_or_404(Applications, id=pk)
    application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def delete_app_acc(request, acc_id, app_id, format=None):
    app_acc = get_object_or_404(AccountApplication, account_id=acc_id, application_id=app_id)
    app_acc.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
def put_app_acc(request, acc_id, app_id, format=None):
    app_acc = get_object_or_404(AccountApplication, account_id=acc_id, application_id=app_id)
    serializer = serial.AccountApplicationSerializer(app_acc, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def put_create_status(request, id, format=None):
    stat = get_object_or_404(ApplicationStatus, id=id)
    stat.status_create = not stat.status_create
    stat.save()
    serializer = serial.ApplicationStatusSerializer(stat)
    return Response(serializer.data)

@api_view(['PUT'])
def put_mod_status(request, id, format=None):
    stat = get_object_or_404(ApplicationStatus, id=id)
    application = get_object_or_404(Applications, application_status_refer=id)
    ref = application.user_id
    user = get_object_or_404(Users, id=ref)
    if user.role == "admin":
        serializer = serial.ApplicationStatusSerializer(stat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    else:
        return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)