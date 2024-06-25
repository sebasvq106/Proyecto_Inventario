from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
# Create your views here.
from django.views.generic.list import ListView

from .forms import GroupForm, OrderForm
from .models import Class, ClassGroups, Item, Order, Users


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
    fields = ["semester", "number", "professor"]

    def get_success_url(self):
        # I cannot access the 'pk' of the deleted object here
        return reverse("grupos", kwargs={"code": self.kwargs["code"]})


class ClassGroupStudentList(View):
    def get(self, request, *args, **kwargs):
        group = get_object_or_404(ClassGroups, pk=self.kwargs["pk"])
        return render(
            request,
            "page/grupos/estudiantes.html",
            {"object_list": group.student.all()},
        )


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
        print(request.user)
        return render(
            request,
            "page/crear-orden-grupos.html",
            {"object_list": request.user.groups.all()},
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
