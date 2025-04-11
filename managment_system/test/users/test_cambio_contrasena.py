import pytest
from django.urls import reverse
from django.contrib.auth import authenticate
from supply_room.models import Users


@pytest.mark.django_db
def test_password_change_view(client):
    """
    Test that PasswordChangeView changes the password correctly.
    """
    # Crear y autenticar al usuario
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@user.com',
        password='testpass',
        role='student'
    )
    client.force_login(user)

    # Data
    data = {
        'old_password': 'testpass',
        'new_password1': 'Testp@ss22',
        'new_password2': 'Testp@ss22'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    assert response.status_code == 302

    client.logout()

    # Verificar que la contraseña vieja ya no funciona
    user_old = authenticate(email='testuser@user.com', password='testpass')
    assert user_old is None

    client.logout()

    # Verificar que se puede autenticar con la nueva contraseña
    user_refresh = authenticate(
        email='testuser@user.com',
        password='Testp@ss22'
    )
    assert user_refresh is not None
    assert user_refresh.username == 'testuser'


@pytest.mark.django_db
def test_password_change_view_incorrect_old_password(client):
    """
    Test that password does NOT change if the old password is incorrect.
    """
    # Crear y autenticar al usuario
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@user.com',
        password='testpass',
        role='student'
    )
    client.force_login(user)

    # Enviar datos con contraseña actual incorrecta
    data = {
        'old_password': 'wrongpass',
        'new_password1': 'Testp@ss22',
        'new_password2': 'Testp@ss22'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    assert response.status_code == 200

    # Verificar que el formulario tiene errores
    form = response.context['form']
    assert 'old_password' in form.errors

    client.logout()

    # La contraseña vieja aún debe funcionar
    assert client.login(email='testuser@user.com', password='testpass')

    # La nueva contraseña NO debe funcionar
    client.logout()
    assert not client.login(email='testuser@user.com', password='Testp@ss22')


@pytest.mark.django_db
def test_password_change_same_as_old_password(client):
    """
    Test that password change fails if the new password is
    the same as the old one.
    """
    # Crear y autenticar al usuario
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@user.com',
        password='Test@2255',
        role='student'
    )
    client.force_login(user)

    # Enviar datos donde la nueva contraseña es igual a la actual
    data = {
        'old_password': 'Test@2255',
        'new_password1': 'Test@2255',
        'new_password2': 'Test@2255'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    # No debe redirigir, debe mostrar errores
    assert response.status_code == 200

    client.logout()
    assert not client.login(username='testuser', password='Test@2255')  # La contraseña no debe haberse cambiado


@pytest.mark.django_db
def test_password_change_invalid_password(client):
    """
    Test that password change fails if the new password is invalid.
    """
    # Crear y autenticar al usuario
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@user.com',
        password='Test@2255',
        role='student'
    )
    client.force_login(user)

    # Contraseña nueva inválida
    data = {
        'old_password': 'Test@2255',
        'new_password1': 'aa',  # Contraseña demasiado corta
        'new_password2': 'aa'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    # No debe redirigir, debe mostrar errores del formulario
    assert response.status_code == 200

    client.logout()
    assert client.login(email='testuser@user.com', password='Test@2255')

    client.logout()
    assert not client.login(email='testuser@user.com', password='aa')
