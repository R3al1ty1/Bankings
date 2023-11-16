import json

from datetime import date, timedelta
from django.http import JsonResponse
from datetime import date
from operator import itemgetter

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.schemas import openapi

from bmstu_lab.models import Account, AccountStatus, ApplicationStatus, Applications, Users, SaveTerms, CardTerms, \
    CreditTerms, DepositTerms, AccountApplication, CustomUser
import bmstu_lab.serializers as serial
from .tasks import delete_account
from .funcs import getAccounts, typeCheck, accsList
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

@api_view(["GET"])
def get_accounts_search(request):
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
            accs = accsList(account_ids)
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

@swagger_auto_schema(
    method='put',
    request_body=serial.AccountApplicationSerializer,
    responses={200: openapi.Response('Successful response', serial.AccountApplicationSerializer)},
)
@api_view(['PUT'])
def put_app_acc(request, acc_id, app_id, format=None):
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
def put_create_status(request, id, format=None):
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

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = serial.UserSerializer
    model_class = CustomUser

    def create(self, request):
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=serial.UserSerializer)
@api_view(['Post'])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("{'status': 'ok'}")
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")

def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'})