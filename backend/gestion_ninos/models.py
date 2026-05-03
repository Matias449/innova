from django.db import models

class Nino(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, help_text="Formato: 12.345.678-9")
    apoderado_principal = models.CharField(max_length=200)
    telefono_apoderado = models.CharField(max_length=20, blank=True, null=True, help_text="Teléfono de contacto del apoderado")
    fecha_nacimiento = models.DateField()
    curso = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)

    enfermedades = models.TextField(blank=True, null=True, help_text="Antecedentes médicos o enfermedades")
    alergias = models.TextField(blank=True, null=True, help_text="Alergias conocidas")
    situacion_familiar = models.TextField(blank=True, null=True, help_text="Situaciones particulares de la familia")

    # Campos socioeconómicos para modelos predictivos
    quintil_rsh = models.IntegerField(null=True, blank=True, help_text="Quintil del Registro Social de Hogares (1-5)")
    direccion = models.CharField(max_length=300, blank=True, null=True, help_text="Dirección del estudiante")
    numero_hermanos = models.IntegerField(null=True, blank=True, help_text="Número de hermanos")
    SITUACION_LABORAL_CHOICES = [
        ('ninguno', 'Ningún apoderado con trabajo full time'),
        ('uno', 'Un apoderado con trabajo full time'),
        ('ambos', 'Ambos apoderados con trabajo full time'),
    ]
    situacion_laboral_padres = models.CharField(
        max_length=20, choices=SITUACION_LABORAL_CHOICES, blank=True, null=True
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.curso}"

class AnotacionDesarrollo(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='anotaciones')
    fecha = models.DateField()
    descripcion = models.TextField()
    autor = models.CharField(max_length=100, default="Educadora")

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Anotación de {self.nino.nombres} el {self.fecha}"

class RegistroAsistencia(models.Model):
    ESTADOS = [
        ('Presente', 'Presente'),
        ('Ausente', 'Ausente'),
        ('Atraso', 'Atraso'),
        ('Justificado', 'Justificado')
    ]
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Presente')

    class Meta:
        ordering = ['-fecha']
        unique_together = ('nino', 'fecha')

    def __str__(self):
        return f"{self.nino.nombres} - {self.fecha}: {self.estado}"

class PlanificacionCurso(models.Model):
    curso = models.CharField(max_length=50)
    fecha = models.DateField()
    actividades = models.TextField(help_text="Actividades planificadas para el día")

    class Meta:
        unique_together = ('curso', 'fecha')

    def __str__(self):
        return f"Planificación {self.curso} - {self.fecha}"


class EvaluacionActividad(models.Model):
    ESTADOS = [
        ('Logrado', 'Logrado'),
        ('En proceso', 'En proceso'),
        ('Necesita apoyo', 'Necesita apoyo')
    ]
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='evaluaciones')
    fecha = models.DateField()
    evaluacion = models.CharField(max_length=20, choices=ESTADOS)

    class Meta:
        ordering = ['-fecha']
        unique_together = ('nino', 'fecha')

    def __str__(self):
        return f"{self.nino.nombres} - {self.fecha}: {self.evaluacion}"


class PerfilInstitucional(models.Model):
    nombre = models.CharField(max_length=200, default="Jardín Infantil INNOVA")
    direccion = models.CharField(max_length=300, default="Av. Ricardo Lyon 1345, Providencia")
    comuna = models.CharField(max_length=100, default="Providencia")
    region = models.CharField(max_length=100, default="Región Metropolitana")
    lat = models.FloatField(default=-33.4372)
    lng = models.FloatField(default=-70.6506)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = "Perfil Institucional"

    def __str__(self):
        return self.nombre


class PersonalInstitucional(models.Model):
    nombre = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_ingreso = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} — {self.cargo}"


class RegistroMeteorologico(models.Model):
    fecha = models.DateField(unique=True)
    temp_max = models.FloatField(null=True, blank=True)
    temp_min = models.FloatField(null=True, blank=True)
    precipitacion = models.FloatField(null=True, blank=True, help_text="mm de lluvia")
    codigo_clima = models.IntegerField(null=True, blank=True, help_text="WMO weather code")
    viento_max = models.FloatField(null=True, blank=True, help_text="km/h")

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Clima {self.fecha}: {self.temp_min}°C – {self.temp_max}°C"


class RegistroCasosRespiratorios(models.Model):
    fecha_publicacion = models.DateField()
    semana_epidemiologica = models.IntegerField()
    anio = models.IntegerField()
    region = models.CharField(max_length=100)
    tipo_virus = models.CharField(max_length=100, default="Total respiratorios")
    casos_confirmados = models.IntegerField(default=0)

    class Meta:
        ordering = ['-fecha_publicacion']
        unique_together = ('semana_epidemiologica', 'anio', 'region', 'tipo_virus')

    def __str__(self):
        return f"SE{self.semana_epidemiologica}/{self.anio} — {self.region}: {self.casos_confirmados} casos"
