import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups


@pytest.mark.django_db
def test_crear_grupo(client):
    """
    Test to verify the creation of a class group.
    """
    # Create and authenticate teacher user
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="teacher",
    )
    client.force_login(user)

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # URL to create group
    url = reverse("crear-grupo", kwargs={"code": class1.code})

    # Test data for creating the group
    data = {
        "number": 1,
        "year": 2025,
        "term": "I",
        "professor": user.id,
        "class_id": class1.id,
    }

    # Make the POST request
    response = client.post(url, data)

    # Check that it redirects after creation
    assert response.status_code == 302

    # Verify that the group was created correctly
    grupo = ClassGroups.objects.filter(number=1, class_id=class1)
    assert grupo.count() == 1

    # Get the newly created group
    grupo = grupo.first()

    # Verify that the group data is correct
    assert grupo.number == 1
    assert grupo.year == 2025
    assert grupo.term == "I"
    assert grupo.professor == user
    assert grupo.class_id == class1


@pytest.mark.django_db
def test_crear_grupo_duplicado(client):
    """
    Test to verify that two groups cannot be created with the same data.
    """
    # Create and authenticate teacher user
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="teacher",
    )
    client.force_login(user)

    # Create student user
    user2 = Users.objects.create_user(
        username="user",
        email="user@example.com",
        password="user",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Maquinas", code="IE001")

    # URL to create group
    url = reverse("crear-grupo", kwargs={"code": class1.code})

    # Test data for creating the group
    data = {
        "number": 1,
        "year": 2025,
        "term": "I",
        "professor": user.id,
        "class_id": class1.id,
        "student": [user2.id],
    }

    # Make the POST request to create the first group
    response = client.post(url, data)

    # Check that it redirects after creation
    assert response.status_code == 302

    # Verify that the first group was created correctly
    grupo = ClassGroups.objects.filter(number=1, class_id=class1)
    assert grupo.count() == 1

    # Try to create a second group with the same number for the same course
    data = {
        "number": 1,
        "year": 2025,
        "term": "I",
        "professor": user.id,
        "class_id": class1.id,
        "student": [user2.id],
    }
    response = client.post(url, data)

    # Check that the response is 302
    assert response.status_code == 302

    # Verify that a second group was not created in the database
    grupo_count = ClassGroups.objects.filter(number=1, class_id=class1).count()
    assert grupo_count == 1  # There should only be one group with that number
