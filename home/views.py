from django.shortcuts import render

def homepage(request):
    return render(request, "home.html")

def sklep(request):
    return render(request, "sklep.html")
