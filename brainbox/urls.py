from .views import *

from django.urls import path

urlpatterns = [
    path('web-upload', WebLinkView.as_view()),
    path('chat', QueryView.as_view()),
    path('products', ProjectView.as_view()),
    path('file-upload', FileView.as_view())
]
