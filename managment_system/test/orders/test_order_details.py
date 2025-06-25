import pytest
from django.urls import reverse
from supply_room.models import (Class, Users, ClassGroups, Order,
                                UserOrder, ItemOrder, Item)


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
def test_order_details_student(setup_test_data):
    """
    Verify that the student can observe the details of an order.
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    student1 = Users.objects.get(username="student1")
    client.force_login(student1)

    url = reverse("orden", kwargs={"pk": order1.pk})
    response = client.get(url)

    assert response.status_code == 200

    assert "Lab Maquinas" in response.content.decode()
    assert "Resistor" in response.content.decode()
    assert "Solicitado" in response.content.decode()
    assert "Sebas" in response.content.decode()


@pytest.mark.django_db
def test_order_details_teacher(setup_test_data):
    """
    Verify that the course instructor can observe the details
    of a student's order
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    teacher = Users.objects.get(username="teacher")
    client.force_login(teacher)

    url = reverse("orden", kwargs={"pk": order1.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert "Lab Maquinas" in response.content.decode()
    assert "Resistor" in response.content.decode()
    assert "Sebas" in response.content.decode()


@pytest.mark.django_db
def test_student_cannot_view_other_student_order_details(setup_test_data):
    """
    Verify that another student cannot
    see the details of another student's order
    """
    client = setup_test_data["client"]
    order1, order2, order3 = setup_test_data["orders"]

    # Switch to the second student and try to see
    # the order of the first student
    student2 = Users.objects.get(username="student2")
    client.force_login(student2)

    url = reverse("orden", kwargs={"pk": order1.pk})
    response = client.get(url)

    assert response.status_code == 403
