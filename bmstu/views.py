from django.http import HttpResponse
from datetime import date
from django.shortcuts import redirect, render

Descriptions = [
    "Вклад - это идеальный способ для тех, кто не хочет волноваться о возможных рисках. Это надежный способ сохранения и увеличения капитала при помощи различных стратегий",
	"Кредитный счет является отличный способом для получения денежных средств для различных целей. Не стоит откладывать крупную покупку!",
	"На карте клиенты могут хранить личные средства, а также удобно ими пользоваться",
	"При помощи сберегательного счета Вы можете хранить деньги с небольшим процентом, а также пользоваться ими в любое удобное время"
]

Services =[
    {"Name": "Вклад", "Conditions": "Вклад - надежный способ сохранить и увеличить свои сбережения",
     "Description": Descriptions[0], "ImageURL": "/image/vklad.png"},
    {"Name": "Кредит",
     "Conditions": "Заем средств на личные нужды",
     "Description": Descriptions[1], "ImageURL": "/image/credit.png"},
    {"Name": "Карта",
     "Conditions": "Удобный способ хранения и перевода денежных средств",
     "Description": Descriptions[2], "ImageURL": "/image/ipoteka.png"},
    {"Name": "Сберегательный счет", "Conditions": "Сохарните Ваши средства до востребования",
     "Description": Descriptions[3], "ImageURL": "/image/insurance.png"},
]

def GetServices(request):
    query = request.GET.get('query', '')
    if query == "":
        return render(request, 'services.html', {'services': Services})
    else:
        found = []
        for service in Services:
            if str(query.lower()) in str(service["Name"].lower()):
                found.append(service)
        return render(request, 'services.html', {'services': found})

def GetService(request, name):
    for service in Services:
        if service['Name'] == name:
            return render(request, 'service.html', {'service': service})
