import json

from datetime import date, timedelta
from django.http import JsonResponse
from datetime import date
from operator import itemgetter

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.schemas import openapi

from bmstu_lab.models import Account, AccountStatus, ApplicationStatus, Applications, SaveTerms, CardTerms, \
    CreditTerms, DepositTerms, AccountApplication, CustomUser
import bmstu_lab.serializers as serial
from . import settings
from .permissions import IsAdmin, IsManager
from .tasks import delete_account
from .funcs import getAccounts, typeCheck, accsList
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .jwt_helper import create_access_token, create_refresh_token, get_jwt_payload, get_access_token, get_refresh_token

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

@api_view(["GET"])
def get_accounts_search(request):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    query = itemgetter('query')(request.GET)
    flag = True
    query = query.capitalize()

    if query == "":
        resp = getAccounts()
        return Response(resp)
    else:
        if not Account.objects.filter(name__icontains=query, available=True).exists():
            flag = False
        if not Account.objects.filter(type__icontains=query, available=True).exists() and flag == False:
            return Response([])
        if not flag:
            resp = Account.objects.filter(type__icontains=query, available=True)
        if flag:
            resp = Account.objects.filter(name__icontains=query, available=True)
        serializer = typeCheck(resp)
        return Response(serializer)

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountCardSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountCardSerializer)},
)
@api_view(['POST'])
@method_permission_classes((IsAdmin,))
def post_card(request, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
@method_permission_classes((IsAdmin,))
def post_credit(request, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
@method_permission_classes((IsAdmin,))
def post_deposit(request, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
@method_permission_classes((IsAdmin,))
def post_save(request, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    serializer = serial.AccountSaveSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_account(request, id, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
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
@method_permission_classes((IsAdmin,))
def put_detail(request, id, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    account = get_object_or_404(Account, id=id)
    account.available = False
    account.delete_date = date.today()
    account.save()
    #delete_account.apply_async(args=[account.id], countdown=10)

    resp = getAccounts()
    return Response(getAccounts())

@swagger_auto_schema(
    method='post',
    request_body=serial.AccountApplicationSerializer,
    responses={201: openapi.Response('Successful response', serial.AccountApplicationSerializer)},
)
@api_view(['POST'])
def add_account_to_application(request):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    applications = Applications.objects.all()
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
def get_application(request, pk, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
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
def put_application(request, pk, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    application = get_object_or_404(Applications, id=pk)
    serializer = serial.ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_application(request, pk, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    application = get_object_or_404(Applications, id=pk)
    application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@method_permission_classes((IsAdmin,))
def delete_app_acc(request, acc_id, app_id, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    app_acc = get_object_or_404(AccountApplication, account_id=acc_id, application_id=app_id)
    app_acc.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='put',
    request_body=serial.AccountApplicationSerializer,
    responses={200: openapi.Response('Successful response', serial.AccountApplicationSerializer)},
)
@api_view(['PUT'])
@method_permission_classes((IsAdmin,))
def put_app_acc(request, acc_id, app_id, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    app_acc = get_object_or_404(AccountApplication, account_id=acc_id, application_id=app_id)
    serializer = serial.AccountApplicationSerializer(app_acc, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    responses={200: openapi.Response('Successful response', serial.ApplicationStatusSerializer)},
)
@api_view(['PUT'])
@method_permission_classes((IsAdmin,))
def put_create_status(request, id, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    stat = get_object_or_404(ApplicationStatus, id=id)
    stat.status_create = not stat.status_create
    stat.save()
    serializer = serial.ApplicationStatusSerializer(stat)
    return Response(serializer.data)

@swagger_auto_schema(
    method='put',
    request_body=serial.ApplicationStatusSerializer,
    responses={200: openapi.Response('Successful response', serial.ApplicationStatusSerializer)},
)
@api_view(['PUT'])
@method_permission_classes((IsAdmin,))
def put_mod_status(request, id, format=None):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    stat = get_object_or_404(ApplicationStatus, id=id)
    application = get_object_or_404(Applications, application_status_refer=id)
    ref = application.user_id
    user = get_object_or_404(CustomUser, id=ref)
    if user.role == "admin":
        serializer = serial.ApplicationStatusSerializer(stat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    else:
        return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    # Ensure email and passwords are posted properly
    serializer = serial.UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Check credentials
    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Create new access and refresh token
    access_token = create_access_token(user.id)

    # Add access token to redis for validating by other services
    user_data = {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "is_staff": user.is_staff,
        "access_token": access_token
    }
    access_token_lifetime = settings.ACCESS_TOKEN_LIFETIME  # Предположим, что у вас есть такая переменная в settings.py
    cache.set(access_token, user_data, access_token_lifetime)

    # Create response object
    response = Response(user_data, status=status.HTTP_201_CREATED)
    # Set access token in cookie
    response.set_cookie('access_token', access_token, httponly=False, expires=access_token_lifetime, samesite="Lax")

    return response

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    # Ensure username and passwords are posted is properly
    serializer = serial.UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = serializer.save()
    message = {
        'message': 'User registered successfully',
        'user_id': user.id
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check(request):
    access_token = get_access_token(request)

    if access_token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Check is token in Redis
    if not cache.has_key(access_token):
        message = {"message": "Token is not valid"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    user_data = cache.get(access_token)
    return Response(user_data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def logout(request):
    access_token = request.COOKIES.get('access_token')

    # Check access token is in cookie
    if access_token is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    #  Check access token is in Redis
    if cache.has_key(access_token):
        # Delete access token from Redis
        cache.delete(access_token)

    # Create response object
    message = {"message": "Logged out successfully!"}
    response = Response(message, status=status.HTTP_200_OK)
    # Delete access token from cookie
    response.delete_cookie('access_token')

    return response