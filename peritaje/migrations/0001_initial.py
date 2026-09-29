from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Perito",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("especialidad", models.CharField(max_length=150)),
                ("zona", models.CharField(max_length=150)),
                ("carga_activa", models.PositiveIntegerField(default=0)),
                ("disponible", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "perito",
                "indexes": [
                    models.Index(fields=["zona", "especialidad"], name="idx_perito_zona_especialidad"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Inspeccion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("id_siniestro", models.IntegerField()),
                ("id_perito", models.IntegerField()),
                ("fecha_programada", models.DateTimeField()),
                ("status", models.CharField(choices=[("programada", "Programada"), ("completada", "Completada"), ("cancelada", "Cancelada")], default="programada", max_length=20)),
                ("informe", models.TextField(blank=True, null=True)),
                ("evaluacion_danos", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "inspeccion",
                "indexes": [
                    models.Index(fields=["id_perito"], name="idx_inspeccion_perito"),
                    models.Index(fields=["id_siniestro"], name="idx_inspeccion_siniestro"),
                ],
            },
        ),
    ]
