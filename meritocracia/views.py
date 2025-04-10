
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CertamenAcademico, CursoEspecializacion, Demeritos, Distincion, Docencia, EstudioIdioma, EstudioMaestria, EstudioOfimatica, EstudioPerfeccionamiento, EventoAcademico, Juez, Antiguedad, GradoAcademico, EstudiosMagistratura, EstudioDoctorado, Pasantia, PublicacionJuridica, PuntajeTotal
from meritocracia import models


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
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

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    return render(request, 'admin_main.html')

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
            return redirect("/meritopj/")

        except Exception as e:
            messages.error(request, f"Error al registrar juez: {e}")
            return redirect("/meritopj/")

    return render(request, "form_registro_juez.html")
    

def registrar_antiguedad(request):
    jueces = Juez.objects.all()
    if request.method == "POST":
        juez_id = request.POST.get("juez") 
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        puntaje = request.POST.get("puntaje", 1)

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})
        
        Antiguedad.objects.create(
            juez=juez,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin if fecha_fin else None,
            puntaje=float(puntaje)
        )

        return redirect("/meritopj") 

    return render(request, "form_antiguedad_juez.html",{"jueces": jueces})


def registrar_grado_academico(request):
    jueces = Juez.objects.all()

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        titulo_gd = request.POST.get("titulo_gd")
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")
        puntaje = request.POST.get("puntaje")
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Validar y calcular puntaje si por alguna razón viene vacío o alterado
        if tipo == 'DOJ':
            puntaje = 9
        elif tipo == 'DONJ':
            puntaje = 6
        elif tipo == 'MAJ':
            puntaje = 4
        elif tipo == 'MANJ':
            puntaje = 3
        elif tipo == 'TINJ':
            puntaje = 2
        else:
            puntaje = 0

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear el registro en la base de datos
        GradoAcademico.objects.create(
            juez=juez,
            titulo_gd=titulo_gd,
            tipo=tipo,
            anio=int(anio),
            puntaje=float(puntaje),
            documento=documento_url if documento else None  # Guardar la URL del documento
        )

        return redirect("/meritopj/")

    return render(request, "form_grado_academico_juez.html", {"jueces": jueces})

