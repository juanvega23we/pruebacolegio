from django.db import connection, transaction
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from app.models import Usuario, Notificacion, Curso, Administrador
from django.contrib.auth import get_user_model
import os
from django.conf import settings

Usuario = get_user_model()

@receiver(post_migrate)
@receiver(post_migrate)
def inicializar_roles_y_admin(sender, **kwargs):
    if sender.name != "app":
        return

    print("[INFO] Inicializando roles, permisos y administrador...")
    
    # 1. Crear grupos (Esto no requiere la tabla Usuario, solo la de Auth)
    for nombre in ['Administrador', 'Docente', 'Estudiante', 'Acudiente']:
        Group.objects.get_or_create(name=nombre)
    
    admin_group = Group.objects.get(name='Administrador')
    admin_group.permissions.set(Permission.objects.all())

    # 2. Comprobación segura de la tabla para el Admin
    # Usamos la inspección de la base de datos para no dar error si la tabla no existe
    if 'usuario' in connection.introspection.table_names():
        if not Usuario.objects.filter(email="admin@colegio.com").exists():
            usuario = Usuario.objects.create_user(
                email="admin@colegio.com",
                nombre="Administrador Principal",
                password="admin123",
                is_staff=True,
                is_superuser=True,
                estado=True
            )
            usuario.groups.add(admin_group)
            Administrador.objects.create(usuario=usuario, cargo="Administrador General")
            print("[OK] Administrador creado correctamente")
    else:
        print("[AVISO] La tabla 'usuario' aún no existe, omitiendo creación de admin.")

def enviar_correo_notificacion(asunto, destinatario, html_context):
    """Función auxiliar para no repetir código de correo"""
    try:
        html_content = render_to_string('emails/notificacion.html', html_context)
        text_content = strip_tags(html_content)

        correo = EmailMultiAlternatives(asunto, text_content, settings.DEFAULT_FROM_EMAIL, [destinatario])
        correo.attach_alternative(html_content, "text/html")

        ruta_imagen = os.path.join(settings.BASE_DIR, 'app/static/img/Logo.jpeg')
        if os.path.exists(ruta_imagen):
            with open(ruta_imagen, "rb") as img:
                mime_img = MIMEImage(img.read())
                mime_img.add_header('Content-ID', '<logo_colegio>')
                correo.attach(mime_img)
        
        correo.send()
    except Exception as e:
        print(f"Error enviando correo: {e}")

@receiver(post_save, sender=Usuario)
def notificar_usuario(sender, instance, created, **kwargs):
    if kwargs.get('update_fields') and 'last_login' in kwargs['update_fields']:
        return

    # Usamos transaction.on_commit para que el correo solo se envíe si el usuario se guardó realmente
    def realizar_notificaciones():
        administradores = Usuario.objects.filter(groups__name='Administrador')
        
        titulo = "Se ha creado un nuevo usuario" if created else "Se ha editado un usuario"
        mensaje = f"Se {'creó' if created else 'editó'} el usuario {instance.nombre}"
        
        for admin in administradores:
            Notificacion.objects.create(
                titulo=titulo, mensaje=mensaje, fecha_envio=now().date(),
                estado='no_leida', tipo="aviso", receptor=admin
            )

        if instance.email:
            enviar_correo_notificacion(
                "Creación/Edición de cuenta", instance.email,
                {'titulo': titulo, 'nombre': instance.nombre, 'mensaje': f"Tu cuenta ha sido {'creada' if created else 'actualizada'} correctamente."}
            )

    transaction.on_commit(realizar_notificaciones)

@receiver(post_save, sender=Curso)
def notificar_curso(sender, instance, created, **kwargs):
    def realizar_notificaciones():
        administradores = Usuario.objects.filter(groups__name='Administrador')
        
        titulo = "Curso creado" if created else "Curso actualizado"
        mensaje = f"Curso {instance.codigo} - Grado: {instance.grado}"
        
        for admin in administradores:
            Notificacion.objects.create(
                titulo=titulo, mensaje=mensaje, fecha_envio=now().date(),
                estado='no_leida', tipo="actualizacion", receptor=admin
            )

        if instance.docenteid and hasattr(instance.docenteid, 'usuario'):
            docente_usuario = instance.docenteid.usuario
            enviar_correo_notificacion(
                titulo, docente_usuario.email,
                {'titulo': titulo, 'nombre': docente_usuario.nombre, 'mensaje': f"El curso {instance.codigo} ha sido gestionado."}
            )

    transaction.on_commit(realizar_notificaciones)