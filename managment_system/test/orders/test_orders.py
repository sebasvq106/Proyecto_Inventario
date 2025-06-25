import pytest
from django.urls import reverse
from supply_room.models import Class, ClassGroups, Order, UserOrder, Users


@pytest.mark.django_db
def test_orders_student(client):
    """
    Test that the OrderList view renders correctly with user role student.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='user',
        password='user',
        role='student'
    )
    client.force_login(user)

    # Create teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
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
    group.add_students([user])

    # Create order
    order = Order.objects.create(group=group)

    # Create user order
    UserOrder.objects.create(user=user, order=order)

    # Make GET request
    url = reverse("mis-ordenes")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['page_obj']

    # Verify the structure of the data in context
    assert len(items) == 1

    # Verify class names and codes exist in the response
    orders_info = {(item.group.class_id.name) for item in items}
    expected_orders = {
        ('Lab Maquinas')
    }
    assert expected_orders.issubset(orders_info)


@pytest.mark.django_db
def test_orders_with_two_stundets(client):
    """
    Test that the OrderList view renders correctly with two users students.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='user',
        password='user',
        role='student'
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
        username='user2',
        password='user2',
        email="user2@example.com",
        role='student'
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

    # Create order
    order = Order.objects.create(group=group)

    # Create user order for each student
    UserOrder.objects.create(user=user, order=order)
    UserOrder.objects.create(user=user2, order=order)

    # Verify for the first student
    client.force_login(user)
    response1 = client.get(reverse("mis-ordenes"))
    assert response1.status_code == 200
    page_obj1 = response1.context['page_obj']
    items1 = list(page_obj1.object_list)
    assert len(items1) == 1
    assert items1[0].group.class_id.name == "Lab Maquinas"

    # Verify for the second student
    client.force_login(user2)
    response2 = client.get(reverse("mis-ordenes"))
    assert response2.status_code == 200
    page_obj2 = response2.context['page_obj']
    items2 = list(page_obj2.object_list)
    assert len(items2) == 1
    assert items2[0].group.class_id.name == "Lab Maquinas"

    # Verify that the same order is associated to both
    assert items1[0].id == items2[0].id == order.id


@pytest.mark.django_db
def test_orders_teacher(client):
    """
    Test that the OrderList view renders correctly with user role teacher.
    """

    # Create teacher
    teacher = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )

    client.force_login(teacher)

    # Create user
    user = Users.objects.create_user(
        username='user',
        password='user',
        role='student'
    )

    # Create another user
    user2 = Users.objects.create_user(
        username='user2',
        password='user',
        email="user2@example.com",
        role='student'
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

    # Create two orders
    order1 = Order.objects.create(group=group)
    order2 = Order.objects.create(group=group)

    # Create two user orders
    UserOrder.objects.create(user=user, order=order1)
    UserOrder.objects.create(user=user2, order=order2)

    # Make GET request
    url = reverse("mis-ordenes")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['page_obj']

    # Verify the structure of the data in context
    assert len(items) == 2

    # Verify that each order has an associated student
    student_names = set()
    for order in items:
        userorders = order.userorder_set.all()
        assert userorders.count() == 1
        student_names.add(userorders.first().user.username)

    # Verify that we see both students
    assert student_names == {'user', 'user2'}

    # Verify group information
    for order in items:
        assert order.group.class_id.name == "Lab Maquinas"
        assert order.group.professor == teacher


@pytest.mark.django_db
def test_teacher_sees_only_own_group_orders(client):
    """
    Verify that a teacher only sees orders
    from groups where he/she is the teacher.
    """
    # Create a main teacher
    main_teacher = Users.objects.create_user(
        username="main_teacher",
        email="main@example.com",
        password="password123",
        role="teacher"
    )
    client.force_login(main_teacher)

    # Create another teacher
    other_teacher = Users.objects.create_user(
        username="other_teacher",
        email="other@example.com",
        password="password123",
        role="teacher"
    )

    # Create student
    student = Users.objects.create_user(
        username='student1',
        email='student1@example.com',
        password='password123',
        role='student'
    )

    # Create class
    class1 = Class.objects.create(name="Matemáticas", code="MATH101")

    # Create groups
    # 1. Main teacjer group
    main_group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=main_teacher,
        class_id=class1
    )
    main_group.add_students(student)

    # 2. Other teacher group
    other_group = ClassGroups.objects.create(
        number=2,
        year=2025,
        term='I',
        professor=other_teacher,
        class_id=class1
    )
    other_group.add_students(student)

    # Create orders
    # Order that main teacher can see
    visible_order = Order.objects.create(group=main_group)
    UserOrder.objects.create(user=student, order=visible_order)

    # Order that main teacher can't see
    hidden_order = Order.objects.create(group=other_group)
    UserOrder.objects.create(user=student, order=hidden_order)

    # Make GET request
    response = client.get(reverse("mis-ordenes"))

    assert response.status_code == 200
    page_obj = response.context['page_obj']
    items = list(page_obj.object_list)

    # Should see only 1 order
    assert len(items) == 1

    assert items[0].id == visible_order.id
    assert items[0].group.professor == main_teacher

    # Verify that main teacher are NOT viewing the other teacher's order.
    all_order_ids = [order.id for order in items]
    assert hidden_order.id not in all_order_ids

    client.force_login(other_teacher)
    other_response = client.get(reverse("mis-ordenes"))
    other_page_obj = other_response.context['page_obj']
    other_items = list(other_page_obj.object_list)
    assert len(other_items) == 1
    assert other_items[0].id == hidden_order.id
