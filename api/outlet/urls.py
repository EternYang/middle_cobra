from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

outlet_router = DefaultRouter()
outlet_router.register('', views.OutletViewSet)

urlpatterns = [
    path('', include(outlet_router.urls)),
]
