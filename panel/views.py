from django.shortcuts import render

def hello_world(req):
    return render(req, 'panel/index.html')
