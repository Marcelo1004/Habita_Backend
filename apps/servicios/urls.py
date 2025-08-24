from django.urls import path
from .views import ServicioListView, ServicioDetailView

urlpatterns = [

    path('<int:pk>/', ServicioDetailView.as_view(), name='servicio-detail'),
]