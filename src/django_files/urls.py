"""quiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django_files import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView
from app import views, views_quiz, views_user
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='/static/images/favicon.webp', permanent=True)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view),
    path('api/register/', views_user.register_user),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('dashboard/', views.dashboard_view),
    path('api/quizes/', views_quiz.quizes),
    path('api/quizes/<int:quiz_id>/', views_quiz.quiz),
    path('dashboard/<int:quiz_id>/', views.dashboard_quiz_view),
    path('api/play/<str:quiz_alphanumeric_code>/', views_quiz.play),
    path('api/preview/<str:quiz_alphanumeric_code>/', views_quiz.preview),
    path('play/<str:quiz_alphanumeric_code>/', views.play_quiz),
    path('preview/<str:quiz_alphanumeric_code>/', views.preview_quiz),
    path('favicon.ico/', favicon_view),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

