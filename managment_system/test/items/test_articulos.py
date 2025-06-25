import json
import pytest
from django.urls import reverse
from supply_room.models import Item, Users


@pytest.mark.django_db
def test_articulos(client):
    """
    Test that the ItemList view renders the grouped items correctly.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='admin'
    )
    client.force_login(user)

    # Create test data
    item1 = Item.objects.create(name="Resistencia", is_available=True)
    item2 = Item.objects.create(name="Resistencia", is_available=False)
    item3 = Item.objects.create(name="Capacitor", is_available=True)

    # Make GET request
    url = reverse("articulos")
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
    assert resistencia_group['count'] == 2
    detalles = json.loads(resistencia_group['detalles'])
    assert len(detalles) == 2
    assert any(d['id'] == item1.id and d['is_available'] for d in detalles)
    assert any(d['id'] == item2.id and not d['is_available'] for d in detalles)

    # Verify group Capacitor
    capacitor_group = next(item for item in items if item['name'] == 'Capacitor')
    assert capacitor_group['count'] == 1
    detalles = json.loads(capacitor_group['detalles'])
    assert detalles[0]['id'] == item3.id
    assert detalles[0]['is_available'] is True
