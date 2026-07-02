from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    def test_creacion_usuario_con_rol_acudiente(self):
        user = Usuario.objects.create_user(
            username="acudiente1",
            password="claveSegura123",
            rol="acudiente",
        )
        self.assertEqual(user.rol, "acudiente")

    def test_creacion_usuario_con_rol_docente(self):
        user = Usuario.objects.create_user(
            username="docente1",
            password="claveSegura123",
            rol="docente",
        )
        self.assertEqual(user.rol, "docente")

    def test_creacion_usuario_con_rol_administrador(self):
        user = Usuario.objects.create_user(
            username="admin1",
            password="claveSegura123",
            rol="administrador",
        )
        self.assertEqual(user.rol, "administrador")


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username="test_admin",
            password="claveSegura123",
            rol="administrador",
        )

    def test_acceso_sin_login_redirige(self):
        response = self.client.get(reverse('app:index_curso'))
        self.assertEqual(response.status_code, 302)

    def test_login_correcto(self):
        response = self.client.post(reverse('login:login'), {
            'username': 'test_admin',
            'password': 'claveSegura123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_incorrecto(self):
        response = self.client.post(reverse('login:login'), {
            'username': 'test_admin',
            'password': 'password_erronea',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_acceso_con_login_ok(self):
        self.client.login(username='test_admin', password='claveSegura123')
        response = self.client.get(reverse('app:index_curso'))
        self.assertEqual(response.status_code, 200)