"""Pruebas unitarias: una unidad de lógica de negocio aislada; las dependencias externas se simulan con mocks."""
import uuid
from unittest import mock

from django.test import TestCase

from peritaje.models import Perito
from peritaje.servicios import asignacion_automatica, buscar_perito


class AsignacionUnitTests(TestCase):
    def setUp(self):
        Perito.objects.create(nombre="Ocupado", especialidad="auto", zona="Montería", carga_activa=4)
        self.libre = Perito.objects.create(nombre="Libre", especialidad="auto", zona="Montería", carga_activa=0)
        Perito.objects.create(nombre="Hogar", especialidad="hogar", zona="Montería", carga_activa=0)

    def test_elige_perito_de_la_especialidad_con_menor_carga(self):
        self.assertEqual(buscar_perito("auto", "Montería"), self.libre)

    @mock.patch("peritaje.servicios.publicar")
    def test_asignacion_automatica_programa_y_publica_evento(self, publicar):
        insp = asignacion_automatica(uuid.uuid4(), "auto", "Montería")
        self.assertEqual(insp.perito, self.libre)
        self.assertEqual(publicar.call_args[0][0], "inspection.scheduled")
        self.libre.refresh_from_db()
        self.assertEqual(self.libre.carga_activa, 1)
