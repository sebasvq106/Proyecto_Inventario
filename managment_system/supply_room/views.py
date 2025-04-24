import json
from django.db.models import ProtectedError
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.forms import modelformset_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
# Create your views here.
from django.views.generic.list import ListView

from .forms import (GroupForm, ItemForm, OrderForm, StudentGroupForm,
                    UpdateOrderItemForm, ItemCreateForm, CustomPasswordChangeForm)
from .models import Class, ClassGroups, Item, ItemOrder, Order, Users
from .utils import (AdminOrTeacherRoleCheck, AdminRoleCheck,
                    TeacherOrStudentRoleCheck, TeacherRoleCheck)
from collections import defaultdict
from django.contrib.auth.views import PasswordChangeView
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied


class ItemList(ListView):
    """
    ListView for Item model

    Requests Methods:
    Get: Renders list of all items
    """
    model = Item
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        """
        Overrides internal queryset to return unique items
        with their count, availability status list, and IDs.
        """
        queryset = super().get_queryset(*args, **kwargs).order_by("name")

        item_counts = defaultdict(lambda: {"name": "", "count": 0, "detalles": []})

        for item in queryset:
            item_counts[item.name]["name"] = item.name
            item_counts[item.name]["count"] += 1
            item_counts[item.name]["detalles"].append({
                "id": item.id,
                "is_available": item.is_available
            })

        items = list(item_counts.values())

        for item in items:
            item["detalles"] = json.dumps(item["detalles"])

        return items


class AvailableItemList(ListView):
    """
    ListView for Item model

    Requests Methods:
    Get: Renders list of all items, counting only available ones
    """
    model = Item
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        """
        Overrides internal queryset to return unique available items
        with their count.
        """
        queryset = super().get_queryset(*args, **kwargs).filter(is_available=True).order_by("name")

        item_counts = defaultdict(lambda: {"name": "", "count": 0})

        for item in queryset:
            item_counts[item.name]["name"] = item.name
            item_counts[item.name]["count"] += 1

        return list(item_counts.values())


class ItemCreate(AdminRoleCheck, CreateView):
    model = Item
    form_class = ItemCreateForm
    template_name = "tu_template.html"

    def form_valid(self, form):
        quantity = form.cleaned_data.get('quantity', 1)

        self.object = form.save()

        # Creamos los items adicionales
        if quantity > 1:
            for _ in range(quantity - 1):
                Item.objects.create(
                    name=form.cleaned_data['name'],
                )

        return redirect(self.get_success_url())


class ItemDelete(AdminRoleCheck, DeleteView):
    """
    DeleteView for Item model with availability check

    Requests Methods:
    Get: Render a deletion confirmation modal
    Delete: Deletes the specified Item in the db only if available
    """
    model = Item
    success_url = reverse_lazy("articulos")
    template_name = "page/confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.is_available:
            return HttpResponseForbidden("No se puede eliminar un artículo que no está disponible")

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_available:
            return HttpResponseForbidden("No se puede eliminar un artículo que no está disponible")

        return super().delete(request, *args, **kwargs)


