from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CertamenAcademico, CursoEspecializacion, Demeritos, Distincion, Docencia, EstudioIdioma, EstudioMaestria, EstudioOfimatica, EstudioPerfeccionamiento, EventoAcademico, Juez, Antiguedad, GradoAcademico, EstudiosMagistratura, EstudioDoctorado, Pasantia, PublicacionJuridica, PuntajeTotal, Vigencia
from .models import (
    Antiguedad_valor_puntaje,
    GradoAcademico_valor_puntaje,
    Magistratura_valor_puntaje,
    Doctorado_valor_puntaje,
    Maestria_valor_puntaje,
    Pasantia_valor_puntaje,
    CursoEspecializacion_valor_puntaje,
    CertamenAcademico_valor_puntaje,
    EventoAcademico_valor_puntaje,
    Ofimatica_valor_puntaje,
    Idiomas_valor_puntaje,
    PublicacionJuridica_valor_puntaje,
    Distincion_valor_puntaje,
    Docencia_valor_puntaje
)

MODELOS_MAPA = {
    'antiguedad': Antiguedad_valor_puntaje,
    'grado_academico': GradoAcademico_valor_puntaje,
    'magistratura': Magistratura_valor_puntaje,
    'doctorado': Doctorado_valor_puntaje,
    'maestria': Maestria_valor_puntaje,
    'pasantia': Pasantia_valor_puntaje,
    'curso_especializacion': CursoEspecializacion_valor_puntaje,
    'certamen_academico': CertamenAcademico_valor_puntaje,
    'evento_academico': EventoAcademico_valor_puntaje,
    'ofimatica': Ofimatica_valor_puntaje,
    'idiomas': Idiomas_valor_puntaje,
    'publicacion_juridica': PublicacionJuridica_valor_puntaje,
    'distincion': Distincion_valor_puntaje,
    'docencia': Docencia_valor_puntaje,
}

from django.core.exceptions import ValidationError


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_view')
            elif hasattr(user, 'juez'):
                return redirect('juez_dashboard')
            else:
                return redirect('home')
        else:
            return render(request, "error.html")

    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect('login_view')


from django.utils.dateparse import parse_date
from django.contrib import messages  # Opcional para mostrar mensajes bonitos
from .models import Vigencia

@login_required
def crear_valores(request):
    if request.method == "POST":
        fecha_minima = request.POST.get("fechaminima")
        fecha_maxima = request.POST.get("fechamaxima")
        estado = request.POST.get("estado")

        if not fecha_minima or not fecha_maxima:
            return render(request, "error.html", {"mensaje": "Debes ingresar ambas fechas."})

        try:
            fecha_min = parse_date(fecha_minima)
            fecha_max = parse_date(fecha_maxima)

            if not fecha_min or not fecha_max:
                raise ValueError("Formato de fecha inválido.")

            if fecha_min > fecha_max:
                return render(request, "error.html", {"mensaje": "La fecha mínima no puede ser mayor a la fecha máxima."})

        except ValueError as e:
            return render(request, "error.html", {"mensaje": f"Error en las fechas: {str(e)}"})

        if estado not in ["Activo", "Inactivo"]:
            return render(request, "error.html", {"mensaje": "Estado no válido. Debe ser Activo o Inactivo."})

        Vigencia.objects.create(
            fecha_minima=fecha_min,
            fecha_maxima=fecha_max,
            estado=estado
        )

        return redirect('mostrar_valores')

    vigencias = Vigencia.objects.all().order_by('-idvigencia')
    return render(request, "editar_valores_formulacion.html", {"vigencia": vigencia, "vigencias": vigencias})

@login_required
def editar_valores(request, idvigencia):
    try:
        vigencia = Vigencia.objects.get(idvigencia=idvigencia)
    except Vigencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "La vigencia seleccionada no existe."})

    if request.method == "POST":
        fecha_minima = request.POST.get("fechaminima")
        fecha_maxima = request.POST.get("fechamaxima")
        estado = request.POST.get("estado")

        if not fecha_minima or not fecha_maxima:
            return render(request, "error.html", {"mensaje": "Debes ingresar ambas fechas."})

        try:
            fecha_min = parse_date(fecha_minima)
            fecha_max = parse_date(fecha_maxima)

            if not fecha_min or not fecha_max:
                raise ValueError("Formato de fecha inválido.")

            if fecha_min > fecha_max:
                return render(request, "error.html", {"mensaje": "La fecha mínima no puede ser mayor a la fecha máxima."})

        except ValueError as e:
            return render(request, "error.html", {"mensaje": f"Error en las fechas: {str(e)}"})

        if estado not in ["Activo", "Inactivo"]:
            return render(request, "error.html", {"mensaje": "Estado no válido. Debe ser Activo o Inactivo."})

        # Actualizar vigencia
        vigencia.fecha_minima = fecha_min
        vigencia.fecha_maxima = fecha_max
        vigencia.estado = estado
        vigencia.save()

        return redirect('mostrar_valores')

    vigencias = Vigencia.objects.all().order_by('-idvigencia')
    return render(request, "editar_valores_formulacion.html", {"vigencias": vigencias})



@login_required
def mostrar_valores(request):
    vigencias = Vigencia.objects.all().order_by('-idvigencia')  # opcional: ordenar por la más reciente
    return render(request, "editar_valores_formulacion.html", {"vigencias": vigencias})


@login_required
def juez_dashboard(request):
    if not hasattr(request.user, 'juez'):
        return redirect('login')
    return render(request, 'meritopj.html')


def meritopj(request):
    return render(request, 'meritopj.html')

def registrar_juez(request):

    if request.method == "POST":
        apellidos = request.POST.get("apellidos")
        nombres = request.POST.get("nombres")
        fecha_evaluacion = request.POST.get("fecha_evaluacion")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        orden = request.POST.get("orden")
        cargo = request.POST.get("cargo")

        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        try:
            # Crear usuario asociado
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=nombres,
                last_name=apellidos,
                email=email
            )

            # Crear juez vinculado al usuario
            Juez.objects.create(
                user=user,
                apellidos=apellidos,
                nombres=nombres,
                fecha_evaluacion=fecha_evaluacion,
                fecha_nacimiento=fecha_nacimiento,
                orden=orden,
                cargo=cargo
            )

            messages.success(request, "Juez y usuario registrados correctamente.")
            return redirect("/meritopj/admin-view")

        except Exception as e:
            messages.error(request, f"Error al registrar juez: {e}")
            return redirect("/meritopj/admin-view")
        
    jueces = Juez.objects.select_related('user').all()
    datos_jueces = [{
        'nombres': j.nombres,
        'apellidos': j.apellidos,
        'username': j.user.username
    } for j in jueces]

    return render(request, "form_registro_juez.html",{'jueces': datos_jueces})
    

from django.contrib.auth.decorators import login_required

@login_required
def registrar_antiguedad(request):

    try:
        valores_antiguedad = Antiguedad_valor_puntaje.objects.first()
    except Antiguedad_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})
    
    if request.method == "POST":
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        puntaje = float(request.POST.get("puntaje", 1))

        formato_fecha = "%Y-%m-%d"  
        inicio = datetime.strptime(fecha_inicio, formato_fecha)
        fin = datetime.strptime(fecha_fin, formato_fecha)
        años = fin.year - inicio.year

        if juez.cargo == 'Juez Superior':
            for i in range(1, años + 1):
                if i < 10:
                    puntaje += valores_antiguedad.js_puntaje_min
                else:
                    puntaje += valores_antiguedad.js_puntaje_max

        elif juez.cargo == 'Juez de Paz Letrado':
            for i in range(1, años + 1):
                if i < 2:
                    puntaje += valores_antiguedad.jpl_puntaje_min
                else:
                    puntaje += valores_antiguedad.jpl_puntaje_max

        elif juez.cargo == 'Juez Especializado':
            for i in range(1, años + 1):
                if i < 5:
                    puntaje += valores_antiguedad.je_puntaje_min
                else:
                    puntaje += valores_antiguedad.je_puntaje_max


        Antiguedad.objects.create(
            juez=juez,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin if fecha_fin else None,
            puntaje=float(puntaje)
        )

        return redirect('ver_mis_registros')

    return render(request, "form_antiguedad_juez.html")


