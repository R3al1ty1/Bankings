from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
from django.shortcuts import redirect, render
from psycopg2 import Error

from bmstu.db_query import get_account_by_name, connection, change_avaialability
from bmstu_lab.models import Account, AccountStatus, ApplicationStatus, Applications, Users, SaveTerms, CardTerms, CreditTerms, DepositTerms

def getAccountIcon(request, account_id):
    account = Account.objects.get(id=account_id)
    if account.icon:
        response = HttpResponse(account.icon, content_type='image/png')
    else:
        response = HttpResponse(status=204)

    return response

def freezeAccount(request, account_name):
    account = get_account_by_name(connection, account_name)

    if not account:
        return render(request, 'error.html')

    try:
        change_avaialability(connection, account_name)
    except Error as e:
        print("Ошибка при работе с PostgreSQL", e)
        return render(request, 'error.html')

    return HttpResponseRedirect('/accounts')

def GetAccounts(request):
    account_query = request.GET.get('account_url', '')
    if account_query == "":
        return render(request, 'accounts.html', {'accounts': Account.objects.all()})
    else:
        found = Account.objects.filter(
            Q(name__icontains=account_query) | Q(type__icontains=account_query)
        )
        return render(request, 'accounts.html', {'accounts': found, 'account_url': account_query})


def GetAccount(request, name):
    try:
        account = Account.objects.get(name=name)
        if account.type == "Карта":
            try:
                card_terms = CardTerms.objects.get(number_ref=account.number)
                return render(request, 'card.html', {'account': account, 'card_terms': card_terms})
            except CardTerms.DoesNotExist:
                card_terms = None
                return render(request, 'card.html', {'account': account, 'card_terms': card_terms})
        elif account.type == "Кредитный счет":
            try:
                credit_terms = CreditTerms.objects.get(number_ref=account.number)
                return render(request, 'credit.html', {'account': account, 'credit_terms': credit_terms})
            except CardTerms.DoesNotExist:
                credit_terms = None
                return render(request, 'credit.html', {'account': account, 'credit_terms': credit_terms})
        elif account.type == "Вклад":
            try:
                deposit_terms = DepositTerms.objects.get(number_ref=account.number)
                return render(request, 'deposit.html', {'account': account, 'deposit_terms': deposit_terms})
            except DepositTerms.DoesNotExist:
                deposit_terms = None
                return render(request, 'deposit.html', {'account': account, 'deposit_terms': deposit_terms})
        elif account.type == "Сберегательный счет":
            try:
                save_terms = SaveTerms.objects.get(number_ref=account.number)
                return render(request, 'save.html', {'account': account, 'save_terms': save_terms})
            except SaveTerms.DoesNotExist:
                save_terms = None
                return render(request, 'save.html', {'account': account, 'save_terms': save_terms})

    except Account.DoesNotExist:
        return render(request, 'error.html')