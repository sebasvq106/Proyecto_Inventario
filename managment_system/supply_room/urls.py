from django.contrib.auth import views as auth_views
from django.urls import path

# importing views from views.py
from .views import (ClassCreate, ClassGroupsCreate, ClassGroupsDelete,
                    ClassGroupsList, ClassGroupStudentList, ClassGroupsUpdate,
                    ClassList, ItemCreate, ItemDelete, ItemList, OrderCreate,
                    OrderGroupList, StudentList, OrderList, OrderDetails)

urlpatterns = [
    # ------------- Articles -----------
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
    path("eliminar-articulo/<int:pk>", ItemDelete.as_view(), name="eliminar-articulo"),
    # ------------- Groups -----------
    path("cursos", ClassList.as_view(template_name="page/cursos.html"), name="cursos"),
    path(
        "cursos/<str:code>/grupos",
        ClassGroupsList.as_view(template_name="page/grupos.html"),
        name="grupos",
    ),
    path(
        "cursos/<str:code>/crear-grupo",
        ClassGroupsCreate.as_view(
            template_name="page/grupos/crear-grupo.html", success_url="grupos"
        ),
        name="crear-grupo",
    ),
    path(
        "cursos/<str:code>/editar/<pk>",
        ClassGroupsUpdate.as_view(
            template_name="page/grupos/editar-grupo.html", success_url="grupos"
        ),
        name="editar-grupo",
    ),
    path(
        "cursos/<str:code>/estudiantes/<pk>",
        ClassGroupStudentList.as_view(),
        name="estudiantes-grupo",
    ),
    path(
        "crear-curso",
        ClassCreate.as_view(
            template_name="page/crear-curso.html", success_url="cursos"
        ),
        name="crear-curso",
    ),
    path("eliminar-grupo/<int:pk>", ClassGroupsDelete.as_view(), name="eliminar-grupo"),
    # ------------- Students -----------
    path(
        "estudiantes",
        StudentList.as_view(template_name="page/estudiantes.html"),
        name="estudiantes",
    ),
    # ------------- Profile -----------
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
    # ------------- Crear Orden -----------
    path(
        "orden/grupos",
        OrderGroupList.as_view(),
        name="orden-grupos",
    ),
    path(
        "crear-orden/<pk>",
        OrderCreate.as_view(template_name="page/crear-orden.html", success_url="home"),
        name="crear-orden",
    ),
    # ------------- Mis Ordenes-----------
    path(
        "mis-ordenes",
        OrderList.as_view(),
        name="mis-ordenes",
    ),
    path(
        "orden/<pk>",
        OrderDetails.as_view(),
        name="orden",
    ),
]