@login_required
def registrar_grado_academico(request):

    try:
        valores_gradoacademico = GradoAcademico_valor_puntaje.objects.first()
    except GradoAcademico_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        titulo_gd = request.POST.get("titulo_gd")
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")
        documento = request.FILES.get("documento")

        # Calcular el puntaje según el tipo
        if tipo == 'DONJ':
            puntaje = valores_gradoacademico.donj_puntaje
        elif tipo == 'MAJ':
            puntaje = valores_gradoacademico.maj_puntaje
        elif tipo == 'MANJ':
            puntaje = valores_gradoacademico.manj_puntaje
        elif tipo == 'TINJ':
            puntaje = valores_gradoacademico.tinj_puntaje
        else:
            puntaje = 0

        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        GradoAcademico.objects.create(
            juez=juez,
            titulo_gd=titulo_gd,
            tipo=tipo,
            anio=int(anio),
            puntaje=puntaje,
            documento=documento_url
        )

        return redirect('ver_mis_registros')

    return render(request, "form_grado_academico_juez.html")


@login_required
def registrar_estudios_magistratura(request):

    try:
        valores_magistratura = Magistratura_valor_puntaje.objects.first()
    except Magistratura_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        programa = request.POST.get("programa")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get("documento")

        # Validar que la nota sea un número válido
        try:
            nota = float(nota)
        except (ValueError, TypeError):
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        # Asignar puntaje según la nota
        if 19 <= nota <= 20:
            puntaje = float(valores_magistratura.puntaje_alto)
        elif 17 <= nota <= 18:
            puntaje = float(valores_magistratura.puntaje_semialto)
        elif 15 <= nota <= 16:
            puntaje = float(valores_magistratura.puntaje_medio)
        elif 13 <= nota <= 14:
            puntaje = float(valores_magistratura.puntaje_bajo)
        else:
            puntaje = 0

        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        EstudiosMagistratura.objects.create(
            juez=juez,
            programa=programa,
            anio=int(anio),
            nota=nota,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect('ver_mis_registros')

    return render(request, "form_estudios_magistratura.html")

def registrar_estudio_perfeccionamiento(request):
    return render(request, "form_estudio_perfeccionamiento.html")


@login_required
def registrar_doctorado(request):
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    try:
        valores_doctorado = Doctorado_valor_puntaje.objects.first()
    except Doctorado_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se encontró la vigencia configurada."})
    
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get("documento")

        # Validar nota
        try:
            nota = float(nota)
        except (ValueError, TypeError):
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida."})
        
        # Validar año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_estudio_doctorado.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Verificar vigencia
        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year
        
        # Asignar puntaje (0 si no cumple vigencia)
        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"
        else:
            if nota < 15:
                puntaje = float(valores_doctorado.puntaje_bajo)
            elif 15 <= nota <= 18:
                puntaje = float(valores_doctorado.puntaje_medio)
            else:
                puntaje = float(valores_doctorado.puntaje_alto)
            mensaje_exito = "Registro exitoso"

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(
                id_estudioperfeccionamiento=estudio_perfeccionamiento_id
            )
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe."})

        # Subir archivo
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear el doctorado
        EstudioDoctorado.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=anio,
            nota=nota,
            puntaje=puntaje,
            documento=documento_url,
            estado="PENDIENTE",
            vigencia=vigencia
        )

        messages.success(request, mensaje_exito)  
        return redirect('ver_mis_registros')

    return render(request, "form_estudio_doctorado.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

@login_required
def registrar_maestria(request):

    try:
        valores_maestria = Maestria_valor_puntaje.objects.first()
    except Maestria_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()
    
    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se encontró la vigencia configurada."})
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get("documento")

        # Validación de nota
        try:
            nota = float(nota)
        except (ValueError, TypeError):
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida."})

 # Validar año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_estudio_doctorado.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Verificar vigencia
        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year
        
        # Asignar puntaje (0 si no cumple vigencia)
        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"

        # Asignación de puntaje
        if nota < 15:
            puntaje = float(valores_maestria.puntaje_bajo)
        elif 15 <= nota <= 18:
            puntaje = float(valores_maestria.puntaje_medio)
        else:
            puntaje = float(valores_maestria.puntaje_alto)

        # Obtener estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe."})

        # Guardar archivo
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear el registro de maestría
        EstudioMaestria.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=anio,
            nota=nota,
            puntaje=puntaje,
            documento=documento_url,
            estado="PENDIENTE",
            vigencia=vigencia
        )

        return redirect('ver_mis_registros')

    return render(request, "form_estudio_maestria.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import EstudioPerfeccionamiento, Pasantia, Pasantia_valor_puntaje, Vigencia, Juez

@login_required
def registrar_pasantia(request):
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    try:
        valores_pasantia = Pasantia_valor_puntaje.objects.first()
    except Pasantia_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    
    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se encontró la vigencia configurada."})
    
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")  
        nombre = request.POST.get("nombre")  
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")  
        nota = request.POST.get("nota")  
        documento = request.FILES.get('documento') 

        # Validación de nota
        try:
            nota = float(nota)
        except (ValueError, TypeError):
            return render(request, "form_pasantia_puntaje.html", {
                "error_modal": "La nota ingresada no es válida.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })
    
        # Validación de año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_pasantia_puntaje.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Verificar vigencia
        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year
        
        # Puntaje por tipo de pasantía (0 si no cumple vigencia)
        tipo = tipo.capitalize()
        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"
        else:
            if tipo == 'Nacional':
                puntaje = float(valores_pasantia.puntaje_bajo)
            elif tipo == 'Internacional':
                puntaje = float(valores_pasantia.puntaje_alto)
            else:
                puntaje = 0.0  # Tipo inválido
            mensaje_exito = "Registro exitoso"

        # Verificar existencia de estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(
                id_estudioperfeccionamiento=estudio_perfeccionamiento_id
            )
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "form_pasantia_puntaje.html", {
                "error_modal": "El estudio de perfeccionamiento no existe.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Guardar archivo si existe
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear registro de pasantía
        Pasantia.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            tipo=tipo,
            anio=anio,
            nota=nota,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            vigencia=vigencia
        )

        messages.success(request, mensaje_exito)
        return redirect('ver_mis_registros')

    return render(request, "form_pasantia_puntaje.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

@login_required 
def registrar_curso_especializacion(request):

    try:
        valores_especializacion = CursoEspecializacion_valor_puntaje.objects.first()
    except CursoEspecializacion_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "form_especializacion.html", {"error_modal": "No se encontró la vigencia configurada."})

    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "form_especializacion.html", {"error_modal": "Este usuario no está asociado a un juez."})

    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento") 
        nombre = request.POST.get("nombre")  
        horas = request.POST.get("horas")  
        anio = request.POST.get("anio")  
        documento = request.FILES.get('documento')

        # Validación de horas
        try:
            horas = int(horas)
            if horas <= 0:
                raise ValueError
        except ValueError:
            return render(request, "form_especializacion.html", {
                "error_modal": "Las horas ingresadas no son válidas (debe ser un número positivo).",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Validación de año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_especializacion.html", {
                "error_modal": "El año ingresado no es válido.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Verificar vigencia
        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year
        
        # Calcular puntaje (0 si no cumple vigencia)
        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"
        else:
            if horas > 200:
                puntaje = float(valores_especializacion.puntaje_alto)
            elif horas >= 101:
                puntaje = float(valores_especializacion.puntaje_medio)
            elif horas >= 50:
                puntaje = float(valores_especializacion.puntaje_bajo)
            else:
                puntaje = 0.0
            mensaje_exito = "Registro exitoso"

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(
                id_estudioperfeccionamiento=estudio_perfeccionamiento_id
            )
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "form_especializacion.html", {
                "error_modal": "El estudio de perfeccionamiento no existe.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Guardar archivo
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear registro
        CursoEspecializacion.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            horas=horas,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            vigencia=vigencia
        )

        messages.success(request, mensaje_exito)
        return redirect('ver_mis_registros')

    return render(request, "form_especializacion.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento,
        "vigencia": vigencia  # Pasamos vigencia al template para usar en JavaScript
    })

@login_required
def registrar_certamen_academico(request):

    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    try:
        valores_certamen = CertamenAcademico_valor_puntaje.objects.first()
    except CertamenAcademico_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "form_certamen_academico.html", {
            "error_modal": "No se encontró la vigencia configurada.",
            "estudios_perfeccionamiento": estudios_perfeccionamiento
        })
    
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "form_certamen_academico.html", {
            "error_modal": "Este usuario no está asociado a un juez.",
            "estudios_perfeccionamiento": estudios_perfeccionamiento
        })

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        tipo_participacion = request.POST.get("tipo_participacion")
        nombre = request.POST.get("nombre")
        tipo = request.POST.get("tipo")  # Nacional o Internacional
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')

        # Validar año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_certamen_academico.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Verificar vigencia
        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year
        
        # Calcular puntaje (0 si no cumple vigencia)
        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"
        else:
            if tipo == 'Nacional':
                puntaje = float(valores_certamen.puntaje_alto)
            elif tipo == 'Internacional':
                puntaje = float(valores_certamen.puntaje_bajo)
            else:
                puntaje = 0.0
            mensaje_exito = "Registro exitoso"

        # Validar estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(
                id_estudioperfeccionamiento=estudio_perfeccionamiento_id
            )
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "form_certamen_academico.html", {
                "error_modal": "El estudio de perfeccionamiento no existe.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Guardar archivo si fue subido
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear y guardar el registro del certamen académico
        CertamenAcademico.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            tipo_participacion=tipo_participacion,
            nombre=nombre,
            tipo=tipo,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            vigencia=vigencia
        )

        messages.success(request, mensaje_exito)
        return redirect('ver_mis_registros')

    return render(request, "form_certamen_academico.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento,
        "vigencia": vigencia  # Pasamos vigencia al template
    })

