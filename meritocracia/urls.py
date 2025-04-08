from django.urls import path
from .views import admin_dashboard, admin_view, buscar_juez, juez_dashboard, login_view, registrar_certamen_academico, registrar_curso_especializacion, registrar_distincion, registrar_docencia, registrar_doctorado, registrar_estudio_idiomas, registrar_estudio_ofimatica, registrar_estudio_perfeccionamiento, registrar_evento_academico, registrar_juez,meritopj,registrar_antiguedad,registrar_grado_academico,registrar_estudios_magistratura, registrar_maestria, registrar_pasantia, registrar_publicacion_juridica

urlpatterns = [
    path('', meritopj),
    path('login/', login_view, name='login_view'),
    path('admin-view/', admin_view, name='admin_view'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('juez-dashboard/', juez_dashboard, name='juez_dashboard'),
    path("registrar_juez/", registrar_juez, name="registrar_juez"),
    path("registrar_antiguedad/", registrar_antiguedad, name="registrar_antiguedad"),
    path("registrar_grado_academico/", registrar_grado_academico, name="registrar_grado_academico"),
    path("registrar_estudios_magistratura/", registrar_estudios_magistratura, name="registrar_estudios_magistratura"),
    path('registrar_estudio_perfeccionamiento/', registrar_estudio_perfeccionamiento, name='registrar_estudio_perfeccionamiento'),
    path('registrar_estudio_perfeccionamiento/registrar_doctorado/', registrar_doctorado, name='registrar_doctorado'),
    path('registrar_estudio_perfeccionamiento/registrar_maestria/', registrar_maestria, name='registrar_maestria'),
    path('registrar_estudio_perfeccionamiento/registrar_pasantia/', registrar_pasantia, name='registrar_pasantia'),
    path('registrar_estudio_perfeccionamiento/registrar_curso_especializacion/', registrar_curso_especializacion, name='registrar_curso_especializacion'),
    path('registrar_estudio_perfeccionamiento/registrar_certamen_academico/', registrar_certamen_academico, name='registrar_certamen_academico'),
    path('registrar_estudio_perfeccionamiento/registrar_evento_academico/', registrar_evento_academico, name='registrar_evento_academico'),
    path('registrar_estudio_perfeccionamiento/registrar_estudio_ofimatica/', registrar_estudio_ofimatica, name='registrar_estudio_ofimatica'),
    path('registrar_estudio_perfeccionamiento/registrar_estudio_idiomas/', registrar_estudio_idiomas, name='registrar_estudio_idiomas'),
    path("registrar_publicacion_juridica/", registrar_publicacion_juridica, name="registrar_publicacion_juridica"),
    path("registrar_distincion/", registrar_distincion, name="registrar_distincion"),
    path("registrar_docencia/", registrar_docencia, name="registrar_docencia"),
    path('buscar_juez/', buscar_juez, name='buscar_juez')
]