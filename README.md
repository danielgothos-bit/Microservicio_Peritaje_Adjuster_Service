# Microservicio de Peritaje — Adjuster Service

Microservicio de InsureFlow definido en la sección 4.4 del documento de arquitectura.

## Responsabilidad

Asignar peritos a siniestros según especialidad, zona y carga de trabajo, programar inspecciones y cargar el informe de evaluación de daños.

## Tecnología

Python · Django REST Framework · PostgreSQL (`adjuster_db`) · Celery + Redis · Docker

## Modelo de datos (3FN, IDs UUID)

`perito` (índice zona + especialidad) e `inspeccion` (scheduled_at, completed_at, findings, report_url).

## Endpoints

```
GET  /api/v1/peritos/disponibilidad?zona=&especialidad= — disponibilidad
GET/POST /api/v1/peritos — listar / registrar peritos
POST /api/v1/inspecciones — programar inspección
PUT  /api/v1/inspecciones/{id}/informe — cargar informe de evaluación
GET  /api/v1/inspecciones/perito/{id} — inspecciones de un perito
GET  /api/v1/inspecciones/siniestro/{id} — inspecciones de un siniestro
GET  /health — estado del servicio y de su base de datos
POST /api/v1/eventos — endpoint interno donde otros microservicios entregan eventos
```

## Eventos

Publica:
- inspection.scheduled
- inspection.completed

Consume:
- claim.opened (asignación automática)

Los eventos se encolan con Celery/Redis y se entregan por HTTP al endpoint `/api/v1/eventos` de cada
suscriptor, con reintentos y backoff exponencial (módulo `comun/eventos.py`). Cada evento se procesa una
sola vez (idempotencia por `event_id`).

## Variables de entorno

- `DATABASE_URL`, `REDIS_URL`: base de datos y Redis propios
- `INTERNAL_TOKEN`: token compartido por todos los microservicios para los eventos
- `RUN_WORKER_IN_WEB=1`: corre el worker de Celery dentro del mismo contenedor (Render gratis)
- `SYNC_TIMEOUT`: timeout de las llamadas REST síncronas (3 s por defecto)
- `CLAIMS_SERVICE_URL`: microservicio de Siniestros
- `DOCUMENT_SERVICE_URL`: microservicio de Documentación

Si una URL no está configurada, el servicio funciona en modo aislado (omite esa validación o ese evento).

## Ejecución local

```bash
docker compose up --build
```

El servicio queda en http://localhost:8000 y las migraciones se aplican solas al arrancar.

Pruebas:

```bash
docker compose exec adjuster_service python manage.py test peritaje
```

## Despliegue en Render

En Render: **New → Blueprint** → conectar este repositorio → **Deploy Blueprint**.
El `render.yaml` crea el servicio web, su PostgreSQL y su Redis (plan gratis).
