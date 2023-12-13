from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("mockgpt", views.mockgpt, name="mockgpt"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
    # path("get-value", views.getValue),
    path("info/", views.info, name="info"),
    path("info/NTU/", views.NTU, name="NTU"),
    path("info/NTU/HT-Lin", views.HT_Lin, name="HT_Lin"),
    path("info/NTU/RueyFengChang", views.Ruey_Feng_Chang, name="Ruey_Feng_Chang"),
    path("info/NTU/P-Lin", views.P_Lin, name="P_Lin"),
    path("info/NYCU/", views.NYCU, name="NYCU"),
    path("info/NYCU/LanDaVan", views.Lan_Da_Van, name="Lan_Da_Van"),
    path("info/NYCU/YenYuLin", views.Yen_Yu_Lin, name="Yen_Yu_Lin"),
    path("info/NYCU/JungHongChung", views.Jung_Hong_Chuang, name="Jung_Hong_Chuang"),
    path("info/NTHU/", views.NTHU, name="NTHU"),
    path("info/NTHU/Che_Rung_Lee", views.Che_Rung_Lee, name="Che_Rung_Lee"),
    path("info/NTHU/Shang_Hong_Lai", views.Shang_Hong_Lai, name="Shang_Hong_Lai"),
    path("info/NTHU/Ching_Te_Chiu", views.Ching_Te_Chiu, name="Ching_Te_Chiu"),
    path("mock/", views.mock, name="mock"),
    path("mock/test", views.test, name="test"),
    path("identity/", views.identity, name="identity"),
]
