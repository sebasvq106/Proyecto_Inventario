import pytest
from django.urls import reverse
from django.db.models.deletion import ProtectedError
from supply_room.models import Class, Users, ClassGroups


@pytest.mark.django_db
def test_eliminar_curso(client):
    user = Users.objects.create_user(
        username='teacher',
        password='pass',
        role='teacher'
    )
    client.force_login(user)

    curso = Class.objects.create(
        name='Lab Micro',
        code='EI-001'
    )
    url = reverse("eliminar-curso", args=[curso.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Class.objects.filter(id=curso.id).exists()


@pytest.mark.django_db
def test_eliminar_curso_grupo_activo(client):
    user = Users.objects.create_user(
        username='techar',
        password='pass',
        role='teacher'
    )

    client.force_login(user)

    user2 = Users.objects.create_user(
        username='user',
        email='user@example.com',
        password='user',
        role='student'
    )

    curso = Class.objects.create(name='Lab Maquinas', code='IE001')
    group1 = ClassGroups.objects.create(
        number=1,
        year=2025,
        term='I',
        professor=user,
        class_id=curso
    )

    group1.student.set([user2])

    url = reverse("eliminar-curso", args=[curso.id])

    try:
        client.post(url)
        pytest.fail("Expected ProtectedError, but deletion was successful")
    except ProtectedError:
        pass  # Test passes if ProtectedError is raised

    assert Class.objects.filter(id=curso.id).exists()

    with pytest.raises(ProtectedError):
        curso.delete()
