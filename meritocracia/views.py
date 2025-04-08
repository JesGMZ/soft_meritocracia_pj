
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CertamenAcademico, CursoEspecializacion, Demeritos, Distincion, Docencia, EstudioIdioma, EstudioMaestria, EstudioOfimatica, EstudioPerfeccionamiento, EventoAcademico, Juez, Antiguedad, GradoAcademico, EstudiosMagistratura, EstudioDoctorado, Pasantia, PublicacionJuridica, PuntajeTotal
from meritocracia import models


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirige según el tipo de usuario
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user):
                return render(request, "meritopj.html")
            else:
                return redirect('home')
        else:
            return render(request, "meritopj.html", {"error": "Credenciales incorrectas"})

    return render(request, "registration/login.html")

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
            documento=documento_url if documento else None  # Guardar la URL del documento
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

        EstudioDoctorado.objects.create(
            juez=juez,
            id_estudioperfeccionamiento=estudio_perfeccionamiento,
            nombre=nombre,
            anio=int(anio),
            nota=float(nota),
            puntaje=float(puntaje),
            documento=documento_url if documento else None  # Guardar la URL del documento
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
            documento=documento_url if documento else None  # Guardar la URL del documento
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
        documento = request.FILES.get('documento')  # Obtener el archivo PDF

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
            documento=documento_url  # Guardar la URL del archivo si se sube
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
            documento=documento_url  # Guardar la URL del archivo si se sube
        )

        return redirect("/meritopj/registrar_estudio_perfeccionamiento")

    jueces = Juez.objects.all()
    estudios_perfeccionamiento = EstudioPerfeccionamiento.objects.all()
    
    return render(request, "form_curso_especializacion.html", {
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
            documento=documento_url  # Guardar la URL del archivo si se sube
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
            documento=documento_url  # Guardar la URL del archivo si se sube
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
            documento=documento_url  # Guardar la URL del archivo si se sube
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
            documento=documento_url  # Guardar la URL del archivo si se sube
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
            documento=documento_url  # Guardar la URL del archivo
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
            documento=documento_url  # Guardar la URL del archivo
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
            documento=documento_url  # Guardar la URL del archivo
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
