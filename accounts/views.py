import json

from datetime import date, timedelta, datetime
from urllib.parse import urlparse, urlsplit, unquote
from xmlrpc.client import ResponseError

import jwt
from django.http import JsonResponse
from datetime import date
from operator import itemgetter

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.schemas import openapi

from bmstu_lab.models import Account, Agreement, Applications, SaveTerms, CardTerms, \
    CreditTerms, DepositTerms, AccountApplication, CustomUser
import bmstu_lab.serializers as serial
from . import settings
from .permissions import IsAuthenticated, IsManager
from .tasks import delete_account
from .funcs import getAccounts, typeCheck, accsList, create_new_account, getAccountsMod, update_number, create_new_card, \
    create_new_credit, create_new_deposit, create_new_save, get_application_by_user, make_room
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from minio import Minio

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from .jwt_tokens import create_access_token, create_refresh_token, get_jwt_payload, get_access_token, get_refresh_token, \
    set_access_token_cookie, set_refresh_token_cookie

from django.http import JsonResponse
from operator import itemgetter

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_accounts(request):
    user_id = 1
    query = request.GET.get('query', '').capitalize()
    flag = True
    query = query.capitalize()

    if query == "":
        resp = getAccounts(user_id)
        response = Response(resp)
    else:
        if not Account.objects.filter(name__icontains=query, available=True, user_id_refer=user_id).exists():
            flag = False
        if not Account.objects.filter(type__icontains=query, available=True, user_id_refer=user_id).exists() and flag == False:
            response = Response([])
        else:
            if not flag:
                resp = Account.objects.filter(type__icontains=query, available=True, user_id_refer=user_id)
            else:
                resp = Account.objects.filter(name__icontains=query, available=True, user_id_refer=user_id)
            serializer = typeCheck(resp)
            response = Response(serializer)

    return response

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def updateNumber(request):
    update_number(76)
    return Response(status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([AllowAny])
@authentication_classes([])
def put_detail_async(request, id, format=None):
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

@api_view(["GET"])
@permission_classes([IsManager])
@authentication_classes([])
def get_accounts_mod(request):
    query = itemgetter('query')(request.GET)
    query = query.strip()

    if query == "":
        resp = getAccountsMod()
        response = Response(resp)
    else:
        resp = Account.objects.filter(number__startswith=query)
        serializer = typeCheck(resp)
        response = Response(serializer)

    return response


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_accounts_search(request):
    token = get_access_token(request)
    if not token:
        return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    query = itemgetter('query')(request.GET)
    flag = True
    query = query.capitalize()

    try:
        application = Applications.objects.get(status=1, user_id=user_id)
        appId = application.id
    except Applications.DoesNotExist:
        appId = 0

    if query == "":
        resp = getAccounts(user_id)
        resp.append({"appId": appId})
        response = Response(resp)
    else:
        if not Account.objects.filter(name__icontains=query, available=True, user_id_refer=user_id).exists():
            flag = False
        if not Account.objects.filter(type__icontains=query, available=True, user_id_refer=user_id).exists() and flag == False:
            response = Response([])
        else:
            if not flag:
                resp = Account.objects.filter(type__icontains=query, available=True, user_id_refer=user_id)
            else:
                resp = Account.objects.filter(name__icontains=query, available=True, user_id_refer=user_id)
            serializer = typeCheck(resp)

            serialized_data = serializer.data
            serialized_data.append({"appId": appId})
            response = Response(serialized_data)

    return response



@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_agreements(request):
    token = get_access_token(request)
    if not token:
        return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    agreements = Agreement.objects.filter(user_id_refer=user_id)
    serialized_agreements = serial.AgreementSerializer(agreements, many=True)
    return Response(serialized_agreements.data)

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_agreements_open(request):
    agreements = Agreement.objects.filter(user_id_refer=None)
    serialized_agreements = serial.AgreementSerializer(agreements, many=True)
    return Response(serialized_agreements.data)

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_agreements_mod(request):
    query = itemgetter('query')(request.GET)
    query = query.strip()

    if query == "":
        agreements = Agreement.objects.all()
        serialized_agreements = serial.AgreementSerializer(agreements, many=True)
        response_data = serialized_agreements.data
    else:
        agreements = Agreement.objects.filter(id__startswith=query)
        serialized_agreements = serial.AgreementSerializer(agreements, many=True)
        response_data = serialized_agreements.data

    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_agreement(request, id, format=None):
    account = get_object_or_404(Agreement, id=id)
    serialized_data = serial.AgreementSerializer(account).data
    return Response(serialized_data)

@api_view(['PUT'])
@permission_classes([AllowAny])
def put_agreement(request, id, format=None):
    agreement = get_object_or_404(Agreement, id=id)
    serializer = serial.AgreementSerializer(agreement, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def create_agreement(request):
    agreement_type = request.data.get('type', '')
    user_refer = request.data.get('user_id_refer', '')
    desc = request.data.get('description', '')
    small_desc = request.data.get('small_desc', '')
    Agreement.objects.create(type=agreement_type,user_id_refer=user_refer, description=desc, small_desc=small_desc)
    agreements = Agreement.objects.all()
    serializer = serial.AgreementSerializer(agreements, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def create_account(request):
    token = get_access_token(request)
    if not token:
        return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    card_name = request.data.get('cardName', '')
    deposit_name = request.data.get('depositName', '')
    credit_name = request.data.get('creditName', '')
    save_name = request.data.get('saveName', '')
    account_names = [card_name, deposit_name, credit_name, save_name]
    account_name = next((name for name in account_names if name), None)
    currency_name = request.data.get('currencyName', '')
    summ = request.data.get('summ', '')
    purpose = request.data.get('creditPurpose', '')
    days = request.data.get('depDays', '')
    firstName = request.data.get('firstName', '')
    lastName = request.data.get('lastName', '')
    card_type = request.data.get('accType', '')

    account_data = create_new_account(account_name, currency_name, card_type, summ, user_id=user_id)
    ref = Account.objects.get(number=int(account_data["number"]))
    accId = ref.id

    if card_type=="card":
        card_data = create_new_card(firstName, lastName, ref)
    elif card_type=="credit":
        card_data = create_new_credit(purpose, ref)
    elif card_type=="deposit":
        card_data = create_new_deposit(days, ref)
    elif card_type=="save":
        card_data = create_new_save(ref)

    if accId is None:
        return JsonResponse({'error': 'Missing required fields in JSON data'}, status=400)
    applic=get_application_by_user(user_id)
    if applic is None:
        latest = Applications.objects.last()
        applic = Applications(id=latest.id + 1, user_id=user_id, agreement_refer=1, status=1)
        app_id = applic.id
        applic.save()
        appAccs = AccountApplication(application_id=latest.id + 1, account_id=accId)
        appAccs.save()
    else:
        app_id = applic.id
        appAccs = AccountApplication(application_id=app_id, account_id=accId)
        appAccs.save()
    update_number(account_id=accId, application_id=app_id)

    return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)



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

@swagger_auto_schema(
    method='put',
    request_body=serial.AccountCardSerializer,  # Use the appropriate serializer for the 'put_detail' method
    responses={200: openapi.Response('Successful response', serial.AccountCardSerializer)},
)
@api_view(['PUT'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
@authentication_classes([])
def delete_detail(request, id, format=None):
    token = get_access_token(request)
    if not token:
        return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    account = get_object_or_404(Account, id=id)
    account.available = False
    account.delete_date = date.today()
    account.save()
    delete_account.apply_async(args=[account.id], countdown=10)

    resp = getAccounts(user_id)
    return Response(resp)


@api_view(['GET'])
@permission_classes([IsManager])
@authentication_classes([])
def get_applications_mod(request, format=None):
    applications = Applications.objects.all()
    serialized_applications = serial.ApplicationsSerializer(applications, many=True).data

    for application in serialized_applications:
        user = CustomUser.objects.get(id=application['user'])
        application['user_email'] = user.email
        account_applications = AccountApplication.objects.filter(application_id=application['id'])
        vals = account_applications.values()
        account_ids = [item['account_id'] for item in vals]
        if len(account_ids) > 0:
            accs = accsList(account_ids)
        else:
            accs = []
        application['accounts'] = accs

    return Response(serialized_applications)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_applications(request, format=None):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    applications = Applications.objects.filter(user_id=user_id).exclude(status__in=[1,5])
    serialized_applications = serial.ApplicationsSerializer(applications, many=True).data

    for application in serialized_applications:
        account_applications = AccountApplication.objects.filter(application_id=application['id'])
        vals = account_applications.values()
        account_ids = [item['account_id'] for item in vals]
        if len(account_ids) > 0:
            accs = accsList(account_ids)
        else:
            accs = []
        application['accounts'] = accs

    return Response(serialized_applications)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_application(request, pk, format=None):
    application = get_object_or_404(Applications, id=pk)

    if request.method == 'GET':
        serialized_application = serial.ApplicationsSerializer(application).data

        account_applications = AccountApplication.objects.filter(application_id=application.id)
        vals = account_applications.values()
        account_ids = [item['account_id'] for item in vals]
        if len(account_ids) > 0:
            accs = accsList(account_ids)
        else:
            accs = []
        serialized_application['accounts'] = accs

        return Response(serialized_application)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_apps_accs(request, pk, format=None):
    apps_accs = AccountApplication.objects.filter(application_id=pk)
    serialized_apps_accs = serial.AccountApplicationSerializer(apps_accs, many=True).data
    return Response(serialized_apps_accs)

@swagger_auto_schema(
    method='put',
    request_body=serial.ApplicationsSerializer,
    responses={200: openapi.Response('Successful response', serial.ApplicationsSerializer)},
)
@api_view(['PUT'])
@permission_classes([IsManager])
@authentication_classes([])
def put_application(request, pk, format=None):
    if not request.user.is_moderator:  # Проверка прав модератора
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    application = get_object_or_404(Applications, id=pk)
    serializer = serial.ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        application.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([AllowAny])
@authentication_classes([])
def delete_application(request, id, format=None):
    applications_to_delete = AccountApplication.objects.filter(application_id=id)
    applications_to_delete.delete()
    application = Applications.objects.filter(id=id)
    application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_app_acc(request, acc_id, app_id, format=None):
    app_acc = get_object_or_404(AccountApplication, account_id=acc_id, application_id=app_id)
    app_acc.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='put',
    request_body=serial.AccountApplicationSerializer,
    responses={200: openapi.Response('Successful response', serial.AccountApplicationSerializer)},
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def put_app_acc(request, acc_id, app_id, format=None):
    app_acc = get_object_or_404(AccountApplication, account_id=acc_id, application_id=app_id)
    serializer = serial.AccountApplicationSerializer(app_acc, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    responses={200: openapi.Response('Successful response', serial.ApplicationsSerializer)},
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def put_create_status(request, id, format=None):
    if not Applications.objects.filter(pk=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=id)
    application_status = application.status

    if application_status == 5:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    today = datetime.now().date()

    formatted_today = today.strftime("%Y-%m-%d")
    application.status = request_status
    application.creation_date = formatted_today
    application.save()

    serializer = serial.ApplicationsSerializer(application, many=False)
    return Response(serializer.data)

@swagger_auto_schema(
    method='put',
    request_body=serial.ApplicationsSerializer,
    responses={200: openapi.Response('Successful response', serial.ApplicationsSerializer)},
)
@api_view(['PUT'])
@permission_classes([IsManager])
@authentication_classes([])
def put_mod_status(request, id, format=None):
    if not Applications.objects.filter(pk=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]
    if request_status in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=id)

    application_status = application.status

    if application_status in [3, 4, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Обновление статуса заявки
    application.status = request_status
    application.save()
    if request_status == 3:
        accounts = Account.objects.filter(accountapplication__application_id=id)
        accounts.update(available=True)

    serializer = serial.ApplicationsSerializer(application, many=False)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    # Проверка входных данных
    serializer = serial.UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Аутентификация пользователя
    user = authenticate(request, **serializer.validated_data)
    if user is None:
        message = {"message": "Invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Создание токена доступа
    access_token = create_access_token(user.id)

    # Сохранение данных пользователя в кеше
    user_data = {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }
    access_token_lifetime = settings.ACCESS_TOKEN_LIFETIME
    cache.set(access_token, user_data, access_token_lifetime)

    # Отправка ответа с данными пользователя и установкой куки
    response_data = {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }
    response = Response(response_data, status=status.HTTP_201_CREATED)
    response.set_cookie('access_token', access_token, httponly=False, expires=access_token_lifetime, samesite=None, secure=True)

    return response
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    serializer = serial.UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    message = {
        'message': 'User registered successfully',
        'user_id': user.id
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def check(request):
    access_token = get_access_token(request)
    if access_token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)
    if not cache.has_key(access_token):
        message = {"message": "Token is not valid"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    user_data = cache.get(access_token)
    return Response(user_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def refresh(request):
    refresh_token = get_refresh_token(request)
    print(refresh_token)
    if not refresh_token:
        return Response({'error': 'Refresh token not provided'}, status=400)

    try:
        refresh_payload = get_jwt_payload(refresh_token)
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Refresh token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'error': 'Invalid refresh token'}, status=401)

    user_id = refresh_payload.get('user_id')

    if not user_id:
        return Response({'error': 'Invalid refresh token'}, status=401)

    new_access_token = create_refresh_token(user_id)

    return Response({'access_token': new_access_token}, status=200)


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def logout(request):
    access_token = request.COOKIES.get('access_token')
    if access_token is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    if cache.has_key(access_token):
        cache.delete(access_token)

    message = {"message": "Logged out successfully!"}
    response = Response(message, status=status.HTTP_200_OK)
    response.delete_cookie('access_token')

    return response


@api_view(['GET'])
def getIcon(request, type):
    minio_endpoint = '127.0.0.1:9000'
    minio_access_key = 'minio'
    minio_secret_key = 'minio124'
    minio_bucket_name = 'bankings'
    minio_object_name = f'{type}.png'

    minio_object_name = unquote(minio_object_name)
    minio_object_name = minio_object_name.replace('й', 'и')
    minio_object_name = minio_object_name.replace(' ', '-')

    minio_client = Minio(
        endpoint=minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False
    )

    try:
        data_object = minio_client.get_object(bucket_name=minio_bucket_name, object_name=minio_object_name)

        image_data = data_object.read()

        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="{minio_object_name}"'

        return response
    except ResponseError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)