import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups, Order, UserOrder


@pytest.mark.django_db
def test_crear_orden_individual(client):
    """
    Test to verify the correct creation of an individual order.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="student",
    )
    client.force_login(user)

    # Create teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )

    # Create another student
    user2 = Users.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="user2",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # Create group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )
    group.add_students([user, user2])  # Both students in the group

    # Data
    data = {
        "is_group_order": False,
        "students": []
    }

    # URL
    url = reverse("crear-orden", kwargs={"pk": group.id})

    # POST
    response = client.post(url, data)

    assert response.status_code == 302

    # Verify that the order was created
    order = Order.objects.last()
    assert order is not None
    assert order.group == group

    # Verificar que solo hay una UserOrder asociada
    user_orders = UserOrder.objects.filter(order=order)
    assert user_orders.count() == 1

    # Verify that there is only one UserOrder associated with it
    user_order = user_orders.first()
    assert user_order.user == user
    assert user_order.order == order

    # Verify that the other student is NOT a partner
    assert not UserOrder.objects.filter(order=order, user=user2).exists()


@pytest.mark.django_db
def test_crear_orden_grupal(client):
    """
    Test to verify the correct creation of a group order.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="student",
    )
    client.force_login(user)

    # Create teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )

    # Create another student
    user2 = Users.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="user2",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # Crear group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )
    group.add_students([user, user2])

    # Data
    data = {
        "is_group_order": True,
        "students": [user2.id]
    }

    # URL
    url = reverse("crear-orden", kwargs={"pk": group.id})

    # POST
    response = client.post(url, data)

    assert response.status_code == 302

    # Verify that the order was created
    order = Order.objects.last()
    assert order is not None
    assert order.group == group

    # Verify that there are two users on the same order
    user_orders = UserOrder.objects.filter(order=order)
    assert user_orders.count() == 2

    user_order = user_orders.first()
    assert user_order.user == user
    assert user_order.order == order


@pytest.mark.django_db
def test_no_crear_orden_en_grupo_ajeno(client):
    """
    Test to verify that a user cannot create an order in a group
    to which he/she does not belong, either as a student or as a teacher.
    """
    # Create and authenticate user who does not belong to the group
    outsider = Users.objects.create_user(
        username="outsider",
        email="outsider@example.com",
        password="testpass",
        role="student",
    )
    client.force_login(outsider)

    # Create group owner teacher
    group_teacher = Users.objects.create_user(
        username="groupteacher",
        email="teacher@example.com",
        password="teacherpass",
        role="teacher"
    )

    # Create student who does belong to the group
    group_student = Users.objects.create_user(
        username="groupstudent",
        email="student@example.com",
        password="studentpass",
        role="student"
    )

    # Create class
    course = Class.objects.create(name="Lab Máquinas", code="IE001")

    # Create group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=group_teacher,
        class_id=course
    )
    group.add_students([group_student])  # Only group_student belongs to

    # Data
    order_data = {
        "is_group_order": False,
        "students": []
    }

    # URL
    url = reverse("crear-orden", kwargs={"pk": group.id})

    # POST
    response = client.post(url, order_data)

    assert response.status_code == 403

    # Verify that NO order was created
    assert Order.objects.count() == 0

    # Verify that no UserOrders have been created
    assert UserOrder.objects.count() == 0


@pytest.mark.django_db
def test_crear_orden_individual_profesor(client):
    """
    Test to verify the correct creation of an individual order
    as a teacher.
    """
    # Create teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )

    client.force_login(teacher)

    # Create student
    user2 = Users.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="user2",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # Create group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )
    group.add_students([user2])

    # Data
    data = {
        "is_group_order": False,
        "students": []
    }

    # URL
    url = reverse("crear-orden", kwargs={"pk": group.id})

    # POST
    response = client.post(url, data)

    assert response.status_code == 302

    # Verificar que se creó la orden
    order = Order.objects.last()
    assert order is not None
    assert order.group == group

    # Verify that there is only one UserOrder associated with it
    user_orders = UserOrder.objects.filter(order=order)
    assert user_orders.count() == 1

    # Verify that the UserOrder is only for the current user
    user_order = user_orders.first()
    assert user_order.user == teacher
    assert user_order.order == order

    # Verify that the other student is NOT a partner
    assert not UserOrder.objects.filter(order=order, user=user2).exists()


@pytest.mark.django_db
def test_crear_orden_grupal_profesor(client):
    """
    Test to verify the correct creation of an individual order
    as a teacher.
    """
    # Create a teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )
    client.force_login(teacher)

    # Crear student
    user2 = Users.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="user2",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # Create group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )
    group.add_students([user2])

    # Data
    data = {
        "is_group_order": True,
        "students": [user2.id]
    }

    # URL
    url = reverse("crear-orden", kwargs={"pk": group.id})

    # POST
    response = client.post(url, data)

    assert response.status_code == 302

    # Verify that the order was created
    order = Order.objects.last()
    assert order is not None
    assert order.group == group

    # Verify that there are two users associated to the same order
    user_orders = UserOrder.objects.filter(order=order)
    assert user_orders.count() == 2

    user_order = user_orders.first()
    assert user_order.user == teacher
    assert user_order.order == order


@pytest.mark.django_db
def test_crear_orden_grupal_sin_estudiantes(client):
    """
    Test to verify that you cannot create an order
    without adding students in a group order.
    """
    # Create student
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="student",
    )
    client.force_login(user)

    # Create teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )

    # Crear another student
    user2 = Users.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="user2",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # Create group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )
    group.add_students([user, user2])

    # Data
    data = {
        "is_group_order": True,
        "students": []
    }

    # URL
    url = reverse("crear-orden", kwargs={"pk": group.id})

    # POST
    response = client.post(url, data)

    assert response.status_code == 200

    # Verify that NO order was created
    assert Order.objects.count() == 0

    # Verify that no UserOrders have been created
    assert UserOrder.objects.count() == 0
