from django.db import connection
from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Perito, Inspeccion
from .serializers import PeritoSerializer, InspeccionSerializer, InformeSerializer
from .events import publicar_inspection_scheduled, publicar_inspection_completed


@api_view(["GET"])
def health(request):
    try:
        connection.ensure_connection()
        db = "ok"
    except Exception:
        db = "error"

    codigo = status.HTTP_200_OK if db == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response({"service": "adjuster_service", "status": db, "database": db}, status=codigo)


@api_view(["GET"])
def disponibilidad(request):
    zona = request.query_params.get("zona")
    especialidad = request.query_params.get("especialidad")

    peritos = Perito.objects.filter(
        disponible=True,
        carga_activa__gte=0,
    )

    if zona:
        peritos = peritos.filter(zona=zona)

    if especialidad:
        peritos = peritos.filter(especialidad=especialidad)

    peritos = peritos.order_by("carga_activa")

    return Response(PeritoSerializer(peritos, many=True).data)


@api_view(["POST"])
def inspecciones(request):
    serializer = InspeccionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    inspeccion = serializer.save()

    Perito.objects.filter(id=inspeccion.id_perito).update(
        carga_activa=F("carga_activa") + 1
    )

    publicar_inspection_scheduled.delay(inspeccion.id)

    return Response(
        InspeccionSerializer(inspeccion).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT"])
def inspeccion_informe(request, id):
    try:
        inspeccion = Inspeccion.objects.get(id=id)
    except Inspeccion.DoesNotExist:
        return Response(
            {"code": "NOT_FOUND", "message": "Inspección no encontrada."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = InformeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    inspeccion.informe = serializer.validated_data["informe"]
    inspeccion.evaluacion_danos = serializer.validated_data.get("evaluacion_danos", "")
    inspeccion.status = Inspeccion.COMPLETADA
    inspeccion.save()

    Perito.objects.filter(id=inspeccion.id_perito, carga_activa__gt=0).update(
        carga_activa=F("carga_activa") - 1
    )

    publicar_inspection_completed.delay(inspeccion.id)

    return Response(InspeccionSerializer(inspeccion).data)


@api_view(["GET"])
def inspecciones_por_perito(request, id):
    inspecciones = Inspeccion.objects.filter(id_perito=id).order_by("-fecha_programada")
    return Response(InspeccionSerializer(inspecciones, many=True).data)
