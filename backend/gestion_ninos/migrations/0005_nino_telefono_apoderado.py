from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_ninos', '0004_perfilinstitucional_personalinstitucional_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='nino',
            name='telefono_apoderado',
            field=models.CharField(blank=True, help_text='Teléfono de contacto del apoderado', max_length=20, null=True),
        ),
    ]
