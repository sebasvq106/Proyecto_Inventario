import pytest
from django.urls import reverse
from supply_room.models import Item, Users


@pytest.mark.django_db
def test_articulos_disponibles(client):
    """
    Test that the ItemList view renders the grouped items correctly.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='student'
    )
    client.force_login(user)

    # Create test data
    Item.objects.create(name="Resistencia", is_available=True)
    Item.objects.create(name="Resistencia", is_available=False)
    Item.objects.create(name="Capacitor", is_available=True)

    # Make GET request
    url = reverse("articulos-disponibles")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 2

    # Verify group Resistencia
    resistencia_group = next(item for item in items if item['name'] == 'Resistencia')
    assert resistencia_group['count'] == 1

    # Verify group Capacitor
    capacitor_group = next(item for item in items if item['name'] == 'Capacitor')
    assert capacitor_group['count'] == 1
