from django.db import models


class Perito(models.Model):
    especialidad = models.CharField(max_length=150)
    zona = models.CharField(max_length=150)
    carga_activa = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)

    class Meta:
        db_table = "perito"
        indexes = [
            models.Index(fields=["zona", "especialidad"], name="idx_perito_zona_especialidad"),
        ]

    def __str__(self):
        return f"{self.id} - {self.especialidad} - {self.zona}"


class Inspeccion(models.Model):
    PROGRAMADA = "programada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (PROGRAMADA, "Programada"),
        (COMPLETADA, "Completada"),
        (CANCELADA, "Cancelada"),
    ]

    id_siniestro = models.IntegerField()
    id_perito = models.IntegerField()
    fecha_programada = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PROGRAMADA)
    informe = models.TextField(blank=True, null=True)
    evaluacion_danos = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "inspeccion"
        indexes = [
            models.Index(fields=["id_perito"], name="idx_inspeccion_perito"),
            models.Index(fields=["id_siniestro"], name="idx_inspeccion_siniestro"),
        ]

    def __str__(self):
        return f"Inspección {self.id} - Siniestro {self.id_siniestro}"
