from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
from django.shortcuts import redirect, render
from bmstu_lab.models import Account, AccountStatus, ApplicationStatus, Applications, Users, SaveTerms, CardTerms, CreditTerms, DepositTerms

def getAccountIcon(request, account_id):
    account = Account.objects.get(id=account_id)
    if account.icon:
        response = HttpResponse(account.icon, content_type='image/png')
    else:
        response = HttpResponse(status=204)

    return response

def freezeAccount(request, account_name):
    try:
        account = Account.objects.get(name=account_name)
    except Account.DoesNotExist:
        return render(request, 'error.html')

    try:
        account.change_availability()
    except Exception as e:
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
    account = Account.objects.get(name=name)
    return render(request, 'card.html', {'account': account, 'card_terms': card_terms})
