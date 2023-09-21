from django.http import HttpResponse
from datetime import date
from django.shortcuts import redirect, render

Accounts =[
    {"Type": "Карта","Name": "INK No Limits", "Number": "40817810344610004312",
     "Amount": "1 320", "ImageURL": "/image/vklad.png", "Currency": " Руб", "BIC": "044525228", "Interest": "0"},
    {"Type": "Карта","Name": "INK Limited", "Number": "40817840344610004312",
     "Amount": "20 450", "ImageURL": "/image/credit.png", "Currency": " $", "BIC": "044525228", "Interest": "0"},
    {"Type": "Сберегательный счет","Name": "INK копилка",
     "Number": "40817810344610012387",
     "Amount": "150 000", "ImageURL": "/image/ipoteka.png", "Currency": " Руб", "BIC": "044525228", "Interest": "0.1"},
    {"Type": "Кредитный счет","Name": "Потребительский кредит", "Number": "40817810344610065398",
     "Amount": "1 200 000", "ImageURL": "/image/insurance.png", "Currency": " Руб", "BIC": "044525228", "Interest": "12"},
    {"Type": "Вклад","Name": "Выгодный", "Number": "40817810344615513287",
     "Amount": "500 000", "ImageURL": "/image/transactions.png", "Currency": " Руб", "BIC": "044525228", "Interest": "7"}
]

def GetAccounts(request):
    account = request.GET.get('account', '')
    if account == "":
        return render(request, 'accounts.html', {'accounts': Accounts})
    else:
        found = []
        for account in Accounts:
            if str(account.lower()) in str(account["Name"].lower()):
                found.append(account)
        return render(request, 'accounts.html', {'accounts': found})

def GetAccount(request, name):
    for account in Accounts:
        if account['Name'] == name:
            return render(request, 'account.html', {'account': account})