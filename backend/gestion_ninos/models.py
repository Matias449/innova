from django.db import models

class Nino(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, help_text="Formato: 12.345.678-9")
    apoderado_principal = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField()
    curso = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)
    
    # Nuevos campos médicos y familiares
    enfermedades = models.TextField(blank=True, null=True, help_text="Antecedentes médicos o enfermedades")
    alergias = models.TextField(blank=True, null=True, help_text="Alergias conocidas")
    situacion_familiar = models.TextField(blank=True, null=True, help_text="Situaciones particulares de la familia")

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
