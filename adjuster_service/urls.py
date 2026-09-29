from django.urls import path
from peritaje.views import (
    health,
    disponibilidad,
    inspecciones,
    inspeccion_informe,
    inspecciones_por_perito,
)

urlpatterns = [
    path("health", health),
    path("api/v1/peritos/disponibilidad", disponibilidad),
    path("api/v1/inspecciones", inspecciones),
    path("api/v1/inspecciones/<int:id>/informe", inspeccion_informe),
    path("api/v1/inspecciones/perito/<int:id>", inspecciones_por_perito),
]
