from django.contrib.auth.models import User
from django.db import models

class Juez(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_juez = models.AutoField(primary_key=True)
    CARGOS = [
        ('Juez Especializado', 'Juez Especializado o Mixto'),
        ('Juez de Paz Letrado', 'Juez de Paz Letrado'),
        ('Juez Superior', 'Juez Superior')
    ]
    
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    fecha_evaluacion = models.DateField()
    fecha_nacimiento = models.DateField()
    orden = models.IntegerField()
    cargo = models.CharField(max_length=100, choices=CARGOS)
    
    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"  

class Antiguedad(models.Model):
    id_antiguedad = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    puntaje = models.FloatField(default=0)

class GradoAcademico(models.Model):
    id_gradoacademico = models.AutoField(primary_key=True)
    TIPOS = [
        ('DOJ', 'Doctorado en especialidad jurídica'),
        ('DONJ', 'Doctorado en especialidad no jurídica'),
        ('MAJ', 'Maestría en especialidad jurídica'),
        ('MANJ', 'Maestría en especialidad no jurídica'),
        ('TINJ', 'Título en especialidad no jurídica'),
    ]
    
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    titulo_gd = models.CharField(max_length=255)
    tipo = models.CharField(max_length=5, choices=TIPOS)
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/gradoacademico/', null=True, blank=True)

class EstudiosMagistratura(models.Model):
    id_estudiomagistratura = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    programa = models.CharField(max_length=255)
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/estudiosmagistratura/', null=True, blank=True)

class EstudioPerfeccionamiento(models.Model):
    id_estudioperfeccionamiento = models.AutoField(primary_key=True)
    TIPOS = [
        ('Estudio de Doctorado', 'Estudio de Doctorado'),
        ('Estudio de Maestría', 'Estudio de Maestría'),
        ('Pasantía', 'Pasantía'),
        ('Curso de Especialización','Curso de Especialización'),
        ('Certámenes Académicos','Certámenes Académicos'),
        ('Evento Académico','Evento Académico'),
        ('Estudio de Ofimática','Estudio de ofimática'),
        ('Estudio de Idioma','Estudio de Idioma')
    ]
    tipo = models.CharField(max_length=100, choices=TIPOS)
    documento = models.FileField(upload_to='certificados/estudioperfeccionamiento/', null=True, blank=True)

class EstudioDoctorado(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_estudiodoctorado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/estudiodoctado/', null=True, blank=True)

class EstudioMaestria(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_estudiomaestria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/estudiomaestria/', null=True, blank=True)

class Pasantia(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_pasantia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('Nacional', 'Nacional'), ('Internacional', 'Internacional')])
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/pasantia/', null=True, blank=True)

class CursoEspecializacion(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_cursoespecializacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    horas = models.IntegerField()
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/cursoespecializacion/', null=True, blank=True)

class CertamenAcademico(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_certamenacademico = models.AutoField(primary_key=True)
    tipo_participacion = models.CharField(max_length=50, choices=[('Expositor', 'Expositor'), ('Ponente', 'Ponente'), ('Panelista', 'Panelista')])
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('Nacional', 'Nacional'), ('Internacional', 'Internacional')])
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/certamenacademico/', null=True, blank=True)

class EventoAcademico(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_eventoacademico = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/eventoacademico/', null=True, blank=True)

class EstudioOfimatica(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_ofimatica = models.AutoField(primary_key=True)
    nivel = models.CharField(max_length=50, choices=[('Básico', 'Básico'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')])
    estudio = models.CharField(max_length=255)  # Nombre del curso de ofimática
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/ofimatica/', null=True, blank=True)

class EstudioIdioma(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    id_idioma = models.AutoField(primary_key=True)
    nivel = models.CharField(max_length=50, choices=[('Básico', 'Básico'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')])
    estudio = models.CharField(max_length=255)  # Nombre del idioma
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/idioma/', null=True, blank=True)

class PublicacionJuridica(models.Model):
    id_publicacionjuridica = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    TIPOS = [
        ('LIBRO', 'Libro'),
        ('REVISTA', 'Revista'),
        ('MERITO', 'Publicación con mérito')
    ]
    tipo = models.CharField(max_length=10, choices=TIPOS)
    nombre = models.CharField(max_length=255)
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/publicacionjuridica/', null=True, blank=True)

class Distincion(models.Model):
    id_distincion = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/distincion/', null=True, blank=True)

class Docencia(models.Model):
    id_docencia = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    curso = models.CharField(max_length=255)
    universidad = models.CharField(max_length=255)
    anio = models.IntegerField()
    horas = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/docencia/', null=True, blank=True)


class Demeritos(models.Model):
    id_demerito = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    medida_disciplinaria = models.CharField(max_length=255)
    TIPOS = [
        ('AMONESTACION', 'Amonestación'),
        ('MULTA', 'Multa'),
        ('SUSPENSION', 'Suspensión')
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS)
    puntaje = models.FloatField()


class PuntajeTotal(models.Model):
    id_puntaje_total = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    puntaje_antiguedad = models.FloatField(default=0)
    puntaje_grado_academico = models.FloatField(default=0)
    puntaje_estudios_magistratura = models.FloatField(default=0)
    puntaje_estudios_doctorado = models.FloatField(default=0)
    puntaje_estudios_maestria = models.FloatField(default=0)
    puntaje_pasantia = models.FloatField(default=0)
    puntaje_curso_especializacion = models.FloatField(default=0)
    puntaje_certamen_academico = models.FloatField(default=0)
    puntaje_evento_academico = models.FloatField(default=0)
    puntaje_ofimatica = models.FloatField(default=0)
    puntaje_idioma = models.FloatField(default=0)
    puntaje_publicaciones = models.FloatField(default=0)
    puntaje_distincion = models.FloatField(default=0)
    puntaje_docencia = models.FloatField(default=0)
    puntaje_demeritos = models.FloatField(default=0)
    
    puntaje_total = models.FloatField(default=0)
