import pytest
from django.urls import reverse
from django.contrib.auth import authenticate
from supply_room.models import Users


@pytest.mark.django_db
def test_password_change_view(client):
    """
    Test that PasswordChangeView changes the password correctly.
    """
    # Create and authenticate the user
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

    # Verify that the old password no longer works
    user_old = authenticate(email='testuser@user.com', password='testpass')
    assert user_old is None

    client.logout()

    # Verify that you can authenticate with the new password
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

    # Send data with incorrect current password
    data = {
        'old_password': 'wrongpass',
        'new_password1': 'Testp@ss22',
        'new_password2': 'Testp@ss22'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    assert response.status_code == 200

    # Verify that the form has errors
    form = response.context['form']
    assert 'old_password' in form.errors

    client.logout()

    # The old password should still work
    assert client.login(email='testuser@user.com', password='testpass')

    # The new password should NOT work
    client.logout()
    assert not client.login(email='testuser@user.com', password='Testp@ss22')


@pytest.mark.django_db
def test_password_change_same_as_old_password(client):
    """
    Test that password change fails if the new password is
    the same as the old one.
    """
    # Create and authenticate the user
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@user.com',
        password='Test@2255',
        role='student'
    )
    client.force_login(user)

    # Send data where the new password is equal to the current password
    data = {
        'old_password': 'Test@2255',
        'new_password1': 'Test@2255',
        'new_password2': 'Test@2255'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    assert response.status_code == 200

    client.logout()
    # The password must not have been changed
    assert not client.login(username='testuser', password='Test@2255')


@pytest.mark.django_db
def test_password_change_invalid_password(client):
    """
    Test that password change fails if the new password is invalid.
    """
    # Create and authenticate the user
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@user.com',
        password='Test@2255',
        role='student'
    )
    client.force_login(user)

    # Invalid new password
    data = {
        'old_password': 'Test@2255',
        'new_password1': 'aa',  # Password too short
        'new_password2': 'aa'
    }

    url = reverse("password_change")
    response = client.post(url, data)

    assert response.status_code == 200

    client.logout()
    assert client.login(email='testuser@user.com', password='Test@2255')

    client.logout()
    assert not client.login(email='testuser@user.com', password='aa')
