import pytest
from django.urls import reverse
from supply_room.models import (Class, Users, ClassGroups, Order,
                                UserOrder, ItemOrder, Item)


@pytest.fixture
def setup_test_data(client):
    admin = Users.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="adminpass",
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
def test_base_ordering(setup_test_data):
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    url = reverse("administrar-ordenes")
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    items = context['object_list']

    assert len(items) == 3
    assert items[0] == order3
    assert items[1] == order1
    assert items[2] == order2


@pytest.mark.django_db
def test_filter_pendiente(setup_test_data):
    client = setup_test_data["client"]
    order1 = setup_test_data["orders"][0]

    url = reverse("administrar-ordenes") + "?search=&status=pendiente"
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    items = context['object_list']

    assert len(items) == 1
    assert items[0] == order1


@pytest.mark.django_db
def test_filter_prestado(setup_test_data):
    client = setup_test_data["client"]
    order2 = setup_test_data["orders"][1]

    url = reverse("administrar-ordenes") + "?search=&status=prestado"
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    items = context['object_list']

    assert len(items) == 1
    assert items[0] == order2


@pytest.mark.django_db
def test_filter_completado(setup_test_data):
    client = setup_test_data["client"]
    order3 = setup_test_data["orders"][2]

    url = reverse("administrar-ordenes") + "?search=&status=completado"
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    items = context['object_list']

    assert len(items) == 1
    assert items[0] == order3


@pytest.mark.django_db
def test_search_by_class_name(setup_test_data):
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    url = reverse("administrar-ordenes") + "?search=Maquinas&status="
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    items = context['object_list']

    assert len(items) == 2
    assert order1 in items
    assert order2 in items
    assert order3 not in items


@pytest.mark.django_db
def test_search_by_student_name(setup_test_data):

    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    url = reverse("administrar-ordenes") + "?search=Sebas&status="
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    items = context['object_list']

    assert len(items) == 2
    assert order1 in items
    assert order3 in items
    assert order2 not in items
