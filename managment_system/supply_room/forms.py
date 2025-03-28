from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django_select2 import forms as s2forms

from .models import ClassGroups, ItemOrder, Order, Users, Item


class ItemCreateForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={
            'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
        })
    )

    class Meta:
        model = Item
        fields = ['name']
        labels = {
            'name': 'Nombre'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
            })
        }


class RegistrationForm(UserCreationForm):
    """
    Form for user creation
    """

    email = forms.EmailField(
        required=False, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "id": "password-input"}
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    # Add an additional field for password strength
    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Users
        fields = ("username", "email", "role", "student_id", "name")


class StudentWidget(s2forms.Select2MultipleWidget):
    """
    Widget that allows the multiple selection and search of Students

    Documentation: https://django-select2.readthedocs.io/en/latest/django_select2.html
    """

    search_fields = [
        "name__icontains",
        "email__icontains",
    ]


class ItemWidget(s2forms.Select2Widget):
    """
    Widget that allows the selection and search of Items

    Documentation: https://django-select2.readthedocs.io/en/latest/django_select2.html
    """

    search_fields = [
        "name__icontains",
    ]


class GroupForm(forms.ModelForm):
    """
    From to create ClassGroups
    """

    class Meta:
        model = ClassGroups
        fields = ["year", "term", "number", "professor", "student"]
        widgets = {"student": StudentWidget}  # use custom widget for students

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        # update form choices with only students or teachers in each field
        self.fields["student"].queryset = Users.objects.filter(role="student")
        self.fields["professor"].queryset = Users.objects.filter(role="teacher")


class StudentGroupForm(forms.ModelForm):
    """
    Form to modify the students in a GlassGroup
    """

    class Meta:
        model = ClassGroups
        fields = ["year", "term", "number", "professor", "student"]
        widgets = {
            "student": StudentWidget,  # use custom widget for students
            # fields with hidden inputs so the data is in the form but the user does not update it
            "number": forms.HiddenInput(),
            "year": forms.HiddenInput(),
            "term": forms.HiddenInput(),
            "professor": forms.HiddenInput(),
        }
        labels: {"student": "Agregar Estudiantes"}

    def __init__(self, *args, **kwargs):
        super(StudentGroupForm, self).__init__(*args, **kwargs)
        # update form choices with only students in the field
        self.fields["student"].queryset = Users.objects.filter(role="student")


class OrderForm(forms.ModelForm):
    """
    Form to create an Order
    """

    class Meta:
        model = Order
        fields = ["student"]
        widgets = {"student": StudentWidget}  # use custom widget for students

    def __init__(self, group_pk: int, user_pk: int, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        # update form choices with only students of the current group excluding the current user
        self.fields["student"].queryset = Users.objects.filter(
            role="student", groups__in=group_pk
        ).exclude(pk=user_pk)


class ItemForm(forms.ModelForm):
    """
    Form to add an Item to an Order
    """

    class Meta:
        model = ItemOrder
        fields = ["item", "quantity", "code"]
        widgets = {"item": ItemWidget}  # use custom widget for students


class UpdateOrderItemForm(forms.ModelForm):
    """
    Form to update a specific Item in an Order
    """

    # Restrictions of items status. See Docs/item_after_request_diagram.png in this repository.
    RESTRICTED_CHOICES = {
        "Solicitado": (
            ("Solicitado", "Solicitado"),
            ("Prestado", "Prestado"),
            ("Denegado", "Denegado"),
        ),
        "Prestado": (
            ("Solicitado", "Solicitado"),
            ("Prestado", "Prestado"),
            ("Devuelto", "Devuelto"),
        ),
        "Devuelto": (
            ("Prestado", "Prestado"),
            ("Devuelto", "Devuelto"),
        ),
        "Denegado": (
            ("Solicitado", "Solicitado"),
            ("Denegado", "Denegado"),
        ),
    }

    class Meta:
        model = ItemOrder
        fields = ["item", "quantity", "code", "status"]
        widgets = {
            "item": forms.HiddenInput(),  # keep the information but don't show it to user
            "quantity": forms.NumberInput(attrs={"style": "text-align: center"}),
            "code": forms.TextInput(attrs={"style": "text-align: center"}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateOrderItemForm, self).__init__(*args, **kwargs)
        # Apply the restriction over the order status modifications
        self.fields["status"].choices = self.RESTRICTED_CHOICES[self.instance.status]
