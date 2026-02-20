from django.shortcuts import render


def index(req):
    return render(req, 'shop/index.html')

def about(req):
    return render(req, 'shop/about.html')