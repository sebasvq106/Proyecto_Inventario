from django.urls import path

# importing views from views.py
from .views import (
    ItemList,
    ItemCreate,
    ClassList,
    ClassCreate,
    ItemDelete,
    StudentList,
    ClassGroupsList,
    ClassGroupsCreate,
    ClassGroupsDelete, ClassGroupsUpdate,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        "articulos",
        ItemList.as_view(template_name="page/articulos.html"),
        name="articulos",
    ),
    path(
        "crear-articulo",
        ItemCreate.as_view(
            template_name="page/crear-articulo.html", success_url="articulos"
        ),
        name="crear-articulo",
    ),
    path("cursos", ClassList.as_view(template_name="page/cursos.html"), name="cursos"),
    path(
        "cursos/<str:code>/grupos",
        ClassGroupsList.as_view(template_name="page/grupos.html"),
        name="grupos",
    ),
    path(
        "cursos/<str:code>/crear-grupo",
        ClassGroupsCreate.as_view(
            template_name="page/crear-grupo.html", success_url="grupos"
        ),
        name="crear-grupo",
    ),
    path(
        "cursos/<str:code>/editar/<pk>",
        ClassGroupsUpdate.as_view(
            template_name="page/editar-grupo.html", success_url="grupos"
        ),
        name="editar-grupo",
    ),
    path(
        "estudiantes",
        StudentList.as_view(template_name="page/estudiantes.html"),
        name="estudiantes",
    ),
    path(
        "crear-curso",
        ClassCreate.as_view(
            template_name="page/crear-curso.html", success_url="cursos"
        ),
        name="crear-curso",
    ),
    path("eliminar-articulo/<int:pk>", ItemDelete.as_view(), name="eliminar-articulo"),
    path("eliminar-grupo/<int:pk>", ClassGroupsDelete.as_view(), name="eliminar-grupo"),
    path(
        "cambiar-contrasena/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html"
        ),
        name="password_change",
    ),
    path(
        "cambiar-contrasena/exitoso/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
]
