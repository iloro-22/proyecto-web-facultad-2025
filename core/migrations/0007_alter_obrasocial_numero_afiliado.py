from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_merge_0003_recetamedica_0005_producto_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obrasocial',
            name='numero_afiliado',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
    ]


