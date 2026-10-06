from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Inspeccion, Perito
from .serializers import InformeSerializer, InspeccionSerializer, PeritoSerializer
from .servicios import cargar_informe, programar_inspeccion


@api_view(["GET", "POST"])
def peritos(request):
    if request.method == "GET":
        return Response(PeritoSerializer(Perito.objects.order_by("nombre"), many=True).data)

    serializer = PeritoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    perito = serializer.save()
    return Response(PeritoSerializer(perito).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def disponibilidad(request):
    zona = request.query_params.get("zona")
    especialidad = request.query_params.get("especialidad")

    qs = Perito.objects.filter(disponible=True)
    if zona:
        qs = qs.filter(zona=zona)
    if especialidad:
        qs = qs.filter(especialidad=especialidad)

    return Response(PeritoSerializer(qs.order_by("carga_activa"), many=True).data)


@api_view(["POST"])
def inspecciones(request):
    serializer = InspeccionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    datos = serializer.validated_data

    inspeccion = programar_inspeccion(datos["id_siniestro"], datos["perito"], datos["scheduled_at"])
    return Response(InspeccionSerializer(inspeccion).data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def inspeccion_informe(request, id):
    inspeccion = get_object_or_404(Inspeccion, id_inspeccion=id)
    if inspeccion.status != Inspeccion.PROGRAMADA:
        return Response(
            {"code": "INVALID_STATUS", "message": f"La inspección está {inspeccion.status}."},
            status=status.HTTP_409_CONFLICT,
        )

    serializer = InformeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cargar_informe(inspeccion, serializer.validated_data["findings"], serializer.validated_data.get("report_url", ""))
    return Response(InspeccionSerializer(inspeccion).data)


@api_view(["GET"])
def inspecciones_por_perito(request, id):
    qs = Inspeccion.objects.filter(perito_id=id).order_by("-scheduled_at")
    return Response(InspeccionSerializer(qs, many=True).data)


@api_view(["GET"])
def inspecciones_por_siniestro(request, id):
    qs = Inspeccion.objects.filter(id_siniestro=id).order_by("-scheduled_at")
    return Response(InspeccionSerializer(qs, many=True).data)
