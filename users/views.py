from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import DefaultUserCreationForm


def signup(request):
    if request.method == "POST":
        form = DefaultUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = DefaultUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})
