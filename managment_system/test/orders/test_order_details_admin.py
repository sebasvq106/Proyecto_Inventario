import pytest
from django.urls import reverse
from supply_room.models import (Class, Users, ClassGroups, Order,
                                UserOrder, ItemOrder, Item)


@pytest.fixture
def setup_test_data(client):

    admin = Users.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="admin",
        role="admin"
    )

    client.force_login(admin)

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
    student2 = Users.objects.create_user(
        username="student2",
        email="student2@example.com",
        password="student2pass",
        role="student",
        name="Luis"
    )

    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")
    class2 = Class.objects.create(name="Lab Digitales", code="IE002")

    group1 = ClassGroups.objects.create(number=1,
                                        year=2025,
                                        term='I',
                                        professor=teacher,
                                        class_id=class1
                                        )

    group2 = ClassGroups.objects.create(number=2,
                                        year=2025,
                                        term='II',
                                        professor=teacher,
                                        class_id=class2
                                        )

    group1.add_students([student1, student2])
    group2.add_students([student1, student2])

    order1 = Order.objects.create(group=group1)
    order2 = Order.objects.create(group=group1)
    order3 = Order.objects.create(group=group2)

    UserOrder.objects.create(order=order1, user=student1)
    UserOrder.objects.create(order=order2, user=student2)
    UserOrder.objects.create(order=order3, user=student1)

    item1 = Item.objects.create(name='Resistor', is_available=True)
    item2 = Item.objects.create(name='Capacitor', is_available=False)

    ItemOrder.objects.create(order=order1,
                             status="Solicitado",
                             quantity=1,
                             item=item1
                             )

    ItemOrder.objects.create(order=order2,
                             status="Prestado",
                             quantity=1,
                             item=item2
                             )

    return {
        "client": client,
        "orders": [order1, order2, order3]
    }


@pytest.mark.django_db
def test_order_details_admin(setup_test_data):
    """
    Verify that the admin can observe the details of an order.
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    url = reverse("admin-orden", kwargs={"pk": order1.pk})
    response = client.get(url)

    assert response.status_code == 200

    assert "Lab Maquinas" in response.content.decode()
    assert "Resistor" in response.content.decode()
    assert "Solicitado" in response.content.decode()
    assert "Sebas" in response.content.decode()


@pytest.mark.django_db
def test_order_details_admin_prestar(setup_test_data):
    """
    Verify that the administrator can change the status of a student's
    order to "Prestado".
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    # Obtain the first ItemOrder related to order1
    item_order = ItemOrder.objects.filter(order=order1).first()

    # Create the data
    data = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '1',
        'form-MIN_NUM_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-id': str(item_order.id),
        'form-0-item': str(item_order.item.id),
        'form-0-quantity': str(item_order.quantity),
        'form-0-status': 'Prestado'
    }

    url = reverse("admin-orden", kwargs={"pk": order1.pk})
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse('administrar-ordenes')

    # Verify that the change was applied
    item_order.refresh_from_db()
    assert item_order.status == 'Prestado'


@pytest.mark.django_db
def test_order_details_admin_devuelto(setup_test_data):
    """
    Verify that the administrator can change the status of a student's
    order to "Devuelto".
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    # Obtain the first ItemOrder related to order2
    item_order = ItemOrder.objects.filter(order=order2).first()

    # Create data
    data = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '1',
        'form-MIN_NUM_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-id': str(item_order.id),
        'form-0-item': str(item_order.item.id),
        'form-0-quantity': str(item_order.quantity),
        'form-0-status': 'Devuelto'
    }

    url = reverse("admin-orden", kwargs={"pk": order1.pk})
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse('administrar-ordenes')

    # Verify that the change was applied
    item_order.refresh_from_db()
    assert item_order.status == 'Devuelto'


@pytest.mark.django_db
def test_order_details_admin_solicitado_devuelto(setup_test_data):
    """
    Verify that an item with status "Solicitado" cannot be
    changed directly to "Devuelto"
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    # Obtain the item with status "Solicitado"
    item_order = ItemOrder.objects.filter(order=order1).first()
    assert item_order.status == "Solicitado"

    # Create the data
    data = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '1',
        'form-MIN_NUM_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-id': str(item_order.id),
        'form-0-item': str(item_order.item.id),
        'form-0-quantity': str(item_order.quantity),
        'form-0-status': 'Devuelto'
    }

    url = reverse("admin-orden", kwargs={"pk": order1.pk})
    response = client.post(url, data)

    item_order.refresh_from_db()

    assert response.status_code == 302
    assert item_order.status != "Devuelto"  # Status is not Devuelto
    assert item_order.status == "Solicitado"  # Remains the same
