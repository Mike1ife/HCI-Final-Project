from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("mockgpt", views.mockgpt, name="mockgpt"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
    path("get-value", views.getValue),
    path("info/", views.info, name="info"),
    path("mock/", views.mock, name="mock"),
    path("identity/", views.identity, name="identity"),
]
