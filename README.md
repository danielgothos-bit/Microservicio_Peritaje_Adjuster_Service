# Microservicio de Peritaje — Adjuster Service

Implementación del microservicio de Peritaje definido en la guía de InsureFlow.

## Responsabilidad

Gestionar:
- asignación de peritos a siniestros según especialidad y zona geográfica;
- programación de inspecciones presenciales;
- carga estructurada del informe de evaluación de daños.

## Tecnología

- Python
- Django REST Framework
- PostgreSQL (`adjuster_db`)
- Celery
- Redis
- Docker

## Endpoints definidos

GET  /api/v1/peritos/disponibilidad
POST /api/v1/inspecciones
PUT  /api/v1/inspecciones/{id}/informe
GET  /api/v1/inspecciones/perito/{id}
GET  /health

## Eventos

Consume:
- claim.opened

Publica:
- inspection.scheduled
- inspection.completed

## Ejecución

```bash
docker compose up --build
```

Las migraciones se aplican automáticamente al arrancar (`start.sh`).

El servicio queda disponible en el puerto 8000.

## Despliegue en Render

El archivo `render.yaml` crea el servicio web `adjuster-service` (Docker, plan gratis, health check en `/health`).

Como el plan gratis de Render permite una sola PostgreSQL y un solo Key Value por cuenta,
este servicio usa el servidor PostgreSQL y el Redis de `payment-db` / `payment-redis`:
- `DATABASE_URL`: "Internal Database URL" de `payment-db`;
- `DB_NAME=adjuster_db`: base de datos propia de Peritaje dentro de ese servidor (se crea sola con `ensure_db.py`);
- `REDIS_URL`: "Internal Key Value URL" de `payment-redis`.

Las tareas de Celery van a la cola `peritaje`, para no mezclarse con las de otros servicios en el mismo Redis.
