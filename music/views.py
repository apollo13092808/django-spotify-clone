from django.contrib.auth import logout
from django.shortcuts import render, redirect


# Create your views here.
def index(request):
    context = {}
    return render(request=request, template_name='music/index.html', context=context)


def sign_in(request):
    return render(request=request, template_name='music/login.html')


def sign_up(request):
    return render(request=request, template_name='music/register.html')


def sign_out(request):
    logout(request=request)
    return redirect(to='login')


def music(request, pk):
    context = {}
    return render(request=request, template_name='music/music.html', context=context)


def profile(request, pk):
    context = {}
    return render(request=request, template_name='music/profile.html', context=context)


def search(request):
    context = {}
    return render(request=request, template_name='music/search.html', context=context)
