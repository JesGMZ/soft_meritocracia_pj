from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from .models import *
from django.db.models import Sum

def calcular_puntaje_total(juez_id):
    juez = get_object_or_404(Juez, id_juez=juez_id)

    # Sumamos los puntajes de cada modelo relacionado, pero con los límites establecidos
    puntaje_antiguedad = min(
        Antiguedad.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        12  # Límite de 12 puntos
    )
    puntaje_grado_academico = min(
        GradoAcademico.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        17  # Límite de 17 puntos
    )
    puntaje_estudios_magistratura = min(
        EstudiosMagistratura.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        8  # Límite de 8 puntos
    )
    puntaje_estudios_doctorado = min(
        EstudioDoctorado.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        1.5  # Límite de 1.5 puntos
    )
    puntaje_estudios_maestria = min(
        EstudioMaestria.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        1.5  # Límite de 1.5 puntos
    )
    puntaje_pasantia = min(
        Pasantia.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        1.5  # Límite de 1.5 puntos
    )
    puntaje_curso_especializacion = min(
        CursoEspecializacion.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        3  # Límite de 3 puntos
    )
    puntaje_certamen_academico = min(
        CertamenAcademico.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        2  # Límite de 2 puntos
    )
    puntaje_evento_academico = min(
        EventoAcademico.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        2  # Límite de 2 puntos
    )
    puntaje_ofimatica = min(
        EstudioOfimatica.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        2  # Límite de 2 puntos
    )
    puntaje_idioma = min(
        EstudioIdioma.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        2  # Límite de 2 puntos
    )
    puntaje_publicaciones = min(
        PublicacionJuridica.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        3  # Límite de 3 puntos
    )
    puntaje_distincion = min(
        Distincion.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        3  # Límite de 3 puntos
    )
    puntaje_docencia = min(
        Docencia.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0,
        3  # Límite de 3 puntos
    )
    puntaje_demeritos = Demeritos.objects.filter(juez=juez).aggregate(total=Sum('puntaje'))['total'] or 0

    # Calcular el total general
    puntaje_total = (
        puntaje_antiguedad + puntaje_grado_academico + puntaje_estudios_magistratura +
        puntaje_estudios_doctorado + puntaje_estudios_maestria + puntaje_pasantia +
        puntaje_curso_especializacion + puntaje_certamen_academico + puntaje_evento_academico +
        puntaje_ofimatica + puntaje_idioma + puntaje_publicaciones + puntaje_distincion +
        puntaje_docencia - puntaje_demeritos  # se restan los deméritos
    )

    # Crear o actualizar el puntaje total
    puntaje_total_obj, created = PuntajeTotal.objects.update_or_create(
        juez=juez,
        defaults={
            'puntaje_antiguedad': puntaje_antiguedad,
            'puntaje_grado_academico': puntaje_grado_academico,
            'puntaje_estudios_magistratura': puntaje_estudios_magistratura,
            'puntaje_estudios_doctorado': puntaje_estudios_doctorado,
            'puntaje_estudios_maestria': puntaje_estudios_maestria,
            'puntaje_pasantia': puntaje_pasantia,
            'puntaje_curso_especializacion': puntaje_curso_especializacion,
            'puntaje_certamen_academico': puntaje_certamen_academico,
            'puntaje_evento_academico': puntaje_evento_academico,
            'puntaje_ofimatica': puntaje_ofimatica,
            'puntaje_idioma': puntaje_idioma,
            'puntaje_publicaciones': puntaje_publicaciones,
            'puntaje_distincion': puntaje_distincion,
            'puntaje_docencia': puntaje_docencia,
            'puntaje_demeritos': puntaje_demeritos,
            'puntaje_total': puntaje_total
        }
    )

    return puntaje_total_obj


modelos_actualizables = [
    Antiguedad, GradoAcademico, EstudiosMagistratura,
    EstudioDoctorado, EstudioMaestria, Pasantia, CursoEspecializacion,
    CertamenAcademico, EventoAcademico, EstudioOfimatica, EstudioIdioma,
    PublicacionJuridica, Distincion, Docencia, Demeritos
]

for modelo in modelos_actualizables:
    @receiver(post_save, sender=modelo)
    def actualizar_puntaje_post_save(sender, instance, **kwargs):
        calcular_puntaje_total(instance.juez.id_juez)

    @receiver(post_delete, sender=modelo)
    def actualizar_puntaje_post_delete(sender, instance, **kwargs):
        calcular_puntaje_total(instance.juez.id_juez)
