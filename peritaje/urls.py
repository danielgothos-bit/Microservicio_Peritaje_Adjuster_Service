from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/peritos", views.peritos),
    path("api/v1/peritos/disponibilidad", views.disponibilidad),
    path("api/v1/inspecciones", views.inspecciones),
    path("api/v1/inspecciones/<uuid:id>/informe", views.inspeccion_informe),
    path("api/v1/inspecciones/perito/<uuid:id>", views.inspecciones_por_perito),
    path("api/v1/inspecciones/siniestro/<uuid:id>", views.inspecciones_por_siniestro),
]
