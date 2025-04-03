import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups


@pytest.mark.django_db
def test_actualizar_grupo(client):
    """
    Test to verify the update of a class group.
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

    # Create Group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user,
        class_id=class1
    )
    group.student.set([user2])

    # Create a second professor
    user3 = Users.objects.create_user(
        username="professor",
        email="professor@example.com",
        password="testpass",
        role="teacher",
    )

    # Test data for update the group
    data = {
        "number": 2,
        "year": 2025,
        "term": "II",
        "professor": user3.id,
        "class_id": class1.id
    }
    # URL to create group
    url = reverse("editar-grupo", kwargs={"code": class1.code, "pk": group.id})

    # Make the POST request
    response = client.post(url, data)

    # Check that it redirects after creation
    assert response.status_code == 302

    # Verify that the group was update correctly
    group = ClassGroups.objects.get(id=group.id)

    # Verify that the group data is correct
    assert group.number == 2
    assert group.year == 2025
    assert group.term == "II"
    assert group.professor == user3
    assert group.class_id == class1

    # Verify that the student is in the group
    student_ids = list(group.student.values_list("id", flat=True))
    assert user2.id in student_ids
