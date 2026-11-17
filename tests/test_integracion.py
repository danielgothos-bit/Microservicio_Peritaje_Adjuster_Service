"""Prueba de integración: endpoint + lógica de negocio + base de datos funcionando juntos."""
import uuid
from unittest import mock

from rest_framework.test import APITestCase

from peritaje.models import Inspeccion, Perito


@mock.patch("peritaje.servicios.publicar")
class PeritajeIntegracionTests(APITestCase):
    def test_programar_inspeccion_y_cargar_informe(self, publicar):
        perito = Perito.objects.create(nombre="María López", especialidad="hogar", zona="Montería")
        id_sin = str(uuid.uuid4())
        resp = self.client.post("/api/v1/inspecciones", {"id_siniestro": id_sin, "id_perito": str(perito.pk),
                                                         "scheduled_at": "2026-12-01T10:00:00-05:00"}, format="json")
        self.assertEqual(resp.status_code, 201)
        id_insp = resp.data["id_inspeccion"]
        self.assertEqual(len(self.client.get(f"/api/v1/inspecciones/perito/{perito.pk}").data), 1)
        resp = self.client.put(f"/api/v1/inspecciones/{id_insp}/informe", {"findings": "Filtración en el techo"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Inspeccion.objects.get(pk=id_insp).status, "completada")
        self.assertEqual(publicar.call_args[0][0], "inspection.completed")
