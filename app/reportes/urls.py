from django.urls import path, include
from .views import ReporteReservasView, ReporteIngresosView, ReporteViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ReporteViewSet, basename='reportes')

urlpatterns = [
    path('reservas/', ReporteReservasView.as_view()),
    path('ingresos/', ReporteIngresosView.as_view()),
    path('', include(router.urls)),
]
