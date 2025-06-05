import json
from django.db.models import ProtectedError
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.forms import ValidationError, modelformset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
# Create your views here.
from django.views.generic.list import ListView

from .forms import (GroupForm, ItemForm, OrderForm, StudentGroupForm,
                    UpdateOrderItemForm, ItemCreateForm, CustomPasswordChangeForm,
                    UsersRegistrationForm)
from .models import Class, ClassGroups, Item, ItemOrder, Order, StudentGroups, UserOrder, Users
from .utils import (AdminOrTeacherRoleCheck, AdminRoleCheck,
                    TeacherOrStudentRoleCheck, TeacherRoleCheck)
from collections import defaultdict
from django.contrib.auth.views import PasswordChangeView
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Exists, OuterRef
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.generic import TemplateView


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
                "code": item.code,
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
    success_url = reverse_lazy("articulos")

    def form_valid(self, form):
        quantity = form.cleaned_data.get('quantity', 1)
        has_code = form.cleaned_data.get('has_code')
        start_code = form.cleaned_data.get('start_code')
        name = form.cleaned_data.get('name')

        self.object = form.save()

        for i in range(1, quantity):
            item_data = {'name': name}
            if has_code:
                item_data['code'] = start_code + i
            Item.objects.create(**item_data)

        if has_code:
            self.object.code = start_code
            self.object.save()

        return redirect(self.success_url)

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


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
    model = ClassGroups
    template_name = "page/grupos/confirm_delete_grupos.html"
    code = ""

    def get_success_url(self):
        return reverse("grupos", kwargs={"code": self.code})

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        self.code = group.class_id.code

        if StudentGroups.objects.filter(group=group).exists():
            messages.error(request, "No se puede eliminar el grupo porque tiene estudiantes asociados.")
            return render(request, self.template_name, {"object": group})

        return super().post(request, *args, **kwargs)


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

        current_students = group.students.all()

        form = StudentGroupForm(group=group)

        student_list = current_students.order_by('name')
        paginator = Paginator(student_list, self.paginate_by)
        page_obj = paginator.get_page(request.GET.get('page'))

        return render(request, "page/grupos/estudiantes.html", {
            'form': form,
            'group': group,
            'class1': group.class_id,
            'page_obj': page_obj,
            'current_students': current_students
        })

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        form = StudentGroupForm(request.POST, group=group)

        if form.is_valid():
            try:
                form.save()
                return redirect("estudiantes-grupo", code=group.class_id.code, pk=group.pk)
            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
        else:
            messages.error(request, "Error en el formulario")

        student_list = group.students.order_by('name')
        paginator = Paginator(student_list, self.paginate_by)
        page_obj = paginator.get_page(request.GET.get('page'))

        return render(request, "page/grupos/estudiantes.html", {
            'form': form,
            'group': group,
            'class1': group.class_id,
            'page_obj': page_obj
        })


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
            return ClassGroups.objects.filter(
                professor=user
            ).select_related(
                'class_id', 'professor'
            ).order_by("-year", "-term")
        else:

            return ClassGroups.objects.filter(
                studentgroups__student=user
            ).select_related(
                'class_id', 'professor'
            ).distinct().order_by("-year", "-term")


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
                StudentGroups.objects.filter(group=group, student=request.user).exists()):
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
    OrderList for Order model

    Requests Methods:
    Get: List of all requests from a user (student) or a group (teacher).
    """

    def get(self, request, *args, **kwargs):
        # Students
        if request.user.role == "student":
            user_orders = UserOrder.objects.filter(
                user=request.user
            ).select_related(
                'order__group',
                'order__group__class_id'
            ).order_by("-order__group__year", "-order__group__term")

            orders_list = [uo.order for uo in user_orders]
            querySet = orders_list

        # Teachers
        elif request.user.role == "teacher":
            querySet = Order.objects.filter(
                group__professor=request.user
            ).select_related(
                'group',
                'group__class_id'
            ).prefetch_related(
                'userorder_set__user'
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
    View for listing orders with filtering by status,
    search and filtering by user
    """

    model = Order
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Base ordering
        queryset = queryset.order_by("-group__year", "-group__term")

        # Filter by status
        status = self.request.GET.get('status')
        if status in ['pendiente', 'prestado', 'completado']:
            queryset = queryset.annotate(
                has_pendiente=Exists(
                    ItemOrder.objects.filter(
                        order=OuterRef('pk'),
                        status="Solicitado"
                    )
                ),
                has_prestado=Exists(
                    ItemOrder.objects.filter(
                        order=OuterRef('pk'),
                        status="Prestado"
                    )
                )
            )

            if status == 'pendiente':
                queryset = queryset.filter(has_pendiente=True)
            elif status == 'prestado':
                queryset = queryset.filter(has_prestado=True)
            elif status == 'completado':
                queryset = queryset.filter(has_pendiente=False, has_prestado=False)

        # Text search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(group__class_id__name__icontains=search) |
                Q(group__class_id__code__icontains=search) |
                Q(userorder__user__name__icontains=search) |
                Q(userorder__user__email__icontains=search) |
                Q(userorder__user__student_id__icontains=search)
            ).distinct()

        # Query optimization
        queryset = queryset.select_related(
            'group',
            'group__class_id',
            'group__professor'
        ).prefetch_related(
            'userorder_set__user'
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_search': self.request.GET.get('search', ''),
            'current_status': self.request.GET.get('status', ''),
            'current_user': self.request.GET.get('user', ''),
        })
        return context


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

        if request.user.role == 'student':
            if not UserOrder.objects.filter(order=order, user=request.user).exists():
                raise PermissionDenied("No tienes permiso para ver esta orden")

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
        order = get_object_or_404(Order, pk=kwargs["pk"])
        OrderItemFormSet = modelformset_factory(
            ItemOrder,
            form=UpdateOrderItemForm,
            extra=0
        )
        formset = OrderItemFormSet(request.POST, queryset=ItemOrder.objects.filter(order=order))

        if formset.is_valid():
            try:
                with transaction.atomic():
                    formset.save()
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario")

        return redirect("administrar-ordenes")


