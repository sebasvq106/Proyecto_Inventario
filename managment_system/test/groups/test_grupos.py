import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups


@pytest.mark.django_db
def test_groups_teacher(client):
    """
    Test that the ClassGroupList view renders correctly with user role teacher.
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
    class1 = Class.objects.create(name='Lab Maquinas', code='IE001')
    group1 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user,
        class_id=class1
    )

    group1.add_students([user2])

    # Make GET request
    url = reverse("grupos", kwargs={"code": class1.code})
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
    assert group.number == 1
    assert group.year == 2025
    assert group.term == 'I'
    assert group.professor.username == 'testuser'
    assert group.class_id.name == 'Lab Maquinas'
    assert group.class_id.code == 'IE001'

    # Verify that the student is in the group
    student_names = [student.username for student in group.students.all()]
    assert 'user' in student_names


@pytest.mark.django_db
def test_groups_admin(client):
    """
    Test that the ClassGroupList view renders correctly with user role admin.
    """
    # Create and authenticate user
    user1 = Users.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass',
        role='admin'
    )
    client.force_login(user1)

    # Create test data
    user2 = Users.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass',
        role='teacher'
    )
    user3 = Users.objects.create_user(
        username='user',
        email='user@example.com',
        password='user',
        role='student'
    )
    class1 = Class.objects.create(name='Lab Maquinas', code='IE001')
    group1 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user2,
        class_id=class1
    )

    group1.add_students([user3])

    # Make GET request
    url = reverse("grupos", kwargs={"code": class1.code})
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
    assert group.number == 1
    assert group.year == 2025
    assert group.term == 'I'
    assert group.professor.username == 'testuser'
    assert group.class_id.name == 'Lab Maquinas'
    assert group.class_id.code == 'IE001'

    # Verify that the student is in the group
    student_names = [student.username for student in group.students.all()]
    assert 'user' in student_names


@pytest.mark.django_db
def test_groups_student(client):
    """
    Test that the ClassGroupList view not renders with user role student.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='ejemplo',
        password='ejemplo',
        role='student'
    )
    client.force_login(user)

    # Create test data
    user2 = Users.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass',
        role='teacher'
    )
    user3 = Users.objects.create_user(
        username='user',
        email='user@example.com',
        password='user',
        role='student'
    )
    class1 = Class.objects.create(name='Lab Maquinas', code='IE001')
    group1 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user2,
        class_id=class1
    )

    group1.add_students([user3])

    # Make GET request
    url = reverse("grupos", kwargs={"code": class1.code})
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 403
