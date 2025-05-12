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

class Vigencia(models.Model):
    idvigencia = models.AutoField(primary_key=True)
    fecha_minima = models.DateField()
    fecha_maxima = models.DateField()
    estado = models.CharField(max_length=100, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default='Activo')

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

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    titulo_gd = models.CharField(max_length=255)
    tipo = models.CharField(max_length=5, choices=TIPOS)
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/gradoacademico/', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class EstudiosMagistratura(models.Model):
    id_estudiomagistratura = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    programa = models.CharField(max_length=255)
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/estudiosmagistratura/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

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
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_estudiodoctorado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/estudiodoctado/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class EstudioMaestria(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_estudiomaestria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/estudiomaestria/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class Pasantia(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_pasantia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('Nacional', 'Nacional'), ('Internacional', 'Internacional')])
    anio = models.IntegerField()
    nota = models.FloatField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/pasantia/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class CursoEspecializacion(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_cursoespecializacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    horas = models.IntegerField()
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/cursoespecializacion/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class CertamenAcademico(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_certamenacademico = models.AutoField(primary_key=True)
    tipo_participacion = models.CharField(max_length=50, choices=[('Expositor', 'Expositor'), ('Ponente', 'Ponente'), ('Panelista', 'Panelista')])
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('Nacional', 'Nacional'), ('Internacional', 'Internacional')])
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/certamenacademico/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class EventoAcademico(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_eventoacademico = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/eventoacademico/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class EstudioOfimatica(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_ofimatica = models.AutoField(primary_key=True)
    nivel = models.CharField(max_length=50, choices=[('Básico', 'Básico'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')])
    estudio = models.CharField(max_length=255)  # Nombre del curso de ofimática
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/ofimatica/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class EstudioIdioma(models.Model):
    id_estudioperfeccionamiento = models.ForeignKey(EstudioPerfeccionamiento, on_delete=models.CASCADE)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    id_idioma = models.AutoField(primary_key=True)
    nivel = models.CharField(max_length=50, choices=[('Básico', 'Básico'), ('Intermedio', 'Intermedio'), ('Avanzado', 'Avanzado')])
    estudio = models.CharField(max_length=255)  # Nombre del idioma
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/idioma/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

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
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class Distincion(models.Model):
    id_distincion = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/distincion/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

class Docencia(models.Model):
    id_docencia = models.AutoField(primary_key=True)
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, to_field='idvigencia')
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    curso = models.CharField(max_length=255)
    universidad = models.CharField(max_length=255)
    anio = models.IntegerField()
    horas = models.IntegerField()
    puntaje = models.FloatField()
    documento = models.FileField(upload_to='certificados/docencia/', null=True, blank=True)
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')


class Demeritos(models.Model):
    id_demerito = models.AutoField(primary_key=True)
    juez = models.ForeignKey(Juez, on_delete=models.CASCADE, to_field='id_juez')
    TIPOS = [
        ('AMONESTACION', 'Amonestación'),
        ('MULTA', 'Multa'),
        ('SUSPENSION', 'Suspensión')
    ]

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')
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


class Antiguedad_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    js_puntaje_min = models.FloatField()
    js_puntaje_max = models.FloatField()
    jpl_puntaje_min = models.FloatField()
    jpl_puntaje_max = models.FloatField()
    je_puntaje_min = models.FloatField()
    je_puntaje_max = models.FloatField()

class GradoAcademico_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    doj_puntaje = models.FloatField()
    donj_puntaje = models.FloatField()
    maj_puntaje = models.FloatField()
    manj_puntaje = models.FloatField()
    tinj_puntaje = models.FloatField()

class Magistratura_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_alto = models.FloatField()
    puntaje_semialto = models.FloatField()
    puntaje_medio = models.FloatField()
    puntaje_bajo = models.FloatField()

class Doctorado_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_alto = models.FloatField()
    puntaje_medio = models.FloatField()
    puntaje_bajo = models.FloatField()

class Maestria_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_alto = models.FloatField()
    puntaje_medio = models.FloatField()
    puntaje_bajo = models.FloatField()

class Pasantia_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_alto = models.FloatField()
    puntaje_bajo = models.FloatField()

class CursoEspecializacion_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_alto = models.FloatField()
    puntaje_medio = models.FloatField()
    puntaje_bajo = models.FloatField()

class CertamenAcademico_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_alto = models.FloatField()
    puntaje_bajo = models.FloatField()

class EventoAcademico_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje = models.FloatField()

class Ofimatica_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_basico = models.FloatField()
    puntaje_intermedio = models.FloatField()
    puntaje_avanzado = models.FloatField()

class Idiomas_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_basico = models.FloatField()
    puntaje_intermedio = models.FloatField()
    puntaje_avanzado = models.FloatField()

class PublicacionJuridica_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje_libro = models.FloatField()
    puntaje_revista = models.FloatField()
    puntaje_merito = models.FloatField()

class Distincion_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje = models.FloatField()

class Docencia_valor_puntaje(models.Model):
    id = models.AutoField(primary_key=True)
    puntaje = models.FloatField()

class ValorizacionPuntaje(models.Model):
    id = models.AutoField(primary_key=True)
    valor_antiguedad = models.ForeignKey(Antiguedad_valor_puntaje, on_delete=models.CASCADE)
    valor_grado_academico = models.ForeignKey(GradoAcademico_valor_puntaje, on_delete=models.CASCADE)
    valor_magistratura = models.ForeignKey(Magistratura_valor_puntaje, on_delete=models.CASCADE)
    valor_doctorado = models.ForeignKey(Doctorado_valor_puntaje, on_delete=models.CASCADE)
    valor_maestria = models.ForeignKey(Maestria_valor_puntaje, on_delete=models.CASCADE)
    valor_pasantia = models.ForeignKey(Pasantia_valor_puntaje, on_delete=models.CASCADE)
    valor_curso_especializacion = models.ForeignKey(CursoEspecializacion_valor_puntaje, on_delete=models.CASCADE)
    valor_certamen_academico = models.ForeignKey(CertamenAcademico_valor_puntaje, on_delete=models.CASCADE)
    valor_evento_academico = models.ForeignKey(EventoAcademico_valor_puntaje, on_delete=models.CASCADE)
    valor_ofimatica = models.ForeignKey(Ofimatica_valor_puntaje, on_delete=models.CASCADE)
    valor_idiomas = models.ForeignKey(Idiomas_valor_puntaje, on_delete=models.CASCADE)
    valor_publicacion_juridica = models.ForeignKey(PublicacionJuridica_valor_puntaje, on_delete=models.CASCADE)
    valor_distincion = models.ForeignKey(Distincion_valor_puntaje, on_delete=models.CASCADE)
    valor_docencia = models.ForeignKey(Docencia_valor_puntaje, on_delete=models.CASCADE)
