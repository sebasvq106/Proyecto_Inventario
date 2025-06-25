import pytest
from django.urls import reverse
from supply_room.models import ClassGroups, Users, Class
from django.contrib.messages import get_messages


@pytest.mark.django_db
def test_teacher_can_delete_group_without_students(client):
    """
    Verifica que un profesor pueda eliminar un
    grupo que no tiene estudiantes asociados.
    """
    # Crear un profesor y login
    teacher = Users.objects.create_user(
        username="teacher1", email="teacher1@example.com",
        password="teacherpass", role="teacher"
    )
    client.force_login(teacher)

    # Crear clase y grupo sin estudiantes
    clase = Class.objects.create(name="Electrónica", code="IE123")
    grupo = ClassGroups.objects.create(
        number=1, year=2025, term='I', professor=teacher, class_id=clase
    )

    url = reverse("eliminar-grupo", kwargs={"pk": grupo.pk})
    response = client.post(url)

    # El grupo debe eliminarse y redirigir
    assert response.status_code == 302
    assert not ClassGroups.objects.filter(pk=grupo.pk).exists()


@pytest.mark.django_db
def test_teacher_cannot_delete_group_with_students(client):
    """
    Verifica que no se pueda eliminar un grupo que tiene estudiantes asociados.
    """
    # Crear profesor y estudiante
    teacher = Users.objects.create_user(
        username="teacher2", email="teacher2@example.com",
        password="teacherpass", role="teacher"
    )
    student = Users.objects.create_user(
        username="student", email="student@example.com",
        password="studentpass", role="student"
    )
    client.force_login(teacher)

    # Crear clase y grupo
    clase = Class.objects.create(name="Digitales", code="IE456")
    grupo = ClassGroups.objects.create(
        number=2, year=2025, term='II', professor=teacher, class_id=clase
    )

    # Asociar estudiante al grupo
    grupo.add_students([student])

    url = reverse("eliminar-grupo", kwargs={"pk": grupo.pk})
    response = client.post(url)

    # El grupo no debe eliminarse
    assert response.status_code == 200  # Se queda en la misma vista
    assert ClassGroups.objects.filter(pk=grupo.pk).exists()

    # Verificar que el mensaje de error esté presente
    messages = list(get_messages(response.wsgi_request))
    assert any("no se puede eliminar el grupo" in str(
        message).lower() for message in messages)
