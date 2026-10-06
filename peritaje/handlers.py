"""Eventos que consume el microservicio de Peritaje (sección 4.4)."""
from .servicios import asignacion_automatica


def on_claim_opened(data):
    # Asigna un perito según la especialidad (línea de negocio de la póliza), zona y carga actual.
    asignacion_automatica(data["id_siniestro"], especialidad=data.get("product_type"), zona=data.get("zona"))


HANDLERS = {
    "claim.opened": on_claim_opened,
}
