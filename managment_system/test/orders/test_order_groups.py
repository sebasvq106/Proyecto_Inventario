import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups


@pytest.mark.django_db
def test_order_groups_teacher(client):
    """
    Test that the OrderGroupList view renders correctly with user role teacher.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass',
        role='teacher'
    )
    client.force_login(user)

    # Create test data
    user2 = Users.objects.create_user(
        username='user',
        email='user@example.com',
        password='user',
        role='student'
    )
    user3 = Users.objects.create_user(
        username='teacher2',
        email='teacher2@example.com',
        password='teacher2',
        role='teacher'
    )
    class1 = Class.objects.create(name='Lab Maquinas', code='IE001')
    group1 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user,
        class_id=class1
    )
    group1.student.set([user2])

    group2 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user3,
        class_id=class1
    )
    group2.student.set([user2])

    # Make GET request
    url = reverse("orden-grupos")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 1

    # Verify that the group data is correct.
    group = items[0]
    assert group.semester == 'I Semestre 2025'
    assert group.class_id.name == 'Lab Maquinas'
    assert group.number == 1
    assert group.professor.username == 'testuser'


@pytest.mark.django_db
def test_order_groups_student(client):
    """
    Test that the OrderGroupList view renders correctly with user role student.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass',
        role='teacher'
    )

    # Create test data
    user2 = Users.objects.create_user(
        username='user',
        email='user@example.com',
        password='user',
        role='student'
    )

    client.force_login(user2)

    user3 = Users.objects.create_user(
        username='teacher2',
        email='teacher2@example.com',
        password='teacher2',
        role='teacher'
    )
    class1 = Class.objects.create(name='Lab Maquinas', code='IE001')
    group1 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user,
        class_id=class1
    )
    group1.student.set([user2])

    group2 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user3,
        class_id=class1
    )
    group2.student.set([user2])

    # Make GET request
    url = reverse("orden-grupos")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 2

    # Verify that the group data is correct.
    group = items[0]
    assert group.semester == 'I Semestre 2025'
    assert group.class_id.name == 'Lab Maquinas'
    assert group.number == 1
    assert group.professor.username == 'testuser'
