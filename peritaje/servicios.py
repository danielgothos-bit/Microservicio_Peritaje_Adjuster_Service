"""Reglas de asignación de peritos e inspecciones (sección 4.4)."""
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from comun.eventos import publicar

from .models import Inspeccion, Perito


def buscar_perito(especialidad=None, zona=None):
    """Perito disponible con menor carga, priorizando especialidad y zona."""
    disponibles = Perito.objects.filter(disponible=True).order_by("carga_activa", "nombre")
    candidatos = [
        disponibles.filter(especialidad=especialidad, zona=zona) if especialidad and zona else None,
        disponibles.filter(especialidad=especialidad) if especialidad else None,
        disponibles,
    ]
    for qs in candidatos:
        if qs is not None and qs.exists():
            return qs.first()
    return None


@transaction.atomic
def programar_inspeccion(id_siniestro, perito, scheduled_at):
    inspeccion = Inspeccion.objects.create(id_siniestro=id_siniestro, perito=perito, scheduled_at=scheduled_at)
    Perito.objects.filter(pk=perito.pk).update(carga_activa=F("carga_activa") + 1)

    publicar("inspection.scheduled", {
        "id_inspeccion": inspeccion.id_inspeccion,
        "id_siniestro": inspeccion.id_siniestro,
        "id_perito": perito.id_perito,
        "perito": perito.nombre,
        "scheduled_at": inspeccion.scheduled_at,
    })
    return inspeccion


@transaction.atomic
def cargar_informe(inspeccion, findings, report_url=""):
    inspeccion.findings = findings
    inspeccion.report_url = report_url or None
    inspeccion.status = Inspeccion.COMPLETADA
    inspeccion.completed_at = timezone.now()
    inspeccion.save()
    Perito.objects.filter(pk=inspeccion.perito_id, carga_activa__gt=0).update(carga_activa=F("carga_activa") - 1)

    publicar("inspection.completed", {
        "id_inspeccion": inspeccion.id_inspeccion,
        "id_siniestro": inspeccion.id_siniestro,
        "id_perito": inspeccion.perito_id,
        "findings": inspeccion.findings,
        "report_url": inspeccion.report_url,
        "completed_at": inspeccion.completed_at,
    })
    return inspeccion


def asignacion_automatica(id_siniestro, especialidad=None, zona=None):
    """Al abrirse un siniestro se asigna un perito y se programa la inspección para el día siguiente."""
    if Inspeccion.objects.filter(id_siniestro=id_siniestro).exclude(status=Inspeccion.CANCELADA).exists():
        return None  # ya tiene inspección (evento repetido)
    perito = buscar_perito(especialidad, zona)
    if perito is None:
        return None
    return programar_inspeccion(id_siniestro, perito, timezone.now() + timedelta(days=1))
