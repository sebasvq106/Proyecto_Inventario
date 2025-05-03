import pytest
from django.urls import reverse
from supply_room.models import Class, Users, ClassGroups, StudentGroups


@pytest.mark.django_db
def test_actualizar_estudiantes_grupo(client):
    """
    Test to check the updating of students in a group
    """
    # Create and authenticate teacher user
    teacher = Users.objects.create_user(
        username="profesor_test",
        email="profesor@example.com",
        password="testpass",
        role="teacher",
    )
    client.force_login(teacher)

    # Create students
    student1 = Users.objects.create_user(
        username="estudiante1",
        email="est1@example.com",
        password="testpass",
        role="student"
    )
    student2 = Users.objects.create_user(
        username="estudiante2",
        email="est2@example.com",
        password="testpass",
        role="student"
    )

    # Create class
    class1 = Class.objects.create(name="Lab Máquinas", code="IE001")

    # Create group
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )

    # Add one student
    group.add_students([student1])

    # Verify that the data was created
    assert StudentGroups.objects.filter(group=group, student=student1).exists()
    assert group.students.count() == 1

    # POST
    data = {
        "student": [student2.id],
        "csrfmiddlewaretoken": "testtoken"
    }

    # URL
    url = reverse(
        "estudiantes-grupo",
        kwargs={"code": class1.code, "pk": group.id}
    )

    # Make POST request
    response = client.post(url, data)

    # Verifications
    group.refresh_from_db()

    assert response.status_code == 302

    # Verify that the new student was added
    assert StudentGroups.objects.filter(group=group, student=student2).exists()

    # Verificar que el estudiante no original sigue ahí
    assert group.students.count() == 1
    assert student2 in group.students.all()


@pytest.mark.django_db
def test_permisos_estudiante(client):
    """
    Test to verify that a student cannot modify groups
    """
    student = Users.objects.create_user(
        username="estudiante_test",
        email="estudiante@example.com",
        password="testpass",
        role="student",
    )
    client.force_login(student)

    teacher = Users.objects.create_user(
        username="profesor_real",
        email="prof@example.com",
        password="testpass",
        role="teacher"
    )

    class1 = Class.objects.create(name="Lab Máquinas", code="IE001")
    group = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=teacher,
        class_id=class1
    )

    url = reverse(
        "estudiantes-grupo",
        kwargs={"code": class1.code, "pk": group.id}
    )

    response = client.post(url, {"student": [student.id]})
    assert response.status_code == 403
