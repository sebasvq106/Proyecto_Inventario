import pytest
from django.urls import reverse
from supply_room.models import Class, Users


@pytest.mark.django_db
def test_crear_curso(client):
    """
    Test to verify the creation of a class.
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='teacher'
    )
    client.force_login(user)

    url = reverse('crear-curso')

    # Create test data
    data = {
        'name': 'Lab Digitales',
        'code': 'IE-001'
    }

    # Make POST request
    response = client.post(url, data)

    # Verify redirection
    assert response.status_code == 302

    # Verify that the items were created
    items = Class.objects.filter(name='Lab Digitales')
    assert items.count() == 1

    # Verify that all have the same name
    for item in items:
        assert item.name == 'Lab Digitales'
        assert item.code == 'IE-001'


@pytest.mark.django_db
def test_crear_curso_student(client):
    """
    Test to verify that the role student cannot create a course
    """
    # Create and authenticate user
    user = Users.objects.create_user(
        username='testuser',
        password='testpass',
        role='student'
    )
    client.force_login(user)

    url = reverse('crear-curso')

    # Create test data
    data = {
        'name': 'Lab Digitales',
        'code': 'IE-001'
    }

    # Make POST request
    response = client.post(url, data)

    # Verify redirection
    assert response.status_code == 403


@pytest.mark.django_db
def test_crear_curso_duplicado(client):
    """
    Test to verify that two classes cannot be created with the same data.
    """
    # Create and authenticate teacher user
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="teacher",
    )
    client.force_login(user)

    url = reverse('crear-curso')

    # Test data for creating the class
    data = {
        "name": 'Lab Micro',
        "code": 'IE-001'
    }

    # Make the POST request to create the first class
    response = client.post(url, data)

    # Check that it redirects after creation
    assert response.status_code == 302

    # Verify that the first class was created correctly
    curso = Class.objects.filter(name='Lab Micro')
    assert curso.count() == 1

    # Try to create a second class with the same data
    data = {
        "name": 'Lab Micro',
        "code": 'IE-001'
    }
    response = client.post(url, data)

    # Check that the response is 302
    assert response.status_code == 302

    # Verify that a second group was not created in the database
    curso = Class.objects.filter(name='Lab Micro')
    assert curso.count() == 1