class ItemOrderCreate(TeacherOrStudentRoleCheck, CreateView):
    """
    CreateView for ItemOrder model with improved error handling
    """
    model = ItemOrder
    form_class = ItemForm

    def form_valid(self, form):
        """
        Sets the specific Order of the ItemOrder before saving
        """
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        form.instance.order = order
        form.instance.request_date = timezone.now()
        try:
            return super().form_valid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Handles invalid form submission with proper error messages
        """

        if '__all__' in form.errors:
            for error in form.errors['__all__']:
                messages.error(self.request, error)

        for field, errors in form.errors.items():
            if field != '__all__':
                for error in errors:
                    messages.error(self.request, f"{form.fields[field].label}: {error}")

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Expands data sent to the template
        """
        ctx = super().get_context_data(**kwargs)
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


class ItemSearchView(View):
    '''
    Search filter items by letters and return a jason
    '''
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')

        items = (
            Item.objects
            .filter(name__icontains=query, is_available=True)
            .order_by('name')
            .distinct('name')
        )[:20]

        results = [{
            'id': item.id,
            'text': item.name
        } for item in items]

        return JsonResponse({
            'results': results,
            'pagination': {'more': False}
        })


class GenerateLetter(TemplateView):
    """
    View to generate a letter with information of items borrowed by a student.
    GET: Displays the student's data and outstanding items if the code is valid.
    POST: Sends an email to the student (and an additional recipient) with their loan status.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to search for a student by their code and list their pending items.
        """
        # The student's code is extracted from the GET parameters.
        student_code = request.GET.get('student_code')
        context = {}

        if student_code:
            try:
                # Search for the student by their unique code
                student = Users.objects.get(student_id=student_code)

                # Get backordered items (status = 'Prestado')
                pending_items = ItemOrder.objects.filter(
                    order__userorder__user=student,
                    status='Prestado'
                ).select_related(
                    'order__group__class_id',
                    'item',
                    'order__group__professor'
                ).order_by(
                    'order__group__class_id__name',
                    'item__name'
                )

                # The context for rendering the information in the template is updated.
                context.update({
                    'student': student,
                    'pending_items': pending_items,
                    'search_performed': True,
                    'error': None
                })
            except Users.DoesNotExist:
                # If the code does not correspond to any student
                context.update({
                    'error': "Estudiante no encontrado. Verifica el código de estudiante.",
                    'search_performed': True
                })
            except Exception as e:
                context.update({
                    'error': f"Error en la búsqueda: {str(e)}",
                    'search_performed': True
                })

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to send an email to the student.
        Determines which template to use in the mail depending on whether or not you have outstanding items.
        """
        try:
            # A JSON is expected in the body of the POST.
            data = json.loads(request.body)

            student_id = data.get('student_id')
            extra_email = data.get('extra_email')

            student = Users.objects.get(id=student_id)

            pending_items = ItemOrder.objects.filter(
                order__userorder__user=student,
                status='Prestado'
            ).select_related('item')

            # Choose the template and subject of the mail according to whether there are pending articles
            if pending_items.exists():
                subject = "Recordatorio de artículos pendientes"
                template = "correos/pending_items.html"
            else:
                subject = "Confirmación de devolución completa"
                template = "correos/no_pending_items.html"

            message = render_to_string(template, {
                'student': student,
                'pending_items': pending_items,
            })

            # The administrator's email that you are sending
            from_email = request.user.email
            recipient_list = [student.email]
            if extra_email:
                recipient_list.append(extra_email)

            # Send mail
            send_mail(subject, '', from_email, recipient_list, html_message=message)

            return JsonResponse({'status': 'success'})

        except Users.DoesNotExist:
            return JsonResponse({'error': 'Estudiante no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class = UsersRegistrationForm
    success_url = reverse_lazy("login")
