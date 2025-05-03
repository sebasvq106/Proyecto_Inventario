from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import TemplateView

from .views import (AdminOrderDetails, AdminOrderList, ClassCreate, ClassDelete,
                    ClassGroupsCreate, ClassGroupsDelete, ClassGroupsList,
                    ClassGroupStudentList, ClassGroupsUpdate, ClassList,
                    ItemCreate, ItemDelete, ItemList, AvailableItemList, ItemOrderCreate,
                    MyProfileView, OrderCreate, OrderDetails, OrderGroupList,
                    OrderList, StudentList, CustomPasswordChangeView)

urlpatterns = [
    # ------------- Articles -----------
    path(
        "articulos",
        ItemList.as_view(template_name="page/articulos.html"),
        name="articulos",
    ),
    path(
        "articulos-disponibles",
        AvailableItemList.as_view(template_name="page/articulos-disponibles.html"),
        name="articulos-disponibles",
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
    path("eliminar-curso/<int:pk>", ClassDelete.as_view(), name="eliminar-curso"),
    path(
        "cursos/<str:code>/editar/<pk>",
        ClassGroupsUpdate.as_view(
            template_name="page/grupos/editar-grupo.html", success_url="grupos"
        ),
        name="editar-grupo",
    ),
    path(
        "cursos/<str:code>/estudiantes/<int:pk>",
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
        CustomPasswordChangeView.as_view(
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
        OrderGroupList.as_view(template_name="page/crear-orden-grupos.html"),
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
    path(
        "orden/<pk>/articulo",
        ItemOrderCreate.as_view(template_name="page/crear-orden-articulo.html"),
        name="orden-articulo",
    ),
    # ------------- Administrar Ordenes -----------
    path(
        "administrar-ordenes",
        AdminOrderList.as_view(template_name="page/administrar-ordenes.html"),
        name="administrar-ordenes",
    ),
    path(
        "administrar-ordenes/orden/<pk>",
        AdminOrderDetails.as_view(),
        name="admin-orden",
    ),
    # ------------- Perfil -----------
    path(
        "mi-perfil",
        MyProfileView.as_view(),
        name="perfil",
    ),
    # ------------- Contacto ---------
    path(
        "contacto",
        TemplateView.as_view(template_name="page/contacto.html"),
        name="contacto",
    ),
]
