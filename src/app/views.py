from django.shortcuts import render

# Create your views here.

def login_view(request):
    context = {}
    return render(request, "login.html", context=context)

def dashboard_view(request):
    context = {}
    return render(request, "dashboard.html", context=context)

def dashboard_quiz_view(request, quiz_id):
    context = {"quiz_id": quiz_id}
    return render(request, "dashboard_quiz.html", context=context)

def play_quiz(request, quiz_alphanumeric_code):
    context = {"quiz_alphanumeric_code": quiz_alphanumeric_code, "is_preview": False}
    return render(request, "play_quiz.html", context=context)

def preview_quiz(request, quiz_alphanumeric_code):
    context = {"quiz_alphanumeric_code": quiz_alphanumeric_code, "is_preview": True}
    return render(request, "play_quiz.html", context=context)
