import uuid

from django.db import models
from django.db.models import Q


class Perito(models.Model):
    id_perito = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    especialidad = models.CharField(max_length=150)
    zona = models.CharField(max_length=150)
    carga_activa = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)

    class Meta:
        db_table = "perito"
        indexes = [
            models.Index(fields=["zona", "especialidad"], name="idx_perito_zona_especialidad"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(carga_activa__gte=0), name="chk_perito_carga_activa"),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.especialidad} - {self.zona}"


class Inspeccion(models.Model):
    PROGRAMADA = "programada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (PROGRAMADA, "Programada"),
        (COMPLETADA, "Completada"),
        (CANCELADA, "Cancelada"),
    ]

    id_inspeccion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_siniestro = models.UUIDField()  # FK-ext -> Claims Service
    perito = models.ForeignKey(Perito, on_delete=models.PROTECT, related_name="inspecciones", db_column="id_perito")
    scheduled_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    report_url = models.TextField(blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PROGRAMADA)

    class Meta:
        db_table = "inspeccion"
        indexes = [
            models.Index(fields=["perito"], name="idx_inspeccion_perito"),
            models.Index(fields=["id_siniestro"], name="idx_inspeccion_siniestro"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["programada", "completada", "cancelada"]),
                name="chk_inspeccion_status",
            ),
        ]

    def __str__(self):
        return f"Inspección {self.id_inspeccion} - Siniestro {self.id_siniestro}"