def registrar_estudios_magistratura(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        programa = request.POST.get("programa")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        puntaje = request.POST.get("puntaje")
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Validar que la nota sea un número válido
        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        # Asignar puntaje según el rango de la nota
        if 19 <= nota <= 20:
            puntaje = 8
        elif 17 <= nota <= 18:
            puntaje = 6
        elif 15 <= nota <= 16:
            puntaje = 4
        elif 13 <= nota <= 14:
            puntaje = 2
        else:
            puntaje = 0  # Nota menor a 13 no otorga puntaje

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        # Crear el registro
        EstudiosMagistratura.objects.create(
            juez=juez,
            programa=programa,
            anio=int(anio),
            nota=nota,
            puntaje=puntaje,
            documento=documento_url if documento else None,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/")

    jueces = Juez.objects.all()
    return render(request, "form_estudios_magistratura.html", {"jueces": jueces})

def registrar_estudio_perfeccionamiento(request):
    return render(request, "form_estudio_perfeccionamiento.html")

def registrar_doctorado(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get('documento')  

        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        if nota < 15:
            puntaje = 0.5
        elif 15 <= nota <= 18:
            puntaje = 0.75
        else:
            puntaje = 1.0

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        EstudioDoctorado.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=int(anio),
            nota=float(nota),
            puntaje=float(puntaje),
            documento=documento_url if documento else None,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_estudio_doctorado.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })


def registrar_maestria(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        nota = request.POST.get("nota")
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

        try:
            nota = float(nota)
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})

        if nota < 15:
            puntaje = 0.5
        elif 15 <= nota <= 18:
            puntaje = 0.75
        else:
            puntaje = 1.0

        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)

        EstudioMaestria.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=int(anio),
            nota=float(nota),
            puntaje=float(puntaje),
            documento=documento_url if documento else None,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_estudio_maestria.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def registrar_pasantia(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")  
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")  
        nombre = request.POST.get("nombre")  
        tipo = request.POST.get("tipo")
        anio = request.POST.get("anio")  
        nota = request.POST.get("nota")  
        documento = request.FILES.get('documento') 

        try:
            nota = float(nota)  # Intentar convertir la nota a un número flotante
        except ValueError:
            return render(request, "error.html", {"mensaje": "La nota ingresada no es válida"})
    
        # Asignar puntaje según el tipo de pasantía
        if tipo == 'Nacional':
            puntaje = 0.75
        elif tipo == 'Internacional':
            puntaje = 1
        else:
            puntaje = 0  # Puntaje por defecto si el tipo no es válido

        # Verificar si el juez existe
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Verificar si el estudio de perfeccionamiento existe
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear el registro de la pasantía
        Pasantia.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            tipo=tipo,
            anio=int(anio),
            nota=float(nota),
            puntaje=float(puntaje),
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")  

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()
    
    return render(request, "form_pasantia.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })


def registrar_curso_especializacion(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento") 
        nombre = request.POST.get("nombre")  
        horas = request.POST.get("horas")  
        anio = request.POST.get("anio")  
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

        # Convertir las horas a número entero
        try:
            horas = int(horas)
        except ValueError:
            return render(request, "error.html", {"mensaje": "Las horas ingresadas no son válidas"})

        # Calcular puntaje según la cantidad de horas
        if horas > 200:
            puntaje = 1
        elif 101 <= horas <= 200:
            puntaje = 0.75
        elif 50 <= horas <= 100:
            puntaje = 0.5
        else:
            puntaje = 0  # No asigna puntaje si las horas son menores a 50

        # Obtener el juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Obtener el estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar el registro del curso de especialización
        CursoEspecializacion.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            horas=horas,
            anio=int(anio),
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()
    
    return render(request, "form_especializacion.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def registrar_certamen_academico(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        tipo_participacion = request.POST.get("tipo_participacion")
        nombre = request.POST.get("nombre")
        tipo = request.POST.get("tipo")  # Nacional o Internacional
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

        # Calcular puntaje según el tipo de participación
        if tipo == 'Nacional':
            puntaje = 0.25
        elif tipo == 'Internacional':
            puntaje = 0.5
        else:
            puntaje = 0  # En caso de que no se haya seleccionado correctamente

        # Obtener el juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Obtener el estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar el registro en la base de datos
        CertamenAcademico.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            tipo_participacion=tipo_participacion,
            nombre=nombre,
            tipo=tipo,
            anio=int(anio),
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")  # Redirige al formulario de estudio de perfeccionamiento

    # Obtener los jueces y estudios de perfeccionamiento para los selectores
    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_certamen_academico.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def registrar_evento_academico(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

        # Puntaje fijo para todos los registros
        puntaje = 0.25

        # Obtener el juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Obtener el estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar el registro en la base de datos
        EventoAcademico.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=int(anio),
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")  # Redirigir a otra página después del registro

    # Obtener los jueces y estudios de perfeccionamiento para mostrarlos en el formulario
    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_evento_academico.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def registrar_estudio_ofimatica(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener el archivo si se sube

        # Asignar puntaje según el nivel
        puntaje_dict = {
            "Básico": 0.5,
            "Intermedio": 0.75,
            "Avanzado": 1.0
        }
        puntaje = puntaje_dict.get(nivel, 0)  # Por defecto 0 si nivel no está definido

        # Obtener el juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Obtener el estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar el estudio de ofimática
        EstudioOfimatica.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nivel=nivel,
            estudio=nombre_estudio,
            anio=int(anio),
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    # Para el formulario
    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_estudio_ofimatica.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })

def registrar_estudio_idiomas(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener el archivo si se sube

        # Asignar puntaje según el nivel
        puntaje_dict = {
            "Básico": 0.5,
            "Intermedio": 0.75,
            "Avanzado": 1.0
        }
        puntaje = puntaje_dict.get(nivel, 0)  # Por defecto 0 si nivel no está definido

        # Obtener el juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Obtener el estudio de perfeccionamiento
        try:
            estudio_perfeccionamiento = EstudioPerfeccionamiento.objects.get(id_estudioperfeccionamiento=estudio_perfeccionamiento_id)
        except EstudioPerfeccionamiento.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El estudio de perfeccionamiento no existe"})

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
            anio=int(anio),
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()

    return render(request, "form_estudio_idiomas.html", {
        "jueces": jueces,
        "estudios_perfeccionamiento": estudios_perfeccionamiento
    })


def registrar_publicacion_juridica(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        tipo = request.POST.get("tipo")
        nombre = request.POST.get("nombre")
        documento = request.FILES.get('documento')  # Obtener archivo PDF

        # Definir puntajes según el tipo de publicación
        puntajes = {
            "LIBRO": 1.5,
            "REVISTA": 0.5,
            "MERITO": 1
        }
        
        puntaje = puntajes.get(tipo, 0)  # Valor predeterminado de 0 si el tipo no es válido

        # Validar existencia del juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar la publicación jurídica
        PublicacionJuridica.objects.create(
            juez=juez,
            tipo=tipo,
            nombre=nombre,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_publicacion_juridica")  # Redirige tras registrar

    # Obtener lista de jueces para el formulario
    jueces = Juez.objects.all()

    return render(request, "form_publicacion_juridica.html", {"jueces": jueces})

def registrar_distincion(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        nombre = request.POST.get("nombre")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')  # Obtener archivo PDF si se sube
        puntaje = 0.5  # Puntaje fijo

        # Validar que el juez exista
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Crear y guardar la distinción
        Distincion.objects.create(
            juez=juez,
            nombre=nombre,
            anio=anio,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_distincion")  # Redirige al mismo formulario tras registrar

    # Mostrar formulario con lista de jueces
    jueces = Juez.objects.all()
    return render(request, "form_distincion.html", {"jueces": jueces})

def registrar_docencia(request):
    if request.method == "POST":
        juez_id = request.POST.get("juez")
        curso = request.POST.get("curso")
        universidad = request.POST.get("universidad")
        anio = request.POST.get("anio")
        horas = request.POST.get("horas")
        documento = request.FILES.get('documento')  # Obtener archivo PDF si se sube

        # Calcular puntaje
        try:
            horas = int(horas)
            puntaje = horas * 0.375
        except ValueError:
            return render(request, "error.html", {"mensaje": "Las horas deben ser un número entero"})

        # Obtener el juez
        try:
            juez = Juez.objects.get(id_juez=juez_id)
        except Juez.DoesNotExist:
            return render(request, "error.html", {"mensaje": "El juez no existe"})

        # Guardar el archivo si se sube
        if documento:
            fs = FileSystemStorage()
            filename = fs.save(documento.name, documento)
            documento_url = fs.url(filename)
        else:
            documento_url = None

        # Guardar la docencia
        Docencia.objects.create(
            juez=juez,
            curso=curso,
            universidad=universidad,
            anio=anio,
            horas=horas,
            puntaje=puntaje,
            documento=documento_url,
            estado='PENDIENTE'
        )

        return redirect("/meritopj/registrar_docencia")  # Redirigir tras registrar

    # Mostrar formulario
    jueces = Juez.objects.all()
    return render(request, "form_docencia.html", {"jueces": jueces})


#def calcular_puntaje_total(juez_id):
    juez = get_object_or_404(Juez, id_juez=juez_id)

    # Sumamos los puntajes de cada modelo relacionado
    puntaje_antiguedad = Antiguedad.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_grado_academico = GradoAcademico.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_estudios_magistratura = EstudiosMagistratura.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_estudios_doctorado = EstudioDoctorado.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_estudios_maestria = EstudioMaestria.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_pasantia = Pasantia.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_curso_especializacion = CursoEspecializacion.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_certamen_academico = CertamenAcademico.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_evento_academico = EventoAcademico.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_ofimatica = EstudioOfimatica.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_idioma = EstudioIdioma.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_publicaciones = PublicacionJuridica.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_distincion = Distincion.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_docencia = Docencia.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0
    puntaje_demeritos = Demeritos.objects.filter(juez=juez).aggregate(total=models.Sum('puntaje'))['total'] or 0

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

def buscar_juez(request):
    jueces = Juez.objects.all() 

    if request.method == 'POST':
        juez_id = request.POST.get('juez_id')

        datos = obtener_registros_por_juez(juez_id)
        
        if 'error' in datos:
            return render(request, 'admin_mostrar_registros.html', {'error': datos['error'], 'jueces': jueces})
        return render(request, 'admin_mostrar_registros.html', {'datos': datos, 'jueces': jueces})

    return render(request, 'admin_mostrar_registros.html', {'jueces': jueces})


def obtener_jueces_top_5():
    jueces = Juez.objects.all()  
    jueces_con_puntaje = []
    
    for juez in jueces:
        puntaje_total = PuntajeTotal.objects.filter(juez=juez).first()
        jueces_con_puntaje.append({
            'juez': juez,
            'puntaje_total': puntaje_total.puntaje_total if puntaje_total else 0
        })
    
    return sorted(jueces_con_puntaje, key=lambda x: x['puntaje_total'], reverse=True)[:5]

def contar_jueces(request):
    cantidad_jueces = Juez.objects.count()
    context = {
        'cantidad_jueces': cantidad_jueces,
    }
    return render(request, 'admin_main.html', context)
    
def top_jueces(request):
    jueces = obtener_jueces_top_5() 
    return render(request, 'admin_main.html', {'jueces_top_5': jueces})

def admin_view(request):
    jueces_top_5 = obtener_jueces_top_5()
    cantidad_jueces = Juez.objects.count()
    return render(request, 'admin_main.html', {'jueces_top_5': jueces_top_5, 'cantidad_jueces': cantidad_jueces})


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

        # Calcular nuevo puntaje
        tipos_puntaje = {
            'DOJ': 9,
            'DONJ': 6,
            'MAJ': 4,
            'MANJ': 3,
            'TINJ': 2
        }
        puntaje = tipos_puntaje.get(tipo, 0)

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

        return redirect("/meritopj/")

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

        # Calcular puntaje según nota
        if 19 <= nota <= 20:
            puntaje = 8
        elif 17 <= nota <= 18:
            puntaje = 6
        elif 15 <= nota <= 16:
            puntaje = 4
        elif 13 <= nota <= 14:
            puntaje = 2
        else:
            puntaje = 0

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
        return redirect("/meritopj/")

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

        # Asignar puntaje
        if nota < 15:
            puntaje = 0.5
        elif 15 <= nota <= 18:
            puntaje = 0.75
        else:
            puntaje = 1.0

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

        # Asignar puntaje
        if nota < 15:
            puntaje = 0.5
        elif 15 <= nota <= 18:
            puntaje = 0.75
        else:
            puntaje = 1.0

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

        puntaje = 0
        if tipo == 'Nacional':
            puntaje = 0.75
        elif tipo == 'Internacional':
            puntaje = 1

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

        if horas > 200:
            puntaje = 1
        elif 101 <= horas <= 200:
            puntaje = 0.75
        elif 50 <= horas <= 100:
            puntaje = 0.5
        else:
            puntaje = 0

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
            puntaje = 0.25
        elif tipo == 'Internacional':
            puntaje = 0.5
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

        puntaje = 0.25  # Puntaje fijo

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

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        puntaje_dict = {
            "Básico": 0.5,
            "Intermedio": 0.75,
            "Avanzado": 1.0
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

    if request.method == "POST":
        juez_id = request.POST.get("juez")
        estudio_perfeccionamiento_id = request.POST.get("estudio_perfeccionamiento")
        nivel = request.POST.get("nivel")
        nombre_estudio = request.POST.get("estudio")
        anio = request.POST.get("anio")
        documento = request.FILES.get('documento')
        estado = request.POST.get("estado")

        puntaje_dict = {
            "Básico": 0.5,
            "Intermedio": 0.75,
            "Avanzado": 1.0
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

        puntajes = {
            "LIBRO": 1.5,
            "REVISTA": 0.5,
            "MERITO": 1
        }
        puntaje = puntajes.get(tipo, 0)

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
        distincion.puntaje = 0.5
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
