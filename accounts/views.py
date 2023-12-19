import json

from datetime import date, timedelta
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

from bmstu_lab.models import Account, AccountStatus, Applications, SaveTerms, CardTerms, \
    CreditTerms, DepositTerms, AccountApplication, CustomUser
import bmstu_lab.serializers as serial
from . import settings
from .permissions import IsAuthenticated, IsManager
from .tasks import delete_account
from .funcs import getAccounts, typeCheck, accsList, create_account
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
def get_accounts_search(request):
    token = get_access_token(request)
    # Добавлен блок для обработки отсутствия токена, вам может потребоваться определить, как обрабатывать эту ситуацию
    if not token:
        return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    query = itemgetter('query')(request.GET)
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


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def create_account(request):
    token = get_access_token(request)
    # Добавлен блок для обработки отсутствия токена, вам может потребоваться определить, как обрабатывать эту ситуацию
    if not token:
        return Response({"error": "Access token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    card_name = request.data.get('cardName', '')
    currency_name = request.data.get('currencyName', '')
    account = create_account(card_name,currency_name, user_id=user_id)
    Account.objects.create(type=account.type,name=account.name, amount=account.amount, number=account.number, currency=account.currency,bic=account.bic,account_status_refer=account.account_status_refer, user_id_refer=account.user_id_refer,icon=account.icon, available=account.available)

    accounts = Account.objects.all()
    serializer = serial.AccountSerializer(accounts, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountCardSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountCardSerializer)},
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def post_card(request, format=None):
    serializer = serial.AccountCardSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountCreditSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountCreditSerializer)},
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def post_credit(request, format=None):
    serializer = serial.AccountCreditSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountDepositSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountDepositSerializer)},
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def post_deposit(request, format=None):
    serializer = serial.AccountDepositSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountSaveSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountSaveSerializer)},
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
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

@swagger_auto_schema(
    method='put',
    request_body=serial.AccountCardSerializer,  # Use the appropriate serializer for the 'put_detail' method
    responses={200: openapi.Response('Successful response', serial.AccountCardSerializer)},
)
@api_view(['PUT'])
@permission_classes([IsManager])
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

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountApplicationSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountApplicationSerializer)},
)
@api_view(['POST'])
def add_account_to_application(request, accId):
    user_id = 13
    if accId is None:
        return JsonResponse({'error': 'Missing required fields in JSON data'}, status=400)
    try:
        falseStatus = Applications.objects.get(status=1,user_id=user_id)
        first_app = falseStatus.first()
        app_id = first_app.id
    except:
        app_id = -1
    if app_id != -1:
        appAccs = AccountApplication(application_id=app_id, account_id=accId)
        appAccs.save()
    else:
        latest = Applications.objects.last()
        applic = Applications(id=latest.id+1,user_id=user_id, agreement_refer=1, status=1)
        applic.save()
        appAccs = AccountApplication(application_id=latest.id+1, account_id=accId)
        appAccs.save()

    return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_applications(request, format=None):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    applications = Applications.objects.filter(user_id=user_id).exclude(status__in=[5])
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
@permission_classes([IsAuthenticated])
def get_application_draft(request, format=None):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]
    application = get_object_or_404(Applications, status=1, user_id=user_id)

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

@swagger_auto_schema(
    method='put',
    request_body=serial.ApplicationsSerializer,
    responses={200: openapi.Response('Successful response', serial.ApplicationsSerializer)},
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def put_application(request, pk, format=None):
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
    application = get_object_or_404(Applications, id=id)
    application.delete()
    application.save()
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
@permission_classes([IsManager])
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

    application.status = request_status
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
def put_mod_status(request, application_id, format=None):
    if not Applications.objects.filter(pk=application_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]  # Статус, на который мы хотим поменять

    if request_status in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=application_id)

    application_status = application.status  # Текущий статус заявки

    if application_status in [3, 4, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application.status = request_status
    application.save()

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
        "is_staff": user.is_staff,
        "access_token": access_token
    }
    access_token_lifetime = settings.ACCESS_TOKEN_LIFETIME
    cache.set(access_token, user_data, access_token_lifetime)

    # Отправка ответа с данными пользователя и установкой куки
    response_data = {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "is_staff": user.is_staff,
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
    refresh_token = get_access_token(request)
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

    #
    # try:
    #     # Получение списка объектов в бакете
    #     objects = minio_client.list_objects(minio_bucket_name, recursive=True)
    #
    #     # Собираем имена файлов (ключей) в список
    #     image_names = [obj.object_name for obj in objects]
    #     if not image_names:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #
    #     return Response(image_names, status=status.HTTP_200_OK)
    # except ResponseError as e:
    #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
