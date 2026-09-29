import os
from celery import Celery

app = Celery(
    "adjuster_service",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Cola propia para no mezclar tareas con otros microservicios que comparten Redis.
app.conf.task_default_queue = "peritaje"

@app.task
def publicar_inspection_scheduled(inspection_id):
    # Evento definido por la guía: inspection.scheduled
    print({
        "event": "inspection.scheduled",
        "inspection_id": inspection_id,
    })

@app.task
def publicar_inspection_completed(inspection_id):
    # Evento definido por la guía: inspection.completed
    print({
        "event": "inspection.completed",
        "inspection_id": inspection_id,
    })

@app.task
def consumir_claim_opened(claim_id):
    # Evento consumido por Peritaje: claim.opened
    print({
        "event": "claim.opened",
        "claim_id": claim_id,
    })
