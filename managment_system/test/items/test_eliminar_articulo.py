import pytest
from django.urls import reverse
from supply_room.models import Item, Users


@pytest.mark.django_db
def test_delete_available_item(client):
    admin_user = Users.objects.create_user(
        username='admin',
        password='pass',
        role='admin'
    )
    client.force_login(admin_user)

    item = Item.objects.create(
        name="Resistencia",
        is_available=True
    )
    url = reverse("eliminar-articulo", args=[item.id])
    response = client.post(url)
    assert response.status_code == 302
    assert not Item.objects.filter(id=item.id).exists()


@pytest.mark.django_db
def test_delete_unavailable_item(client):
    admin_user = Users.objects.create_user(
        username='admin',
        password='pass',
        role='admin'
    )
    client.force_login(admin_user)

    item = Item.objects.create(
        name="Resistencia",
        is_available=False
    )
    url = reverse("eliminar-articulo", args=[item.id])

    response = client.post(url)
    assert response.status_code == 403
    assert Item.objects.filter(id=item.id).exists()
