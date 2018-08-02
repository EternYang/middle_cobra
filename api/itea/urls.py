from django.contrib import admin
from django.conf.urls import url
from django.views import static

from api import settings
from . import views

urlpatterns = [
    url('register/', views.RegisterView.as_view(), name="register"),
    url(r'^active/(?P<active_code>\w*)/$', views.ActiveUserView.as_view()),
    url('forget/', views.ForgetPasswordView.as_view()),
    url(r'^forgetpassword/(?P<code>\w*)/$', views.ForgetView.as_view()),
    url('login/', views.LoginView.as_view()),
    url('resetpassword/', views.ResetPasswordView.as_view()),
    url('closure/*', views.ClosureView.as_view()),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_URL}),
    url('recharge/', views.RechargeConsumptionView.as_view()),
]
