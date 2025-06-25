import pytest
from django.urls import reverse
from supply_room.models import Users


@pytest.mark.django_db
def test_students_teacher(client):
    """
    Test that the StudentList view renders correctly with user role teacher.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='teacher'
    )
    client.force_login(user)

    # Create test data
    Users.objects.create(
        username='student1',
        email="user1@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='student2',
        email="user2@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='student3',
        email="user3@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='teacher2',
        email="user4@example.com",
        password='user',
        role='teacher'
    )

    # Make GET request
    url = reverse("estudiantes")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 3

    # Verify class names and codes exist in the response
    student_info = {(item.username) for item in items}
    expected_students = {
        ('student1'),
        ('student2'),
        ('student3')
    }
    assert expected_students.issubset(student_info)
    assert 'teacher2' not in student_info


@pytest.mark.django_db
def test_students_admin(client):
    """
    Test that the StudentList view renders correctly with user role admin.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='admin'
    )
    client.force_login(user)

    # Create test data
    Users.objects.create(
        username='student1',
        email="user1@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='student2',
        email="user2@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='student3',
        email="user3@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='teacher2',
        email="user4@example.com",
        password='user',
        role='teacher'
    )

    # Make GET request
    url = reverse("estudiantes")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 3

    # Verify class names and codes exist in the response
    student_info = {(item.username) for item in items}
    expected_students = {
        ('student1'),
        ('student2'),
        ('student3')
    }
    assert expected_students.issubset(student_info)
    assert 'teacher2' not in student_info


@pytest.mark.django_db
def test_students_student(client):
    """
    Test that the StudentList view not renders with user role student.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='student'
    )
    client.force_login(user)

    # Create test data
    Users.objects.create(
        username='student1',
        email="user1@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='student2',
        email="user2@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='student3',
        email="user3@example.com",
        password='user',
        role='student'
    )
    Users.objects.create(
        username='teacher2',
        email="user4@example.com",
        password='user',
        role='teacher'
    )

    # Make GET request
    url = reverse("estudiantes")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 403


@pytest.mark.django_db
def test_no_students(client):
    """
    Test that the StudentList view renders correctly when no students exist.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='teacher'
    )
    client.force_login(user)

    # Make GET request
    url = reverse("estudiantes")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that no items appear in context
    context = response.context
    items = context['object_list']
    assert len(items) == 0
