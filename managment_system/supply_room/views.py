from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
# Create your views here.
from django.views.generic.list import ListView

from .forms import GroupForm, ItemForm, OrderForm, UpdateOrderItemForm, StudentGroupForm
from .models import Class, ClassGroups, Item, ItemOrder, Order, Users


class ItemList(ListView):

    # specify the model for list view
    model = Item
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(ItemList, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("name")
        return qs


class ItemCreate(CreateView):
    # specify the model for create view
    model = Item

    # specify the fields to be displayed
    fields = ["name"]


class ItemDelete(DeleteView):
    model = Item
    success_url = reverse_lazy("articulos")
    template_name = "page/confirm_delete.html"


class ClassList(ListView):

    # specify the model for list view
    model = Class
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(ClassList, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("name")
        return qs


class ClassCreate(CreateView):
    # specify the model for create view
    model = Class

    # specify the fields to be displayed
    fields = ["name", "code"]


class ClassGroupsList(ListView):

    # specify the model for list view
    model = ClassGroups
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        class_id = Class.objects.filter(code=self.kwargs.get("code"))
        qs = super(ClassGroupsList, self).get_queryset(*args, **kwargs)
        qs = qs.filter(class_id=class_id[0])
        qs = qs.order_by("-year", "-term")
        return qs

    def get_context_data(self, **kwargs):
        class_id = Class.objects.filter(code=self.kwargs.get("code"))
        context = super().get_context_data(**kwargs)
        context["class"] = class_id[0]
        return context


class ClassGroupsCreate(CreateView):
    # specify the model for create view
    model = ClassGroups
    form_class = GroupForm

    def form_valid(self, form):
        class_id = Class.objects.filter(code=self.kwargs.get("code"))
        form.instance.class_id = class_id[0]
        return super(ClassGroupsCreate, self).form_valid(form)


class ClassGroupsDelete(DeleteView):
    model = ClassGroups
    template_name = "page/grupos/confirm_delete_grupos.html"
    code = ""

    def get_success_url(self):
        # I cannot access the 'pk' of the deleted object here
        return reverse("grupos", kwargs={"code": self.code})

    def form_valid(self, form):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        self.code = group.class_id.code
        return super(ClassGroupsDelete, self).form_valid(form)


class ClassGroupsUpdate(UpdateView):
    model = ClassGroups
    fields = ["year", "term", "number", "professor"]
    labels = {
        "number": "Numero de Clase",
        "professor": "Profesor"
    }

    def get_success_url(self):
        # I cannot access the 'pk' of the deleted object here
        return reverse("grupos", kwargs={"code": self.kwargs["code"]})


class ClassGroupStudentList(View):
    def get(self, request, *args, **kwargs):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        print(group.class_id)
        form = StudentGroupForm(instance=group)
        return render(
            request,
            "page/grupos/estudiantes.html",
            {"object_list": group.student.all(), "form": form, 'group': group},
        )

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        form = StudentGroupForm(request.POST, instance=group)
        form.instance.class_id = group.class_id
        print(form.data)
        if form.is_valid():
            form.save()
            print('rere')
        return HttpResponseRedirect(reverse("estudiantes-grupo", kwargs=kwargs))


class StudentList(ListView):

    # specify the model for list view
    model = Users
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(StudentList, self).get_queryset(*args, **kwargs)
        qs = qs.filter(role="student")
        qs = qs.order_by("name")
        return qs


class OrderGroupList(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "page/crear-orden-grupos.html",
            {"object_list": request.user.groups.order_by("-year", "-term").all()},
        )


class OrderCreate(CreateView):
    # specify the model for create view
    model = Order
    form_class = OrderForm

    def form_valid(self, form):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        form.instance.group = group
        return super(OrderCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(OrderCreate, self).get_context_data(**kwargs)
        ctx["group"] = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        return ctx

    def get_success_url(self):
        return reverse("orden", kwargs={"pk": self.object.id})


class OrderList(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "page/mis-ordenes.html",
            {"object_list": request.user.orders.order_by("-group__year", "-group__term").all()},
        )


class AdminOrderList(ListView):
    # specify the model for list view
    model = Order
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(AdminOrderList, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("-group__year", "-group__term")
        return qs


class OrderDetails(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs["pk"])
        items = ItemOrder.objects.filter(order=order)
        return render(
            request,
            "page/orden.html",
            {"order": order, "items": items},
        )


class AdminOrderDetails(View):
    def get(self, request, *args, **kwargs):
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
        OrderItemFormSet = modelformset_factory(ItemOrder, form=UpdateOrderItemForm)
        formset = OrderItemFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
        return HttpResponseRedirect(reverse("admin-orden", kwargs=kwargs))


class ItemOrderCreate(CreateView):
    # specify the model for create view
    model = ItemOrder
    form_class = ItemForm

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        form.instance.order = order
        return super(ItemOrderCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(ItemOrderCreate, self).get_context_data(**kwargs)
        ctx["order"] = get_object_or_404(Order, pk=self.kwargs["pk"])
        return ctx

    def get_success_url(self):
        # I cannot access the 'pk' of the deleted object here
        return reverse("orden", kwargs={"pk": self.kwargs["pk"]})


class MyProfileView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "page/perfil.html",
            {"user": request.user, "grupos": request.user.groups.order_by("-year", "-term").all()},
        )

