import pytest
from django.urls import reverse
from supply_room.models import (Class, Users, ClassGroups, Order,
                                UserOrder, Item)


@pytest.fixture
def setup_test_data(client):
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="teacherpass",
        role="teacher"
    )

    student1 = Users.objects.create_user(
        username="student1",
        email="student1@example.com",
        password="student1pass",
        role="student",
        name="Sebas"
    )

    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    group1 = ClassGroups.objects.create(number=1,
                                        year=2025,
                                        term='I',
                                        professor=teacher,
                                        class_id=class1
                                        )

    group1.add_students([student1])

    order1 = Order.objects.create(group=group1)

    UserOrder.objects.create(order=order1, user=student1)

    item1 = Item.objects.create(name='Resistor 100', is_available=True)
    item2 = Item.objects.create(name='Resistor 200', is_available=True)
    item3 = Item.objects.create(name='Resistor 100', is_available=True)
    item4 = Item.objects.create(name='Resistor 100', is_available=True)
    item5 = Item.objects.create(name='Capacitor', is_available=False)

    return {
        "client": client,
        "items": [item1, item2, item3, item4, item5]
    }


@pytest.mark.django_db
def test_item_search_view(setup_test_data):
    """
    Test that the item search view returns correct JSON results
    """
    client = setup_test_data["client"]
    items = setup_test_data["items"]
    student1 = Users.objects.get(username="student1")

    # Authenticate the user
    client.force_login(student1)

    url = reverse("item_search")

    # Case 1: Empty search - should return all available items
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2  # Only 2 unique items available

    # Case 2: Search with specific term
    response = client.get(url, {'q': 'Resistor'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2  # Resistor 100 y Resistor 200
    assert {'id': items[0].id, 'text': 'Resistor 100'} in data['results']
    assert {'id': items[1].id, 'text': 'Resistor 200'} in data['results']

    # Case 3: Exact search
    response = client.get(url, {'q': 'Resistor 100'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['text'] == 'Resistor 100'

    # Case 4: No results found
    response = client.get(url, {'q': 'Transistor'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 0

    # Case 5: Verify that no unavailable items are returned
    response = client.get(url, {'q': 'Capacitor'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 0  # Capacitor is not available
