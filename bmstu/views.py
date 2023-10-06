from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseRedirect, Http404
from datetime import date
from django.shortcuts import redirect, render
from psycopg2 import Error

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from bmstu.db_query import get_account_by_name, connection, change_avaialability
from bmstu_lab.models import Account, AccountStatus, ApplicationStatus, Applications, Users, SaveTerms, CardTerms, CreditTerms, DepositTerms
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
def get_account(request, account_number, format=None):
    account = get_object_or_404(Account, number=account_number)
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
def put_detail(request, account_number, format=None):
    account = get_object_or_404(Account, number=account_number)
    if account.type == "Карта":
        serializer = serial.AccountCardSerializer(account, data=request.data)
    elif account.type == "Кредитный счет":
        serializer = serial.AccountCreditSerializer(account, data=request.data)
    elif account.type == "Вклад":
        serializer = serial.AccountDepositSerializer(account, data=request.data)
    elif account.type == "Сберегательный счет":
        serializer = serial.AccountSaveSerializer(account, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_detail(request, account_number, format=None):
    account = get_object_or_404(Account, number=account_number)
    stat = get_object_or_404(AccountStatus, id=account.account_status_refer)
    stat.delete()
    account.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#
# def getAccountIcon(request, account_id):
#     account = Account.objects.get(id=account_id)
#     if account.icon:
#         response = HttpResponse(account.icon, content_type='image/png')
#     else:
#         response = HttpResponse(status=204)
#
#     return response
#
# def freezeAccount(request, account_name):
#     account = get_account_by_name(connection, account_name)
#
#     if not account:
#         return render(request, 'error.html')
#
#     try:
#         change_avaialability(connection, account_name)
#     except Error as e:
#         print("Ошибка при работе с PostgreSQL", e)
#         return render(request, 'error.html')
#
#     return HttpResponseRedirect('/accounts')
#
# def GetAccounts(request):
#     account_query = request.GET.get('account_url', '')
#     if account_query == "":
#         return render(request, 'accounts.html', {'accounts': Account.objects.all()})
#     else:
#         found = Account.objects.filter(
#             Q(name__icontains=account_query) | Q(type__icontains=account_query)
#         )
#         return render(request, 'accounts.html', {'accounts': found, 'account_url': account_query})
#
#
# def GetAccount(request, name):
#     try:
#         account = Account.objects.get(name=name)
#         if account.type == "Карта":
#             try:
#                 card_terms = CardTerms.objects.get(number_ref=account.number)
#                 return render(request, 'card.html', {'account': account, 'card_terms': card_terms})
#             except CardTerms.DoesNotExist:
#                 card_terms = None
#                 return render(request, 'card.html', {'account': account, 'card_terms': card_terms})
#         elif account.type == "Кредитный счет":
#             try:
#                 credit_terms = CreditTerms.objects.get(number_ref=account.number)
#                 return render(request, 'credit.html', {'account': account, 'credit_terms': credit_terms})
#             except CardTerms.DoesNotExist:
#                 credit_terms = None
#                 return render(request, 'credit.html', {'account': account, 'credit_terms': credit_terms})
#         elif account.type == "Вклад":
#             try:
#                 deposit_terms = DepositTerms.objects.get(number_ref=account.number)
#                 return render(request, 'deposit.html', {'account': account, 'deposit_terms': deposit_terms})
#             except DepositTerms.DoesNotExist:
#                 deposit_terms = None
#                 return render(request, 'deposit.html', {'account': account, 'deposit_terms': deposit_terms})
#         elif account.type == "Сберегательный счет":
#             try:
#                 save_terms = SaveTerms.objects.get(number_ref=account.number)
#                 return render(request, 'save.html', {'account': account, 'save_terms': save_terms})
#             except SaveTerms.DoesNotExist:
#                 save_terms = None
#                 return render(request, 'save.html', {'account': account, 'save_terms': save_terms})
#
#     except Account.DoesNotExist:
#         return render(request, 'error.html')