class ClassList(AdminOrTeacherRoleCheck, ListView):
    """
    ListView for Class model

    Requests Methods:
    Get: Renders a List of all classes
    """

    # specify the model for list view
    model = Class
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        """
        Overrides internal queryset to add alphabetical ordering
        by name
        """
        qs = super(ClassList, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("name")
        return qs


class ClassCreate(TeacherRoleCheck, CreateView):
    """
    CreateView for Class model

    Requests Methods:
    Get: Render the form for Class Creation
    Post: Validates the form and saves the Class
    """

    # specify the model for create view
    model = Class

    # specify the fields to be displayed
    fields = ["name", "code"]

    def form_valid(self, form):
        """
        Validates that the class name and code are unique before saving.
        """
        name = form.cleaned_data.get("name")
        code = form.cleaned_data.get("code")

        # Check if a class with the same name and code already exists
        if Class.objects.filter(name=name, code=code).exists():
            messages.error(self.request, 'Este curso ya existe.')
            return redirect("crear-curso")  # Redirect to the class creation form

        return super().form_valid(form)


class ClassDelete(TeacherRoleCheck, DeleteView):
    """
    DeleteView for Class model

    Requests Methods:
    Get: Render a deletion confirmation modal
    Delete: Deletes the specified Class in the db
    """
    model = Class
    success_url = reverse_lazy("cursos")
    template_name = "page/eliminar-curso.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Check if there are any groups associated with this class
        if ClassGroups.objects.filter(class_id=self.object).exists():
            messages.error(request, "Este curso no se puede eliminar porque tiene grupos activos.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            return super().delete(request, *args, **kwargs)

        except ProtectedError:
            messages.error(request, "Este curso no se puede eliminar porque tiene grupos activos.")
            return redirect(self.success_url)


class ClassGroupsList(AdminOrTeacherRoleCheck, ListView):
    """
    ListView for ClassGroups

    Requests Methods:
    Get: Renders list of all ClassGroups in a specific Class

    Params (kwargs)
    :code: code of the specific class
    """

    # specify the model for list view
    model = ClassGroups
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        """
        Overrides internal queryset to only return the ClassGroups associated
        with the specific Class and add ordering by semester (term and year)
        """
        class_id = Class.objects.filter(code=self.kwargs.get("code"))
        qs = super(ClassGroupsList, self).get_queryset(*args, **kwargs)
        qs = qs.filter(class_id=class_id[0])
        qs = qs.order_by("-year", "-term")
        return qs

    def get_context_data(self, **kwargs):
        """
        Expands data send to the template

        Extra Context Data
        :class: specific Class
        """
        class_id = Class.objects.filter(code=self.kwargs.get("code"))
        context = super().get_context_data(**kwargs)
        context["class"] = class_id[0]
        return context


class ClassGroupsCreate(TeacherRoleCheck, CreateView):
    """
    CreateView for ClassGroup model

    Requests Methods:
    Get: Render the form for ClassGroup Creation
    Post: Validates the form and saves the ClassGroup

    Params (kwargs)
    :code: code of the specific class for which the ClassGroup is being created
    """

    # specify the model for create view
    model = ClassGroups
    # specify the form rendered
    form_class = GroupForm

    def form_valid(self, form):
        """
        Sets the specific class of the ClassGroup before saving and checks for duplicate group numbers
        """
        class_id = Class.objects.filter(code=self.kwargs.get("code")).first()
        group_number = form.cleaned_data.get('number')
        group_year = form.cleaned_data.get('year')
        group_term = form.cleaned_data.get('term')

        if ClassGroups.objects.filter(class_id=class_id, number=group_number, year=group_year, term=group_term).exists():
            messages.error(self.request, 'Ya existe un grupo con estas características.')
            return redirect('crear-grupo', code=self.kwargs.get("code"))

        form.instance.class_id = class_id

        return super(ClassGroupsCreate, self).form_valid(form)


class ClassGroupsDelete(TeacherRoleCheck, DeleteView):
    """
    DeleteView for ClassGroup model

    Requests Methods:
    Get: Render a deletion confirmation modal
    Delete: Deletes the specified ClassGroup in the db

    Params (kwargs)
    :code: code of the class associated to the ClassGroup that is being deleted
    :pk: primary key of the ClassGroup to be deleted
    """

    # specify the model for delete view
    model = ClassGroups
    template_name = "page/grupos/confirm_delete_grupos.html"
    # Internal variable for class code
    code = ""

    def get_success_url(self):
        """
        Calculates the successful url for redirection

        Here the information of the deleted object is no longer accessible,
        thus the need for preserving the class code in an internal variable
        """
        return reverse("grupos", kwargs={"code": self.code})

    def form_valid(self, form):
        """
        Preserves the class code before deletion
        """
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        self.code = group.class_id.code
        return super(ClassGroupsDelete, self).form_valid(form)


class ClassGroupsUpdate(TeacherRoleCheck, UpdateView):
    """
    UpdateView for ClassGroup model
    Only updates Group data

    Requests Methods:
    Get: Render the form for ClassGroup data
    Post: Validates the form and updates the ClassGroup

    Params (kwargs)
    :code: code of the class associated to the ClassGroup that is being updated
    :pk: primary key of the ClassGroup to be updated
    """

    # specify the model for update view
    model = ClassGroups
    # filter which fields are shown in the form
    fields = ["year", "term", "number", "professor"]
    labels = {"number": "Numero de Clase", "professor": "Profesor"}

    def get_success_url(self):
        """
        Calculates the successful url for redirection
        """
        return reverse("grupos", kwargs={"code": self.kwargs["code"]})


class ClassGroupStudentList(AdminOrTeacherRoleCheck, View):
    """
    Basic View for managing students of a ClassGroup

    Requests Methods:
    Get: Render a form updating the current students in the ClassGroup
    Post: Validates the form and updates the students in the ClassGroup

    Params (kwargs)
    :code: code of the class associated to the ClassGroup that is being updated
    :pk: primary key of the ClassGroup to be updated
    """
    paginate_by = 7

    def get(self, request, *args, **kwargs):
        """
        Renderiza el formulario con lista paginada de estudiantes
        """
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        class1 = group.class_id

        student_list = group.student.all().order_by('name')
        paginator = Paginator(student_list, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        form = StudentGroupForm(instance=group)

        return render(
            request,
            "page/grupos/estudiantes.html",
            {
                "page_obj": page_obj,
                "form": form,
                "group": group,
                "class1": class1,
            },
        )

    def post(self, request, *args, **kwargs):
        """
        Parses the form information and updates the students
        """
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        form = StudentGroupForm(request.POST, instance=group)

        if form.is_valid():
            students = form.cleaned_data["student"]
            group.student.set(students)
            return HttpResponseRedirect(reverse("estudiantes-grupo", kwargs=kwargs))

        return render(request, "page/grupos/estudiantes.html", {"form": form, "group": group})


class StudentList(AdminOrTeacherRoleCheck, ListView):
    """
    ListView for User model
    Only lists Users with Student Role

    Requests Methods:
    Get: Renders list of all students
    """

    # specify the model for list view
    model = Users
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        """
        Overrides internal queryset to only return students
        and order alphabetical by name
        """
        qs = super(StudentList, self).get_queryset(*args, **kwargs)
        qs = qs.filter(role="student")
        qs = qs.order_by("name")
        return qs


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "registration/password_change_form.html"
    title = _("Password change")

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        if form.errors:
            first_error = next(iter(form.errors.values()))[0]
            print("Primer error:", first_error)
            messages.error(self.request, first_error)
        return super().form_invalid(form)


class OrderGroupList(TeacherOrStudentRoleCheck, ListView):
    """
    ListView for showing a list of the current user's groups (teacher or student)

    Request Methods:
    GET: Render a paginated list of ClassGroups relevant to the user
    """

    model = ClassGroups
    template_name = "page/crear-orden-grupos.html"
    paginate_by = 10

    def get_queryset(self):
        """
        Filters ClassGroups depending on the user's role:
        - Teacher: groups where the user is the professor
        - Student: groups where the user is a member
        """
        user = self.request.user
        if user.role == "teacher":
            return ClassGroups.objects.filter(professor=user).order_by("-year", "-term")
        else:
            return user.groups.order_by("-year", "-term")


class OrderCreate(TeacherOrStudentRoleCheck, CreateView):
    """
    CreateView for Order model

    Requests Methods:
    Get: Render the form for Order Creation
    Post: Validates the form and saves the Order

    Params (kwargs)
    :pk: code of the specific ClassGroup for which the order is being created
    """

    # specify the model for create view
    model = Order
    # specify the form rendered
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        
        if not (request.user == group.professor or 
                request.user in group.student.all()):
            raise PermissionDenied()
            
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Passes the kwargs down to the form initializer
        """
        kwargs = super(OrderCreate, self).get_form_kwargs()
        kwargs.update(
            {"group_pk": self.kwargs.get("pk"), "user_pk": self.request.user.pk}
        )
        return kwargs

    def form_valid(self, form):
        """
        Processes the form when validation is successful.
        """
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        form.instance.group = group
        response = super().form_valid(form)

        is_group_order = form.cleaned_data.get('is_group_order', False)
        selected_students = form.cleaned_data.get('students', [])

        users_to_add = [self.request.user]

        if is_group_order:
            users_to_add.extend(selected_students)

        self.object.add_students(users_to_add)

        return response

    def get_context_data(self, **kwargs):
        """
        Expands data send to the template

        Extra Context Data
        :group: specific ClassGroup
        """
        ctx = super(OrderCreate, self).get_context_data(**kwargs)
        ctx["group"] = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        return ctx

    def get_success_url(self):
        """
        Calculates the successful url for redirection
        """
        return reverse("orden", kwargs={"pk": self.object.id})


class OrderList(TeacherOrStudentRoleCheck, View):
    """
    Basic View for showing the Orders related with the current User

    Requests Methods:
    Get: Renders list of all orders form the current User
    """

    def get(self, request, *args, **kwargs):
        """
        Gather the data, performs pagination and renders the template

        Context Data
        :page_obj: pagination object that contain the list of user's Orders
        """
        querySet = request.user.orders.order_by("-group__year", "-group__term")
        if self.request.user.role == "teacher":
            querySet = Order.objects.filter(
                group__professor=self.request.user, student=None
            ).order_by("-group__year", "-group__term")

        paginator = Paginator(querySet, 10)

        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        return render(
            request,
            "page/mis-ordenes.html",
            {"page_obj": page_obj},
        )


class AdminOrderList(AdminRoleCheck, ListView):
    """
    ListView for Order model

    Requests Methods:
    Get: Renders list of all Orders
    """

    # specify the model for list view
    model = Order
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        """
        Overrides internal queryset to add ordering by semester
        """
        qs = super(AdminOrderList, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("-group__year", "-group__term")
        return qs


class OrderDetails(TeacherOrStudentRoleCheck, View):
    """
    Basic View for showing the details of a specific Order

    Requests Methods:
    Get: Renders the details of a specific Order including the related Items

    Params (kwargs)
    :pk: primary key of the specific Order
    """

    def get(self, request, *args, **kwargs):
        """
        Gather the data and renders the template

        Context Data
        :order: specific Order
        :items: items from the order
        """
        order = get_object_or_404(Order, pk=kwargs["pk"])
        items = ItemOrder.objects.filter(order=order)
        return render(
            request,
            "page/orden.html",
            {"order": order, "items": items},
        )


class AdminOrderDetails(AdminRoleCheck, View):
    """
    Basic View for managing the items of an Order

    Requests Methods:
    Get: Render the details of the current Order and a formset with all the items
    Post: Validates the form and updates each item in the Order

    Params (kwargs)
    :pk: primary key of the specific Order
    """

    def get(self, request, *args, **kwargs):
        """
        Gather the data, creates the formset and renders the template

        Context Data
        :order: specific Order
        :forms: formset containing all the individual item forms
        :data: custom object that have each item form with the item name value
        """
        order = get_object_or_404(Order, pk=kwargs["pk"])
        items = ItemOrder.objects.filter(order=order)
        OrderItemFormSet = modelformset_factory(
            ItemOrder, form=UpdateOrderItemForm, extra=0
        )
        forms = OrderItemFormSet(queryset=ItemOrder.objects.filter(order=order))
        data = [
            {"name": items[i].item.name, "form": forms[i]} for i in range(len(items))
        ]
        return render(
            request,
            "page/administrar-orden.html",
            {"order": order, "forms": forms, "data": data},
        )

    def post(self, request, *args, **kwargs):
        """
        Parses the formset information and updates the items in Order
        """
        OrderItemFormSet = modelformset_factory(ItemOrder, form=UpdateOrderItemForm)
        formset = OrderItemFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
        return HttpResponseRedirect(reverse("admin-orden", kwargs=kwargs))


class ItemOrderCreate(TeacherOrStudentRoleCheck, CreateView):
    """
    CreateView for ItemOrder model

    Requests Methods:
    Get: Render the form for ItemOrder Creation
    Post: Validates the form and saves the ItemOrder

    Params (kwargs)
    :pk: code of the specific Order for which the ItemOrder is being created
    """

    # specify the model for create view
    model = ItemOrder
    # specify the form rendered
    form_class = ItemForm

    def form_valid(self, form):
        """
        Sets the specific Order of the ItemOrder before saving
        """
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        form.instance.order = order
        return super(ItemOrderCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Expands data send to the template

        Extra Context Data
        :order: specific Order
        """
        ctx = super(ItemOrderCreate, self).get_context_data(**kwargs)
        ctx["order"] = get_object_or_404(Order, pk=self.kwargs["pk"])
        return ctx

    def get_success_url(self):
        """
        Calculates the successful url for redirection
        """
        return reverse("orden", kwargs={"pk": self.kwargs["pk"]})


class MyProfileView(View):
    """
    Basic View for showing the User's Profile information and related Groups

    Requests Methods:
    Get: Render the details of the current User and the related Groups
    """

    def get(self, request, *args, **kwargs):
        """
        Gather the data and renders the template

        Context Data
        :user: current user
        :grupos: all groups related to the user ordered by semester
        """
        return render(
            request,
            "page/perfil.html",
            {
                "user": request.user,
                "grupos": request.user.groups.order_by("-year", "-term").all(),
            },
        )
