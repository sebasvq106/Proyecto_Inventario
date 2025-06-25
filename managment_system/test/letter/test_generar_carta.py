import pytest
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
        name="Sebas",
        student_id="C18282"
    )
    student2 = Users.objects.create_user(
        username="student2",
        email="student2@example.com",
        password="student2pass",
        role="student",
        name="Luis",
        student_id="C19595"
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

    ItemOrder.objects.create(order=order1,
                             status="Prestado",
                             quantity=1,
                             item=item2
                             )

    return {
        "client": client,
        "orders": [order1, order2, order3]
    }


@pytest.mark.django_db
def test_generar_carta_student_not_found(setup_test_data):
    """
    Verify that the system correctly handles a non-existent student_code.
    """
    client = setup_test_data["client"]

    # URL with student code that does not exist
    url = "/generar-carta?student_code=C99999"

    response = client.get(url)

    # Validate that the page loads correctly
    assert response.status_code == 200

    # Validate that the error message appears in the rendered HTML
    assert "Estudiante no encontrado" in response.content.decode()


@pytest.mark.django_db
def test_generar_carta_student_without_pending_items(setup_test_data):
    """
    Verify that the student's letter 2
    indicates that he/she has no outstanding items.
    """
    client = setup_test_data["client"]

    # URL with student code 2
    url = "/generar-carta?student_code=C19595"

    response = client.get(url)

    assert response.status_code == 200

    content = response.content.decode()

    # Validate that the student's name appears
    assert "Luis" in content

    # Validate that no items are indicated as pending
    assert "no tiene artículos pendientes" in content.lower()


@pytest.mark.django_db
def test_generar_carta_student_with_pending_items(setup_test_data):
    """
    Verify that student 1 sees only borrowed items and not requested items.
    and not the requested items.
    """
    client = setup_test_data["client"]

    url = "/generar-carta?student_code=C18282"

    response = client.get(url)

    assert response.status_code == 200

    content = response.content.decode()

    # Validate that the student's name appears
    assert "Sebas" in content

    # Verify that the borrowed item appears
    assert "Capacitor" in content

    # Verify that the requested item does NOT appear.
    assert "Resistor" not in content
