from .views import LoginView, RegisterView

from django.urls import path

urlpatterns = [
    path('login', LoginView.as_view()),
    path('register', RegisterView.as_view())
]
