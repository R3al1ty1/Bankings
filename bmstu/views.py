from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
from django.shortcuts import redirect, render
from bmstu_lab.models import Agreement, AgreementStatus, ApplicationStatus, Applications, Users

def getAgreementIcon(request, Agreement_id):
    Agreement = Agreement.objects.get(id=Agreement_id)
    if Agreement.icon:
        response = HttpResponse(Agreement.icon, content_type='image/png')
    else:
        response = HttpResponse(status=204)

    return response

def freezeAgreement(request, Agreement_name):
    try:
        Agreement = Agreement.objects.get(name=Agreement_name)
    except Agreement.DoesNotExist:
        return render(request, 'error.html')

    try:
        Agreement.change_availability()
    except Exception as e:
        return render(request, 'error.html')

    return HttpResponseRedirect('/Agreements')

def GetAgreements(request):
    Agreement_query = request.GET.get('Agreement_url', '')
    if Agreement_query == "":
        return render(request, 'Accounts.html', {'Agreements': Agreement.objects.all()})
    else:
        found = Agreement.objects.filter(
            Q(name__icontains=Agreement_query) | Q(type__icontains=Agreement_query)
        )
        return render(request, 'Accounts.html', {'Agreements': found, 'Agreement_url': Agreement_query})


def GetAgreement(request, name):
    Agreement = Agreement.objects.get(name=name)
    return render(request, 'account.html', {'Agreement': Agreement, 'card_terms': card_terms})
