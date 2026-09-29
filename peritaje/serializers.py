from rest_framework import serializers
from .models import Perito, Inspeccion


class PeritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perito
        fields = ["id", "especialidad", "zona", "carga_activa", "disponible"]


class InspeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspeccion
        fields = [
            "id",
            "id_siniestro",
            "id_perito",
            "fecha_programada",
            "status",
            "informe",
            "evaluacion_danos",
        ]
        read_only_fields = ["status"]


class InformeSerializer(serializers.Serializer):
    informe = serializers.CharField()
    evaluacion_danos = serializers.CharField(required=False, allow_blank=True)
