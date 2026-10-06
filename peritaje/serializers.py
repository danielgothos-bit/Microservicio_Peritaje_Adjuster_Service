from rest_framework import serializers

from .models import Inspeccion, Perito


class PeritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perito
        fields = ["id_perito", "nombre", "especialidad", "zona", "carga_activa", "disponible"]
        read_only_fields = ["id_perito", "carga_activa"]


class InspeccionSerializer(serializers.ModelSerializer):
    id_perito = serializers.PrimaryKeyRelatedField(source="perito", queryset=Perito.objects.all())

    class Meta:
        model = Inspeccion
        fields = [
            "id_inspeccion",
            "id_siniestro",
            "id_perito",
            "scheduled_at",
            "completed_at",
            "report_url",
            "findings",
            "status",
        ]
        read_only_fields = ["id_inspeccion", "completed_at", "report_url", "findings", "status"]


class InformeSerializer(serializers.Serializer):
    findings = serializers.CharField()
    report_url = serializers.CharField(required=False, allow_blank=True)
