import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups


@pytest.mark.django_db
def test_actualizar_estudiantes_grupo(client):
    """
    Test to verify the updating of students in a group.
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

    # Create a second student
    user3 = Users.objects.create_user(
        username="student",
        email="stundet@example.com",
        password="testpass",
        role="student",
    )

    # Test data for update the students group
    data = {
        "csrfmiddlewaretoken": "testtoken",
        "student": [user3.id],
        "year": group.year,
        "term": group.term,
        "number": group.number,
        "professor": group.professor.id
    }

    # URL to create group
    url = reverse(
        "estudiantes-grupo",
        kwargs={"code": class1.code, "pk": group.id}
    )

    response = client.post(url, data)

    group.refresh_from_db()
    remaining_students = list(group.student.values_list('id', flat=True))

    assert response.status_code == 302
    assert remaining_students == [user3.id]
    assert user2.id not in remaining_students
    assert group.student.count() == 1


@pytest.mark.django_db
def test_actualizar_estudiantes_grupo_estudiante(client):
    """
    Test to verify that a student cannot update the students in a group.
    """
    # Create and authenticate teacher user
    user = Users.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass",
        role="student",
    )
    client.force_login(user)

    # Create professor user
    user2 = Users.objects.create_user(
        username="teacher",
        email="teacher@example.com",
        password="user",
        role="teacher"
    )

    # Create student user
    user3 = Users.objects.create_user(
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
        professor=user2,
        class_id=class1
    )
    group.student.set([user3])

    # Create a second student
    user4 = Users.objects.create_user(
        username="student",
        email="stundet@example.com",
        password="testpass",
        role="student",
    )

    # Test data for update the students group
    data = {
        "csrfmiddlewaretoken": "testtoken",
        "student": [user4.id],
        "year": group.year,
        "term": group.term,
        "number": group.number,
        "professor": group.professor.id
    }

    # URL to create group
    url = reverse(
        "estudiantes-grupo",
        kwargs={"code": class1.code, "pk": group.id}
    )

    response = client.post(url, data)

    assert response.status_code == 403
