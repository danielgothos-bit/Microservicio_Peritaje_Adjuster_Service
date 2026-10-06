import uuid
from unittest import mock

from rest_framework.test import APITestCase

from comun.eventos import INTERNAL_TOKEN

from .models import Perito


@mock.patch("peritaje.servicios.publicar")
class PeritajeTests(APITestCase):
    def setUp(self):
        self.auto = Perito.objects.create(nombre="Carlos", especialidad="auto", zona="Medellín")
        self.auto_ocupado = Perito.objects.create(nombre="Diana", especialidad="auto", zona="Medellín", carga_activa=3)
        self.hogar = Perito.objects.create(nombre="Elena", especialidad="hogar", zona="Bogotá")

    def test_disponibilidad_ordena_por_carga(self, publicar):
        resp = self.client.get("/api/v1/peritos/disponibilidad?especialidad=auto")
        self.assertEqual([p["nombre"] for p in resp.data], ["Carlos", "Diana"])

    def test_claim_opened_asigna_perito(self, publicar):
        siniestro = str(uuid.uuid4())
        resp = self.client.post("/api/v1/eventos", {
            "event": "claim.opened",
            "data": {"id_siniestro": siniestro, "product_type": "auto"},
        }, format="json", HTTP_X_INTERNAL_TOKEN=INTERNAL_TOKEN)
        self.assertEqual(resp.data["status"], "processed")

        resp = self.client.get(f"/api/v1/inspecciones/siniestro/{siniestro}")
        self.assertEqual(resp.data[0]["id_perito"], self.auto.id_perito)
        self.assertEqual(publicar.call_args[0][0], "inspection.scheduled")

        # Un evento repetido no crea otra inspección.
        self.client.post("/api/v1/eventos", {"event": "claim.opened", "data": {"id_siniestro": siniestro}},
                         format="json", HTTP_X_INTERNAL_TOKEN=INTERNAL_TOKEN)
        self.assertEqual(len(self.client.get(f"/api/v1/inspecciones/siniestro/{siniestro}").data), 1)

    def test_programar_y_cargar_informe(self, publicar):
        resp = self.client.post("/api/v1/inspecciones", {
            "id_siniestro": str(uuid.uuid4()),
            "id_perito": str(self.hogar.id_perito),
            "scheduled_at": "2026-10-10T09:00:00-05:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        id = resp.data["id_inspeccion"]
        self.hogar.refresh_from_db()
        self.assertEqual(self.hogar.carga_activa, 1)

        resp = self.client.put(f"/api/v1/inspecciones/{id}/informe",
                               {"findings": "Filtración en el techo", "report_url": "https://docs/informe.pdf"}, format="json")
        self.assertEqual(resp.data["status"], "completada")
        self.assertIsNotNone(resp.data["completed_at"])
        self.assertEqual(publicar.call_args[0][0], "inspection.completed")
        self.hogar.refresh_from_db()
        self.assertEqual(self.hogar.carga_activa, 0)

        resp = self.client.put(f"/api/v1/inspecciones/{id}/informe", {"findings": "otra vez"}, format="json")
        self.assertEqual(resp.status_code, 409)

        resp = self.client.get(f"/api/v1/inspecciones/perito/{self.hogar.id_perito}")
        self.assertEqual(len(resp.data), 1)
