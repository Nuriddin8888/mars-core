from django.urls import path
from .views import RegisterView, LoginView, StudentCreateView, GroupCreateView

urlpatterns = [
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('students/create/',StudentCreateView.as_view()),
    path('groups/create/', GroupCreateView.as_view()),
]