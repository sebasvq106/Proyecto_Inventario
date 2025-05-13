import pytest
from django.urls import reverse
from supply_room.models import (Class, Users, ClassGroups, Order,
                                UserOrder, Item, ItemOrder)


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
        "items": [item1, item2, item3, item4, item5],
        "order": order1
    }


@pytest.mark.django_db
def test_create_item_order(setup_test_data):
    """
    Test create a itemorder
    """
    client = setup_test_data["client"]
    items = setup_test_data["items"]
    order = setup_test_data["order"]
    student1 = Users.objects.get(username="student1")

    # Authenticate the user
    client.force_login(student1)

    # Get initial counts
    initial_item_count = Item.objects.filter(is_available=True).count()
    initial_item_order_count = ItemOrder.objects.count()

    # URL for creating item order
    url = reverse("orden-articulo", kwargs={'pk': order.id})

    # Create test data
    data = {
        'item': items[0].id,  # Resistor 100
        'quantity': 2,
    }

    # Make POST request
    response = client.post(url, data)

    # Verify redirection
    assert response.status_code == 302

    # Verify that the ItemOrder was created.
    assert ItemOrder.objects.count() == initial_item_order_count + 1
    new_item_order = ItemOrder.objects.last()
    assert new_item_order.order == order
    assert new_item_order.quantity == 2

    # Verify that the status is 'solicitado'
    assert new_item_order.status == 'Solicitado'

    # Verify that items are marked as unavailable
    assert Item.objects.filter(
        is_available=True).count() == initial_item_count - 2

    # Verify specifically that reserved items are marked
    reserved_items = Item.objects.filter(
        name='Resistor 100',
        is_available=False
    )
    assert reserved_items.count() == 2


@pytest.mark.django_db
def test_no_create_item_order(setup_test_data):
    """
    Test that ItemOrder cannot be created when requested quantity
    exceeds available items
    """
    client = setup_test_data["client"]
    items = setup_test_data["items"]
    order = setup_test_data["order"]
    student1 = Users.objects.get(username="student1")

    # Authenticate the user
    client.force_login(student1)

    # URL
    url = reverse("orden-articulo", kwargs={'pk': order.id})

    # Obtain initial count of ItemOrders
    initial_item_order_count = ItemOrder.objects.count()

    data = {
        'item': items[0].id,  # Resistor 100
        'quantity': 5
    }

    # Make POST request
    response = client.post(url, data)

    # Verify that you are NOT redirected
    assert response.status_code == 200

    # Verify that ItemOrder was not created.
    assert ItemOrder.objects.count() == initial_item_order_count

    # Verify that items are still available
    assert Item.objects.filter(
        name='Resistor 100',
        is_available=True
    ).count() == 3


@pytest.mark.django_db
def test_cannot_order_unavailable_item(setup_test_data):
    '''
    Test to verify that you cannot add an item that is not available
    '''
    client = setup_test_data["client"]
    items = setup_test_data["items"]
    order = setup_test_data["order"]
    student1 = Users.objects.get(username="student1")

    client.force_login(student1)
    url = reverse("orden-articulo", kwargs={'pk': order.id})

    unavailable_item = items[4]
    data = {
        'order': order.id,
        'item': unavailable_item.id,
        'quantity': 1,
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert ItemOrder.objects.count() == 0


@pytest.mark.django_db
def test_cannot_order_nonexistent_item(setup_test_data):
    '''
    Test to verify that you cannot add a non-existent item
    '''
    client = setup_test_data["client"]
    order = setup_test_data["order"]
    student1 = Users.objects.get(username="student1")

    client.force_login(student1)
    url = reverse("orden-articulo", kwargs={'pk': order.id})

    data = {
        'order': order.id,
        'item': 66,
        'quantity': 1,
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert ItemOrder.objects.count() == 0
