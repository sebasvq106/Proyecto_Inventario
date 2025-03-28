import pytest
from django.urls import reverse
from supply_room.models import Item, Users


@pytest.mark.django_db
def test_crear_articulo(client):
    """
    Test to verify the creation of an item.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='admin'
    )
    client.force_login(user)

    url = reverse('crear-articulo')

    # Create test data
    data = {
        'name': 'Resistencia',
        'quantity': 3
    }

    # Make POST request
    response = client.post(url, data)

    # Verify redirection
    assert response.status_code == 302

    # Verify that the items were created
    items = Item.objects.filter(name='Resistencia')
    assert items.count() == 3

    # Verify that all have the same name
    for item in items:
        assert item.name == 'Resistencia'


@pytest.mark.django_db
def test_crear_articulo_cantidad_invalida(client):
    """
    Test that verifies the handling of invalid quantities.
    """
    # Create and authenticate user
    admin_user = Users.objects.create_user(
        username='adminuser3',
        password='testpass',
        role='admin'
    )
    client.force_login(admin_user)

    url = reverse("crear-articulo")

    # Case 1: Zero quantity
    data_zero = {
        'name': 'LED Rojo',
        'quantity': 0
    }
    response_zero = client.post(url, data_zero)
    assert response_zero.status_code == 200
    assert 'quantity' in response_zero.context['form'].errors

    # Case 2: Negative quantity
    data_negative = {
        'name': 'LED Verde',
        'quantity': -5
    }
    response_negative = client.post(url, data_negative)
    assert response_negative.status_code == 200
    assert 'quantity' in response_negative.context['form'].errors

    # Case 3: Non-numerical quantity
    data_non_numeric = {
        'name': 'LED Azul',
        'quantity': 'abc'
    }
    response_non_numeric = client.post(url, data_non_numeric)
    assert response_non_numeric.status_code == 200
    assert 'quantity' in response_non_numeric.context['form'].errors
