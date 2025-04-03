import pytest
from django.urls import reverse
from supply_room.models import Class, Users


@pytest.mark.django_db
def test_class_teacher(client):
    """
    Test that the ClassList view renders correctly with user role teacher.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='teacher'
    )
    client.force_login(user)

    # Create test data
    Class.objects.create(name='Lab Maquinas', code='IE001')
    Class.objects.create(name='Lab Digitales', code='IE002')
    Class.objects.create(name='Lab Micro', code='IE003')

    # Make GET request
    url = reverse("cursos")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 3

    # Verify class names and codes exist in the response
    class_info = {(item.name, item.code) for item in items}
    expected_classes = {
        ('Lab Maquinas', 'IE001'),
        ('Lab Digitales', 'IE002'),
        ('Lab Micro', 'IE003')
    }
    assert expected_classes.issubset(class_info)


@pytest.mark.django_db
def test_class_admin(client):
    """
    Test that the ClassList view renders correctly with user role admin.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='admin'
    )
    client.force_login(user)

    # Create test data
    Class.objects.create(name='Lab Maquinas', code='IE001')
    Class.objects.create(name='Lab Digitales', code='IE002')
    Class.objects.create(name='Lab Micro', code='IE003')

    # Make GET request
    url = reverse("cursos")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that items appear in context
    context = response.context
    items = context['object_list']

    # Verify the structure of the data in context
    assert len(items) == 3

    # Verify class names and codes exist in the response
    class_info = {(item.name, item.code) for item in items}
    expected_classes = {
        ('Lab Maquinas', 'IE001'),
        ('Lab Digitales', 'IE002'),
        ('Lab Micro', 'IE003')
    }
    assert expected_classes.issubset(class_info)


@pytest.mark.django_db
def test_class_student(client):
    """
    Test that the ClassList view renders correctly with user role student.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='student'
    )
    client.force_login(user)

    # Create test data
    Class.objects.create(name='Lab Maquinas', code='IE001')
    Class.objects.create(name='Lab Digitales', code='IE002')
    Class.objects.create(name='Lab Micro', code='IE003')

    # Make GET request
    url = reverse("cursos")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 403


@pytest.mark.django_db
def test_no_classes(client):
    """
    Test that the ClassList view renders correctly when no classes exist.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='teacher'
    )
    client.force_login(user)

    # Make GET request
    url = reverse("cursos")
    response = client.get(url)

    # Verify HTML response
    assert response.status_code == 200

    # Verify that no items appear in context
    context = response.context
    items = context['object_list']
    assert len(items) == 0