@login_required
def registrar_evento_academico(request):
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    try:
        valores_evento = EventoAcademico_valor_puntaje.objects.first()
    except EventoAcademico_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    
    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "form_evento_academico.html", {
            "error_modal": "No se encontró la vigencia configurada.",
            "estudios_perfeccionamiento": estudios_perfeccionamiento
        })
    
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "form_evento_academico.html", {
            "error_modal": "Este usuario no está asociado a un juez.",
            "estudios_perfeccionamiento": estudios_perfeccionamiento
        })

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')

        # Validar año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_evento_academico.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year

        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"
        else:
            puntaje = float(valores_evento.puntaje)
            mensaje_exito = "Registro exitoso"

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(
                id_estudioperfeccionamiento=estudio_perfeccionamiento_id
            )
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "form_evento_academico.html", {
                "error_modal": "El estudio de perfeccionamiento no existe.",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        EventoAcademico.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            vigencia=vigencia
        )

        messages.success(request, mensaje_exito)
        return redirect("form_evento_academico")  # Asegúrate de que el nombre de la URL esté definido en urls.py

    return render(request, "form_evento_academico.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento,
        "vigencia": vigencia
    })


@login_required
def registrar_estudio_ofimatica(request):

    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    try:
        valores_ofimatica = Ofimatica_valor_puntaje.objects.first()
    except Ofimatica_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    
    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se encontró la vigencia configurada."})
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener el archivo si se sube

        # Asignar puntaje según el nivel
        puntaje_dict = {
            "Básico": float(valores_ofimatica.puntaje_basico),
            "Intermedio": float(valores_ofimatica.puntaje_intermedio),
            "Avanzado": float(valores_ofimatica.puntaje_avanzado)
        }
        puntaje = puntaje_dict.get(nivel, 0)  # Por defecto 0 si nivel no está definido

        # Validar estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe."})

        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_estudio_ofimatica.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": EstudioPerfeccionamiento.objects.all()
            })
        
        if not (vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year):
            return render(request, "form_estudio_ofimatica.html", {
                "error_modal": f"El año {anio} no está dentro del rango de la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year}).",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })
        
        # Guardar archivo si fue subido
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear y guardar el estudio de ofimática
        EstudioOfimatica.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nivel=nivel,
            estudio=nombre_estudio,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            idvigencia=vigencia
        )

        return redirect('ver_mis_registros')

    return render(request, "form_estudio_ofimatica.html", {
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def registrar_estudio_idiomas(request):

    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    try:
        valores_idiomas = Idiomas_valor_puntaje.objects.first()
    except Idiomas_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
        
    try:
        vigencia = Vigencia.objects.get(idvigencia=1)
    except Vigencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se encontró la vigencia configurada."})
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})
    
    if request.method == "POST":
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener el archivo si se sube

        # Asignar puntaje según el nivel
        puntaje_dict = {
            "Básico": float(valores_idiomas.puntaje_basico),
            "Intermedio": float(valores_idiomas.puntaje_intermedio),
            "Avanzado": float(valores_idiomas.puntaje_avanzado)
        }
        puntaje = puntaje_dict.get(nivel, 0)  # Por defecto 0 si nivel no está definido

        # Obtener el estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_estudio_idiomas.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido.",
                "estudios_perfeccionamiento": EstudioPerfeccionamiento.objects.all()
            })
        
        if not (vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year):
            return render(request, "form_estudio_idiomas.html", {
                "error_modal": f"El año {anio} no está dentro del rango de la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year}).",
                "estudios_perfeccionamiento": estudios_perfeccionamiento
            })

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar el estudio de idiomas
        EstudioIdioma.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nivel=nivel,
            estudio=nombre_estudio,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            idvigencia=vigencia
        )

        return redirect('ver_mis_registros')

    jueces = Juez.objects.all()

    return render(request, "form_estudio_idiomas.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })


@login_required
def registrar_publicacion_juridica(request):

    try:
        valores_publicacion = PublicacionJuridica_valor_puntaje.objects.first()
    except PublicacionJuridica_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        nombre = request.POST.get("nombre")
        documento = request.FILES.get('documento')  # Obtener archivo PDF

        # Definir puntajes según el tipo de publicación
        puntajes = {
            "LIBRO": float(valores_publicacion.puntaje_libro),
            "REVISTA": float(valores_publicacion.puntaje_revista),
            "MERITO": float(valores_publicacion.puntaje_merito)
        }
        
        puntaje = puntajes.get(tipo, 0)  # Valor predeterminado de 0 si el tipo no es válido

        # Guardar el archivo si se sube
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear y guardar la publicación jurídica
        PublicacionJuridica.objects.create(
            juez=juez,
            tipo=tipo,
            nombre=nombre,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect('ver_mis_registros')  

    return render(request, "form_publicacion_juridica.html")

@login_required
def registrar_distincion(request):

    try:
        valores_distincion = Distincion_valor_puntaje.objects.first()
    except Distincion_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener archivo PDF si se sube
        puntaje = valores_distincion.puntaje

        # Guardar el archivo si se sube
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear y guardar la distinción
        Distincion.objects.create(
            juez=juez,
            nombre=nombre,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect('ver_mis_registros')  

    return render(request, "form_distincion.html")

@login_required
def registrar_docencia(request):

    try:
        valores_docencia = Docencia_valor_puntaje.objects.first()
    except Docencia_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})

    try:
        vigencia = Vigencia.objects.get(idvigencia=2)
    except Vigencia.DoesNotExist:
        return render(request, "form_docencia.html", {
            "error_modal": "No se encontró la vigencia configurada."
        })
    
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "form_docencia.html", {
            "error_modal": "Este usuario no está asociado a un juez."
        })

    if request.method == "POST":
        curso = request.POST.get("curso")
        universidad = request.POST.get("universidad")
        anio = request.POST.get("anio")
        horas = request.POST.get("horas")
        documento = request.FILES.get('documento')

        # Validar horas
        try:
            horas = int(horas)
            if horas <= 0:
                raise ValueError
        except ValueError:
            return render(request, "form_docencia.html", {
                "error_modal": "Las horas deben ser un número entero positivo."
            })

        # Validar año
        try:
            anio = int(anio)
        except ValueError:
            return render(request, "form_docencia.html", {
                "error_modal": f"El año ingresado '{anio}' no es válido."
            })

        # Verificar vigencia
        cumple_vigencia = vigencia.fecha_minima.year <= anio <= vigencia.fecha_maxima.year
        
        # Calcular puntaje (0 si no cumple vigencia)
        if not cumple_vigencia:
            puntaje = 0.0
            mensaje_exito = f"Registro no contabilizable: no cumple con la vigencia ({vigencia.fecha_minima.year} - {vigencia.fecha_maxima.year})"
        else:
            puntaje = horas * valores_docencia.puntaje
            mensaje_exito = "Registro exitoso"

        # Guardar archivo
        documento_url = None
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear registro
        Docencia.objects.create(
            juez=juez,
            curso=curso,
            universidad=universidad,
            anio=anio,
            horas=horas,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE',
            vigencia=vigencia
        )

        return render(request, "form_docencia.html", {
            "exito_modal": mensaje_exito,
            "vigencia": vigencia  # Pasamos vigencia al template
        })

    return render(request, "form_docencia.html", {
        "vigencia": vigencia  # Pasamos vigencia al template
    })


def registrar_demerito(request):

    if request.method == "POST":
        id_juez = request.POST.get("id_juez")
        tipo = request.POST.get("tipo")
        puntaje = request.POST.get("puntaje")

        try:
            juez = Juez.objects.get(id_juez=id_juez)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe."})

        try:
            puntaje = float(puntaje)
        except ValueError:
            return render(request, "error.html", {"mensaje": "El puntaje debe ser un número válido."})

        Demeritos.objects.create(
            juez=juez,
            tipo=tipo,
            puntaje=puntaje,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/admin-view/")

    jueces = Juez.objects.all()
    return render(request, "form_demerito.html", {"jueces": jueces})


def obtener_registros_por_juez(id_juez):
    try:
        juez = Juez.objects.get(id_juez=id_juez)
    except Juez.DoesNotExist:
        return {'error': 'Juez no encontrado'}

    registros = {
        'juez': juez,
        'antiguedad': list(Antiguedad.objects.filter(juez=juez)),
        'grado_academico': list(GradoAcademico.objects.filter(juez=juez)),
        'estudios_magistratura': list(EstudiosMagistratura.objects.filter(juez=juez)),
        'doctorados': list(EstudioDoctorado.objects.filter(juez=juez)),
        'maestrias': list(EstudioMaestria.objects.filter(juez=juez)),
        'pasantias': list(Pasantia.objects.filter(juez=juez)),
        'cursos_especializacion': list(CursoEspecializacion.objects.filter(juez=juez)),
        'certamenes_academicos': list(CertamenAcademico.objects.filter(juez=juez)),
        'eventos_academicos': list(EventoAcademico.objects.filter(juez=juez)),
        'ofimatica': list(EstudioOfimatica.objects.filter(juez=juez)),
        'idiomas': list(EstudioIdioma.objects.filter(juez=juez)),
        'publicaciones': list(PublicacionJuridica.objects.filter(juez=juez)),
        'distinciones': list(Distincion.objects.filter(juez=juez)),
        'docencia': list(Docencia.objects.filter(juez=juez)),
        'demeritos': list(Demeritos.objects.filter(juez=juez)),
        'puntaje_total': PuntajeTotal.objects.filter(juez=juez).first()
    }

    return registros

def obtener_registros_por_usuario(juez):
    registros = {
        'juez': juez,
        'antiguedad': Antiguedad.objects.filter(juez=juez),
        'grado_academico': GradoAcademico.objects.filter(juez=juez),
        'estudios_magistratura': EstudiosMagistratura.objects.filter(juez=juez),
        'doctorados': EstudioDoctorado.objects.filter(juez=juez),
        'maestrias': EstudioMaestria.objects.filter(juez=juez),
        'pasantias': Pasantia.objects.filter(juez=juez),
        'cursos_especializacion': CursoEspecializacion.objects.filter(juez=juez),
        'certamenes_academicos': CertamenAcademico.objects.filter(juez=juez),
        'eventos_academicos': EventoAcademico.objects.filter(juez=juez),
        'ofimatica': EstudioOfimatica.objects.filter(juez=juez),
        'idiomas': EstudioIdioma.objects.filter(juez=juez),
        'publicaciones': PublicacionJuridica.objects.filter(juez=juez),
        'distinciones': Distincion.objects.filter(juez=juez),
        'docencia': Docencia.objects.filter(juez=juez),
        'demeritos': Demeritos.objects.filter(juez=juez),
        'puntaje_total': PuntajeTotal.objects.filter(juez=juez).first()
    }
    return registros

@login_required
def ver_mis_registros(request):
    try:
        juez = request.user.juez
    except Juez.DoesNotExist:
        return render(request, "error.html", {"mensaje": "Este usuario no está asociado a un juez."})

    registros = obtener_registros_por_usuario(juez)
    return render(request, 'view_monitoreo_juez.html', {'registros': registros})


def buscar_juez(request):
    jueces = Juez.objects.all() 

    if request.method == 'POST':
        juez_id = request.POST.get('juez_id')

        datos = obtener_registros_por_juez(juez_id)
        
        if 'error' in datos:
            return render(request, 'admin_mostrar_registros.html', {'error': datos['error'], 'jueces': jueces})
        return render(request, 'admin_mostrar_registros.html', {'datos': datos, 'jueces': jueces})

    return render(request, 'admin_mostrar_registros.html', {'jueces': jueces})


def obtener_jueces_ordenados():
    jueces = Juez.objects.all()
    jueces_con_puntaje = []

    for juez in jueces:
        puntaje = PuntajeTotal.objects.filter(juez=juez).first()
        if puntaje:
            juez_data = {
                'juez': juez,
                'puntaje_total': puntaje.puntaje_total,
                'puntaje_antiguedad': puntaje.puntaje_antiguedad,
                'puntaje_grado_academico': puntaje.puntaje_grado_academico,
                'puntaje_estudios_magistratura': puntaje.puntaje_estudios_magistratura,
                'puntaje_estudios_doctorado': puntaje.puntaje_estudios_doctorado,
                'puntaje_estudios_maestria': puntaje.puntaje_estudios_maestria,
                'puntaje_pasantia': puntaje.puntaje_pasantia,
                'puntaje_curso_especializacion': puntaje.puntaje_curso_especializacion,
                'puntaje_certamen_academico': puntaje.puntaje_certamen_academico,
                'puntaje_evento_academico': puntaje.puntaje_evento_academico,
                'puntaje_ofimatica': puntaje.puntaje_ofimatica,
                'puntaje_idioma': puntaje.puntaje_idioma,
                'puntaje_publicaciones': puntaje.puntaje_publicaciones,
                'puntaje_distincion': puntaje.puntaje_distincion,
                'puntaje_docencia': puntaje.puntaje_docencia,
                'puntaje_demeritos': puntaje.puntaje_demeritos,
            }
        else:
            juez_data = {
                'juez': juez,
                'puntaje_total': 0,
                'puntaje_antiguedad': 0,
                'puntaje_grado_academico': 0,
                'puntaje_estudios_magistratura': 0,
                'puntaje_estudios_doctorado': 0,
                'puntaje_estudios_maestria': 0,
                'puntaje_pasantia': 0,
                'puntaje_curso_especializacion': 0,
                'puntaje_certamen_academico': 0,
                'puntaje_evento_academico': 0,
                'puntaje_ofimatica': 0,
                'puntaje_idioma': 0,
                'puntaje_publicaciones': 0,
                'puntaje_distincion': 0,
                'puntaje_docencia': 0,
                'puntaje_demeritos': 0,
            }

        # Suma para CASO 1 (sin incluir total ni antigüedad)
        juez_data['puntaje_desempate'] = (
            juez_data['puntaje_grado_academico'] +
            juez_data['puntaje_estudios_magistratura'] +
            juez_data['puntaje_estudios_doctorado'] +
            juez_data['puntaje_estudios_maestria'] +
            juez_data['puntaje_pasantia'] +
            juez_data['puntaje_curso_especializacion'] +
            juez_data['puntaje_certamen_academico'] +
            juez_data['puntaje_evento_academico'] +
            juez_data['puntaje_ofimatica'] +
            juez_data['puntaje_idioma'] +
            juez_data['puntaje_publicaciones'] +
            juez_data['puntaje_distincion'] +
            juez_data['puntaje_docencia'] +
            juez_data['puntaje_demeritos']
        )

        jueces_con_puntaje.append(juez_data)

    
    jueces_ordenados = sorted(
        jueces_con_puntaje,
        key=lambda x: (
            -x['puntaje_total'],                      # 1. Mayor puntaje total
            -x['puntaje_desempate'],                  # 2. Mayor puntaje sumado (CASO 1)
            x['puntaje_demeritos'],                   # 3. Menor demeritos (CASO 2)
            -x['puntaje_antiguedad'],                 
        )
    )

    return jueces_ordenados



def contar_jueces(request):
    cantidad_jueces = Juez.objects.count()
    context = {
        'cantidad_jueces': cantidad_jueces,
    }
    return render(request, 'admin_main.html', context)

def top_jueces(request):
    jueces = obtener_jueces_ordenados() 
    return render(request, 'admin_main.html', {'jueces_top': jueces})


@login_required
def admin_view(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    jueces_top = obtener_jueces_ordenados()
    cantidad_jueces = Juez.objects.count()
    
    return render(request, 'prueba_admin.html', {
        'jueces_top': jueces_top,
        'cantidad_jueces': cantidad_jueces
    })


#AQUI VIENEN TODOS LAS FUNCIONES DE EDICION DE DATOS

def editar_grado_academico(request, id_gradoacademico):
    grado = get_object_or_404(GradoAcademico, id_gradoacademico=id_gradoacademico)
    jueces = Juez.objects.all()

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        titulo_gd = request.POST.get("titulo_gd")
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Obtener nuevo juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = GradoAcademico_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para el grado académico")

            # Obtener puntaje según tipo
            if tipo == 'DOJ':
                puntaje = float(valores.doj_puntaje)
            elif tipo == 'DONJ':
                puntaje = float(valores.donj_puntaje)
            elif tipo == 'MAJ':
                puntaje = float(valores.maj_puntaje)
            elif tipo == 'MANJ':
                puntaje = float(valores.manj_puntaje)
            elif tipo == 'TINJ':
                puntaje = float(valores.tinj_puntaje)
            else:
                puntaje = 0
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        # Actualizar los campos
        grado.juez = juez
        grado.titulo_gd = titulo_gd
        grado.tipo = tipo
        grado.anio = int(anio)
        grado.puntaje = puntaje
        grado.estado = estado

        # Si se subió nuevo documento, reemplazar el anterior
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            grado.documento = fs.url(filename)

        grado.save()

        return redirect("/meritopj/admin-view/")

    return render(request, "form_editar/form_editar_grado_academico.html", {
        "grado": grado,
        "jueces": jueces
    })

def editar_estudios_magistratura(request, id_estudiomagistratura):
    estudio = get_object_or_404(EstudiosMagistratura, id_estudiomagistratura=id_estudiomagistratura)
    jueces = Juez.objects.all()

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        programa = request.POST.get("programa")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Validar juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Validar nota
        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = Magistratura_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para la magistratura")

            # Calcular puntaje según nota y valores configurados
            if 19 <= nota <= 20:
                puntaje = float(valores.puntaje_alto)
            elif 17 <= nota <= 18:
                puntaje = float(valores.puntaje_semialto)
            elif 15 <= nota <= 16:
                puntaje = float(valores.puntaje_medio)
            elif 13 <= nota <= 14:
                puntaje = float(valores.puntaje_bajo)
            else:
                puntaje = 0
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        # Actualizar campos
        estudio.juez = juez
        estudio.programa = programa
        estudio.anio = int(anio)
        estudio.nota = nota
        estudio.puntaje = puntaje
        estudio.estado = estado

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            estudio.documento = fs.url(filename)

        estudio.save()
        return redirect("/meritopj/admin-view/")

    return render(request, "form_editar/editar_estudios_magistratura.html", {
        "estudio": estudio,
        "jueces": jueces
    })

def editar_doctorado(request, id_estudiodoctorado):
    doctorado = get_object_or_404(EstudioDoctorado, id_estudiodoctorado=id_estudiodoctorado)
    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get("documento")
        estado = request.POST.get("estado")

        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = Doctorado_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para el doctorado")

            # Calcular puntaje según nota y valores configurados
            if nota < 15:
                puntaje = valores.puntaje_bajo
            elif 15 <= nota <= 18:
                puntaje = valores.puntaje_medio
            else:
                puntaje = valores.puntaje_alto
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        doctorado.juez = juez
        doctorado.id_estudioperfeccionamiento = estudio_perfeccionamiento
        doctorado.nombre = nombre
        doctorado.anio = int(anio)
        doctorado.nota = nota
        doctorado.puntaje = puntaje
        doctorado.estado = estado

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            doctorado.documento = fs.url(filename)

        doctorado.save()
        return redirect("/meritopj/")

    return render(request, "form_editar/editar_estudio_doctorado.html", {
        'doctorado': doctorado,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })


def editar_maestria(request, id_estudiomaestria):
    estudio = get_object_or_404(EstudioMaestria, id_estudiomaestria=id_estudiomaestria)
    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get("documento")
        estado = request.POST.get("estado")

        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = Maestria_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para la maestría")

            # Calcular puntaje según nota y valores configurados
            if nota < 15:
                puntaje = valores.puntaje_bajo
            elif 15 <= nota <= 18:
                puntaje = valores.puntaje_medio
            else:
                puntaje = valores.puntaje_alto
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        estudio.juez = juez
        estudio.id_estudioperfeccionamiento = estudio_perfeccionamiento
        estudio.nombre = nombre
        estudio.anio = int(anio)
        estudio.nota = nota
        estudio.puntaje = puntaje
        estudio.estado = estado

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            estudio.documento = fs.url(filename)

        estudio.save()
        return redirect("/meritopj/")

    return render(request, "form_editar/editar_estudio_maestria.html", {
        "estudio": estudio,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_pasantia(request, id_pasantia):
    pasantia = get_object_or_404(Pasantia, id_pasantia=id_pasantia)

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = Pasantia_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para la pasantía")

            # Calcular puntaje según tipo y valores configurados
            if tipo == 'Nacional':
                puntaje = valores.puntaje_bajo
            elif tipo == 'Internacional':
                puntaje = valores.puntaje_alto
            else:
                puntaje = 0
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            pasantia.documento = fs.url(filename)

        # Actualizar campos
        pasantia.juez = juez
        pasantia.id_estudioperfeccionamiento = estudio_perfeccionamiento
        pasantia.nombre = nombre
        pasantia.tipo = tipo
        pasantia.anio = int(anio)
        pasantia.nota = float(nota)
        pasantia.puntaje = puntaje
        pasantia.estado = estado
        pasantia.save()

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_editar/editar_estudio_pasantia.html", {
        "pasantia": pasantia,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_curso_especializacion(request, id_curso):
    curso = get_object_or_404(CursoEspecializacion, id_cursoespecializacion=id_curso)

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        horas = request.POST.get("horas")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        try:
            horas = int(horas)
        except ValueError:
            return render(request, "error.html", {"mensaje": "Las horas ingresadas no son válidas"})

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = CursoEspecializacion_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para el curso de especialización")

            # Calcular puntaje según horas y valores configurados
            if horas > 200:
                puntaje = valores.puntaje_alto
            elif 101 <= horas <= 200:
                puntaje = valores.puntaje_medio
            elif 50 <= horas <= 100:
                puntaje = valores.puntaje_bajo
            else:
                puntaje = 0
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            curso.documento = fs.url(filename)

        # Actualizar campos
        curso.juez = juez
        curso.id_estudioperfeccionamiento = estudio_perfeccionamiento
        curso.nombre = nombre
        curso.horas = horas
        curso.anio = int(anio)
        curso.puntaje = puntaje
        curso.estado = estado
        curso.save()

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_editar/editar_estudio_especializacion.html", {
        "curso": curso,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_certamen_academico(request, id):
    certamen = get_object_or_404(CertamenAcademico, id_certamenacademico=id)
    try:
        valores_certamen = CertamenAcademico_valor_puntaje.objects.first()
    except CertamenAcademico_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de antigüedad."})
    
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        tipo_participacion = request.POST.get("tipo_participacion")
        nombre = request.POST.get("nombre")
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Calcular puntaje
        if tipo == 'Nacional':
            puntaje = valores_certamen.puntaje_bajo
        elif tipo == 'Internacional':
            puntaje = valores_certamen.puntaje_alto
        else:
            puntaje = 0

        try:
            juez = Juez.objects.get(id_juez=juez_id)
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except (Juez.DoesNotExist, EstudioPerfeccionamiento.DoesNotExist):
            return render(request, "error.html", {"mensaje": "El juez o estudio de perfeccionamiento no existe"})


        certamen.juez = juez
        certamen.id_estudioperfeccionamiento = estudio_perfeccionamiento
        certamen.tipo_participacion = tipo_participacion
        certamen.nombre = nombre
        certamen.tipo = tipo
        certamen.anio = int(anio)
        certamen.puntaje = puntaje
        certamen.estado = estado

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            certamen.documento = fs.url(filename)

        certamen.save()

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_editar/editar_estudio_certamen.html", {
        "certamen": certamen,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_evento_academico(request, id):
    evento = get_object_or_404(EventoAcademico, id_eventoacademico=id)

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Obtener el valor de puntaje desde el modelo
        try:
            valor = EventoAcademico_valor_puntaje.objects.first()
            if not valor:
                raise ValueError("No se han configurado los valores de puntaje para el evento académico")

            puntaje = valor.puntaje
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        try:
            juez = Juez.objects.get(id_juez=juez_id)
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except (Juez.DoesNotExist, EstudioPerfeccionamiento.DoesNotExist):
            return render(request, "error.html", {"mensaje": "El juez o estudio de perfeccionamiento no existe"})

        evento.juez = juez
        evento.id_estudioperfeccionamiento = estudio_perfeccionamiento
        evento.nombre = nombre
        evento.anio = int(anio)
        evento.puntaje = puntaje
        evento.estado = estado

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            evento.documento = fs.url(filename)

        evento.save()

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_editar/editar_estudio_evento.html", {
        "evento": evento,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_estudio_ofimatica(request, id_ofimatica):
    estudio = get_object_or_404(EstudioOfimatica, id_ofimatica=id_ofimatica)

    try:
        valores_ofimatica = Ofimatica_valor_puntaje.objects.first()
    except Ofimatica_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de ofimatica."})
    
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        puntaje_dict = {
            "Básico": valores_ofimatica.puntaje_basico,
            "Intermedio": valores_ofimatica.puntaje_intermedio,
            "Avanzado": valores_ofimatica.puntaje_avanzado
        }
        puntaje = puntaje_dict.get(nivel, 0)

        try:
            juez = Juez.objects.get(id_juez=juez_id)
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except (Juez.DoesNotExist, EstudioPerfeccionamiento.DoesNotExist):
            return render(request, "error.html", {"mensaje": "Datos no válidos"})

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            estudio.documento = fs.url(filename)

        estudio.juez = juez
        estudio.id_estudioperfeccionamiento = estudio_perfeccionamiento
        estudio.nivel = nivel
        estudio.estudio = nombre_estudio
        estudio.anio = int(anio)
        estudio.puntaje = puntaje
        estudio.estado = estado
        estudio.save()

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_editar/editar_estudio_ofimatica.html", {
        "estudio": estudio,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_estudio_idiomas(request, id_idioma):
    estudio = get_object_or_404(EstudioIdioma, id_idioma=id_idioma)

    try:
        valores_idiomas = Idiomas_valor_puntaje.objects.first()
    except Idiomas_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de ofimatica."})
    
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        puntaje_dict = {
            "Básico": valores_idiomas.puntaje_basico,
            "Intermedio": valores_idiomas.puntaje_intermedio,
            "Avanzado": valores_idiomas.puntaje_avanzado
        }
        puntaje = puntaje_dict.get(nivel, 0)

        try:
            juez = Juez.objects.get(id_juez=juez_id)
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except (Juez.DoesNotExist, EstudioPerfeccionamiento.DoesNotExist):
            return render(request, "error.html", {"mensaje": "Datos no válidos"})

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            estudio.documento = fs.url(filename)

        estudio.juez = juez
        estudio.id_estudioperfeccionamiento = estudio_perfeccionamiento
        estudio.nivel = nivel
        estudio.estudio = nombre_estudio
        estudio.anio = int(anio)
        estudio.puntaje = puntaje
        estudio.estado = estado
        estudio.save()

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_editar/editar_estudio_idiomas.html", {
        "estudio": estudio,
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def editar_publicacion_juridica(request, id_publicacionjuridica):
    publicacion = get_object_or_404(PublicacionJuridica, id_publicacionjuridica=id_publicacionjuridica)

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        tipo = request.POST.get("tipo")
        nombre = request.POST.get("nombre")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Obtener los valores de puntaje desde el modelo
        try:
            valores = PublicacionJuridica_valor_puntaje.objects.first()
            if not valores:
                raise ValueError("No se han configurado los valores de puntaje para la publicación jurídica")

            # Calcular puntaje según tipo y valores configurados
            if tipo == 'LIBRO':
                puntaje = valores.puntaje_libro
            elif tipo == 'REVISTA':
                puntaje = valores.puntaje_revista
            elif tipo == 'MERITO':
                puntaje = valores.puntaje_merito
            else:
                puntaje = 0
        except Exception as e:
            return render(request, "error.html", {"mensaje": f"Error al obtener los valores de puntaje: {str(e)}"})

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            publicacion.documento = fs.url(filename)

        publicacion.juez = juez
        publicacion.tipo = tipo
        publicacion.nombre = nombre
        publicacion.puntaje = puntaje
        publicacion.estado = estado
        publicacion.save()

        return redirect("/meritopj/registrar_publicacion_juridica")

    jueces = Juez.objects.all()

    return render(request, "form_editar/editar_publicacion.html", {
        "publicacion": publicacion,
        "jueces": jueces
    })

def editar_distincion(request, id_distincion):

    try:
        valores_distincion = Distincion_valor_puntaje.objects.first()
    except Distincion_valor_puntaje.DoesNotExist:
        return render(request, "error.html", {"mensaje": "No se han definido los valores de ofimatica."})
    
    try:
        distincion = Distincion.objects.get(id_distincion=id_distincion)
    except Distincion.DoesNotExist:
        return render(request, "error.html", {"mensaje": "La distinción no existe"})

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Validar juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Guardar el nuevo documento si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
            distincion.documento = documento_url

        # Actualizar campos
        distincion.juez = juez
        distincion.nombre = nombre
        distincion.anio = anio
        distincion.puntaje = valores_distincion.puntaje
        distincion.estado = estado
        distincion.save()

        return redirect("/meritopj/registrar_distincion")

    jueces = Juez.objects.all()
    return render(request, "form_editar/editar_distincion.html", {
        "jueces": jueces,
        "distincion": distincion
    })


def editar_docencia(request, id_docencia):
    try:
        docencia = Docencia.objects.get(id_docencia=id_docencia)
    except Docencia.DoesNotExist:
        return render(request, "error.html", {"mensaje": "La docencia no existe"})

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        curso = request.POST.get("curso")
        universidad = request.POST.get("universidad")
        anio = request.POST.get("anio")
        horas = request.POST.get("horas")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        # Validar horas
        try:
            horas = int(horas)
            puntaje = horas * 0.375
        except ValueError:
            return render(request, "error.html", {"mensaje": "Las horas deben ser un número entero"})

        # Validar juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Guardar nuevo archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
            docencia.documento = documento_url

        # Actualizar campos
        docencia.juez = juez
        docencia.curso = curso
        docencia.universidad = universidad
        docencia.anio = anio
        docencia.horas = horas
        docencia.puntaje = puntaje
        docencia.save()

        return redirect("/meritopj/registrar_docencia")

    jueces = Juez.objects.all()
    return render(request, "form_editar/editar_docencia.html", {
        "jueces": jueces,
        "docencia": docencia
    })

#FUNCIONES PARA CRUD PARA LA VALORIZACION DE PUNTAJE
#1. FUNCIONES DE REGISRO
def registrar_antiguedad_valor_puntaje(request):
    if request.method == 'POST':
        Antiguedad_valor_puntaje.objects.create(
            js_puntaje_min=request.POST.get('js_puntaje_min'),
            js_puntaje_max=request.POST.get('js_puntaje_max'),
            jpl_puntaje_min=request.POST.get('jpl_puntaje_min'),
            jpl_puntaje_max=request.POST.get('jpl_puntaje_max'),
            je_puntaje_min=request.POST.get('je_puntaje_min'),
            je_puntaje_max=request.POST.get('je_puntaje_max')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_antiguedad_puntaje.html')

def registrar_gradoacademico_valor_puntaje(request):
    if request.method == 'POST':
        GradoAcademico_valor_puntaje.objects.create(
            doj_puntaje=request.POST.get('doj_puntaje'),
            donj_puntaje=request.POST.get('donj_puntaje'),
            maj_puntaje=request.POST.get('maj_puntaje'),
            manj_puntaje=request.POST.get('manj_puntaje'),
            tinj_puntaje=request.POST.get('tinj_puntaje')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_gradoacademico_puntaje.html')

def registrar_magistratura_valor_puntaje(request):
    if request.method == 'POST':
        Magistratura_valor_puntaje.objects.create(
            puntaje_alto=request.POST.get('puntaje_alto'),
            puntaje_semialto=request.POST.get('puntaje_semialto'),
            puntaje_medio=request.POST.get('puntaje_medio'),
            puntaje_bajo=request.POST.get('puntaje_bajo')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_magistratura_puntaje.html')

def registrar_doctorado_valor_puntaje(request):
    if request.method == 'POST':
        Doctorado_valor_puntaje.objects.create(
            puntaje_alto=request.POST.get('puntaje_alto'),
            puntaje_medio=request.POST.get('puntaje_medio'),
            puntaje_bajo=request.POST.get('puntaje_bajo')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_doctorado_puntaje.html')

def registrar_maestria_valor_puntaje(request):
    if request.method == 'POST':
        Maestria_valor_puntaje.objects.create(
            puntaje_alto=request.POST.get('puntaje_alto'),
            puntaje_medio=request.POST.get('puntaje_medio'),
            puntaje_bajo=request.POST.get('puntaje_bajo')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_maestria_puntaje.html')

def registrar_pasantia_valor_puntaje(request):
    if request.method == 'POST':
        Pasantia_valor_puntaje.objects.create(
            puntaje_alto=request.POST.get('puntaje_alto'),
            puntaje_bajo=request.POST.get('puntaje_bajo')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_pasantia_puntaje.html')

def registrar_cursoespecializacion_valor_puntaje(request):
    if request.method == 'POST':
        CursoEspecializacion_valor_puntaje.objects.create(
            puntaje_alto=request.POST.get('puntaje_alto'),
            puntaje_medio=request.POST.get('puntaje_medio'),
            puntaje_bajo=request.POST.get('puntaje_bajo')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_cursoespecializacion_puntaje.html')

def registrar_certamenacademico_valor_puntaje(request):
    if request.method == 'POST':
        CertamenAcademico_valor_puntaje.objects.create(
            puntaje_alto=request.POST.get('puntaje_alto'),
            puntaje_bajo=request.POST.get('puntaje_bajo')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_certamenacademico_puntaje.html')

def registrar_eventoacademico_valor_puntaje(request):
    if request.method == 'POST':
        EventoAcademico_valor_puntaje.objects.create(
            puntaje=request.POST.get('puntaje')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_eventoacademico_puntaje.html')

def registrar_ofimatica_valor_puntaje(request):
    if request.method == 'POST':
        Ofimatica_valor_puntaje.objects.create(
            puntaje_basico=request.POST.get('puntaje_basico'),
            puntaje_intermedio=request.POST.get('puntaje_intermedio'),
            puntaje_avanzado=request.POST.get('puntaje_avanzado')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_ofimatica_puntaje.html')

def registrar_idiomas_valor_puntaje(request):
    if request.method == 'POST':
        Idiomas_valor_puntaje.objects.create(
            puntaje_basico=request.POST.get('puntaje_basico'),
            puntaje_intermedio=request.POST.get('puntaje_intermedio'),
            puntaje_avanzado=request.POST.get('puntaje_avanzado')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_idiomas_puntaje.html')

def registrar_publicacionjuridica_valor_puntaje(request):
    if request.method == 'POST':
        PublicacionJuridica_valor_puntaje.objects.create(
            puntaje_libro=request.POST.get('puntaje_libro'),
            puntaje_revista=request.POST.get('puntaje_revista'),
            puntaje_merito=request.POST.get('puntaje_merito')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_publicacionjuridica_puntaje.html')

def registrar_distincion_valor_puntaje(request):
    if request.method == 'POST':
        Distincion_valor_puntaje.objects.create(
            puntaje=request.POST.get('puntaje')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_distincion_puntaje.html')

def registrar_docencia_valor_puntaje(request):
    if request.method == 'POST':
        Docencia_valor_puntaje.objects.create(
            puntaje=request.POST.get('puntaje')
        )
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_docencia_puntaje.html')

#2. FUNCIONES DE EDITAR

def editar_antiguedad_valor_puntaje(request, id):
    registro = Antiguedad_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.js_puntaje_min = request.POST.get('js_puntaje_min')
        registro.js_puntaje_max = request.POST.get('js_puntaje_max')
        registro.jpl_puntaje_min = request.POST.get('jpl_puntaje_min')
        registro.jpl_puntaje_max = request.POST.get('jpl_puntaje_max')
        registro.je_puntaje_min = request.POST.get('je_puntaje_min')
        registro.je_puntaje_max = request.POST.get('je_puntaje_max')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_antiguedad_puntaje.html', {'registro': registro})

def editar_gradoacademico_valor_puntaje(request, id):
    registro = GradoAcademico_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.doj_puntaje = request.POST.get('doj_puntaje')
        registro.donj_puntaje = request.POST.get('donj_puntaje')
        registro.maj_puntaje = request.POST.get('maj_puntaje')
        registro.manj_puntaje = request.POST.get('manj_puntaje')
        registro.tinj_puntaje = request.POST.get('tinj_puntaje')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_gradoacademico_puntaje.html', {'registro': registro})

def editar_magistratura_valor_puntaje(request, id):
    registro = Magistratura_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_alto = request.POST.get('puntaje_alto')
        registro.puntaje_semialto = request.POST.get('puntaje_semialto')
        registro.puntaje_medio = request.POST.get('puntaje_medio')
        registro.puntaje_bajo = request.POST.get('puntaje_bajo')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_magistratura_puntaje.html', {'registro': registro})

def editar_doctorado_valor_puntaje(request, id):
    registro = Doctorado_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_alto = request.POST.get('puntaje_alto')
        registro.puntaje_medio = request.POST.get('puntaje_medio')
        registro.puntaje_bajo = request.POST.get('puntaje_bajo')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_doctorado_puntaje.html', {'registro': registro})

def editar_maestria_valor_puntaje(request, id):
    registro = Maestria_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_alto = request.POST.get('puntaje_alto')
        registro.puntaje_medio = request.POST.get('puntaje_medio')
        registro.puntaje_bajo = request.POST.get('puntaje_bajo')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_maestria_puntaje.html', {'registro': registro})

def editar_pasantia_valor_puntaje(request, id):
    registro = Pasantia_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_alto = request.POST.get('puntaje_alto')
        registro.puntaje_bajo = request.POST.get('puntaje_bajo')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_pasantia_puntaje.html', {'registro': registro})

def editar_cursoespecializacion_valor_puntaje(request, id):
    registro = CursoEspecializacion_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_alto = request.POST.get('puntaje_alto')
        registro.puntaje_medio = request.POST.get('puntaje_medio')
        registro.puntaje_bajo = request.POST.get('puntaje_bajo')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_cursoespecializacion_puntaje.html', {'registro': registro})

def editar_certamenacademico_valor_puntaje(request, id):
    registro = CertamenAcademico_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_alto = request.POST.get('puntaje_alto')
        registro.puntaje_bajo = request.POST.get('puntaje_bajo')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_certamenacademico_puntaje.html', {'registro': registro})

def editar_eventoacademico_valor_puntaje(request, id):
    registro = EventoAcademico_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje = request.POST.get('puntaje')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_eventoacademico_puntaje.html', {'registro': registro})

def editar_ofimatica_valor_puntaje(request, id):
    registro = Ofimatica_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_basico = request.POST.get('puntaje_basico')
        registro.puntaje_intermedio = request.POST.get('puntaje_intermedio')
        registro.puntaje_avanzado = request.POST.get('puntaje_avanzado')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_ofimatica_puntaje.html', {'registro': registro})

def editar_idiomas_valor_puntaje(request, id):
    registro = Idiomas_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_basico = request.POST.get('puntaje_basico')
        registro.puntaje_intermedio = request.POST.get('puntaje_intermedio')
        registro.puntaje_avanzado = request.POST.get('puntaje_avanzado')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_idiomas_puntaje.html', {'registro': registro})

def editar_publicacionjuridica_valor_puntaje(request, id):
    registro = PublicacionJuridica_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje_libro = request.POST.get('puntaje_libro')
        registro.puntaje_revista = request.POST.get('puntaje_revista')
        registro.puntaje_merito = request.POST.get('puntaje_merito')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_publicacionjuridica_puntaje.html', {'registro': registro})

def editar_distincion_valor_puntaje(request, id):
    registro = Distincion_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje = request.POST.get('puntaje')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_distincion_puntaje.html', {'registro': registro})

def editar_docencia_valor_puntaje(request, id):
    registro = Docencia_valor_puntaje.objects.get(id=id)
    if request.method == 'POST':
        registro.puntaje = request.POST.get('puntaje')
        registro.save()
        return redirect('menu_puntajes')
    return render(request, 'form_puntajes/form_docencia_puntaje.html', {'registro': registro})

# 3. FUNCIONES DE ELIMINAR
def eliminar_antiguedad_valor_puntaje(request, id):
    registro = Antiguedad_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_gradoacademico_valor_puntaje(request, id):
    registro = GradoAcademico_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_magistratura_valor_puntaje(request, id):
    registro = Magistratura_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_doctorado_valor_puntaje(request, id):
    registro = Doctorado_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_maestria_valor_puntaje(request, id):
    registro = Maestria_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_pasantia_valor_puntaje(request, id):
    registro = Pasantia_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_cursoespecializacion_valor_puntaje(request, id):
    registro = CursoEspecializacion_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_certamenacademico_valor_puntaje(request, id):
    registro = CertamenAcademico_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_eventoacademico_valor_puntaje(request, id):
    registro = EventoAcademico_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_ofimatica_valor_puntaje(request, id):
    registro = Ofimatica_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_idiomas_valor_puntaje(request, id):
    registro = Idiomas_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_publicacionjuridica_valor_puntaje(request, id):
    registro = PublicacionJuridica_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_distincion_valor_puntaje(request, id):
    registro = Distincion_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

def eliminar_docencia_valor_puntaje(request, id):
    registro = Docencia_valor_puntaje.objects.get(id=id)
    registro.delete()
    return redirect('menu_puntajes')

#4. FUNCIONES PARA MOSTRAR

def mostrar_antiguedad_valor_puntaje(request):
    registros = Antiguedad_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_antiguedad_puntaje.html', {'registros': registros})

def mostrar_gradoacademico_valor_puntaje(request):
    registros = GradoAcademico_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_gradoacademico_puntaje.html', {'registros': registros})

def mostrar_magistratura_valor_puntaje(request):
    registros = Magistratura_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_magistratura_puntaje.html', {'registros': registros})

def mostrar_doctorado_valor_puntaje(request):
    registros = Doctorado_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_doctorado_puntaje.html', {'registros': registros})

def mostrar_maestria_valor_puntaje(request):
    registros = Maestria_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_maestria_puntaje.html', {'registros': registros})

def mostrar_pasantia_valor_puntaje(request):
    registros = Pasantia_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_pasantia_puntaje.html', {'registros': registros})

def mostrar_cursoespecializacion_valor_puntaje(request):
    registros = CursoEspecializacion_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_cursoespecializacion_puntaje.html', {'registros': registros})

def mostrar_certamenacademico_valor_puntaje(request):
    registros = CertamenAcademico_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_certamenacademico_puntaje.html', {'registros': registros})

def mostrar_eventoacademico_valor_puntaje(request):
    registros = EventoAcademico_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_eventoacademico_puntaje.html', {'registros': registros})

def mostrar_ofimatica_valor_puntaje(request):
    registros = Ofimatica_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_ofimatica_puntaje.html', {'registros': registros})

def mostrar_idiomas_valor_puntaje(request):
    registros = Idiomas_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_idiomas_puntaje.html', {'registros': registros})

def mostrar_publicacionjuridica_valor_puntaje(request):
    registros = PublicacionJuridica_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_publicacionjuridica_puntaje.html', {'registros': registros})

def mostrar_distincion_valor_puntaje(request):
    registros = Distincion_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_distincion_puntaje.html', {'registros': registros})

def mostrar_docencia_valor_puntaje(request):
    registros = Docencia_valor_puntaje.objects.all()
    return render(request, 'form_puntajes/form_docencia_puntaje.html', {'registros': registros})

def menu_puntajes(request):
    return render(request, 'menu_valores_puntaje.html')
