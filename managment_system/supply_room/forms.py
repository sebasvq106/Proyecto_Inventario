from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django_select2 import forms as s2forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone

from .models import ClassGroups, ItemOrder, Order, StudentGroups, Users, Item


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
        fields = ["year", "term", "number", "professor"]

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        # update form choices with only students or teachers in each field
        self.fields["professor"].queryset = Users.objects.filter(role="teacher")


class StudentGroupForm(forms.Form):
    student = forms.ModelMultipleChoiceField(
        queryset=Users.objects.filter(role='student'),
        widget=StudentWidget,
        required=False,
        label="Agregar Estudiantes"
    )

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group

        if group:
            self.fields['student'].initial = group.students.all()

    def save(self):
        if not self.group:
            raise ValueError("El grupo no está definido")

        students = self.cleaned_data.get('student', [])

        StudentGroups.objects.filter(group=self.group).delete()

        created = []
        for student in students:
            rel = StudentGroups.objects.create(
                student=student,
                group=self.group
            )
            created.append(rel)

        return created


class OrderForm(forms.ModelForm):
    """
     Form for creating orders with improved student selection
    """
    is_group_order = forms.BooleanField(
        required=False,
        label="¿Es una orden grupal?",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-5 w-5 text-blue-600 rounded focus:ring-blue-500',
            'id': 'id_is_group_order',
            'onchange': 'toggleStudentSelection()'
        })
    )

    students = forms.ModelMultipleChoiceField(
        queryset=Users.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'student-select hidden',
            'multiple': 'multiple',
            'data-placeholder': 'Seleccione estudiantes...'
        }),
        required=False,
        label="Estudiantes del grupo"
    )

    class Meta:
        model = Order
        fields = ['is_group_order', 'students']

    def __init__(self, group_pk: int, user_pk: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['students'].queryset = Users.objects.filter(
            role='student',
            studentgroups__group_id=group_pk
        ).exclude(pk=user_pk).order_by('last_name')

        if self.data.get('is_group_order') == 'on':
            self.fields['students'].widget.attrs['class'] = 'student-select'

    def clean(self):
        cleaned_data = super().clean()
        is_group = cleaned_data.get('is_group_order')
        students = cleaned_data.get('students')

        if is_group and not students:
            raise forms.ValidationError(
                "Debe seleccionar al menos un estudiante para la orden grupal."
            )
        return cleaned_data


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = Item.objects.filter(is_available=True)

        # Configuration to Select2
        self.fields['item'].widget.attrs.update({
            'class': 'item-search w-full',
            'data-placeholder': 'Escribe para buscar...',
            'data-minimum-input-length': '2',
            'data-ajax--url': '/items/search/',
        })

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if item and quantity:
            # Verify that the item is available
            if not item.is_available:
                raise forms.ValidationError(
                    "El artículo seleccionado ya no está disponible"
                )

            total_items = Item.objects.filter(
                name=item.name,
                is_available=True
            ).count()

            available = total_items

            if quantity > available:
                raise forms.ValidationError(
                    f"¡Stock insuficiente! Solo hay {available} unidad(es) disponible(s) de {item.name}"
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        item_name = instance.item.name
        quantity = instance.quantity

        with transaction.atomic():
            # Reserve items
            items_to_reserve = list(
                Item.objects.select_for_update().filter(
                    name=item_name,
                    is_available=True
                )[:quantity]
            )

            if len(items_to_reserve) < quantity:
                raise ValidationError(
                    f"Reserva fallida. Solo {len(items_to_reserve)} de {quantity} unidades disponibles ahora"
                )

            # Mark as unavailable
            for item in items_to_reserve:
                item.is_available = False
                item.save()

            if commit:
                instance.save()

        return instance

    class Meta:
        model = ItemOrder
        fields = ['item', 'quantity', 'code']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'min': 1
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Opcional'
            })
        }


class UpdateOrderItemForm(forms.ModelForm):
    """
    Form to update a specific Item in an Order with availability management
    """

    RESTRICTED_CHOICES = {
        "Solicitado": (
            ("Solicitado", "Solicitado"),
            ("Prestado", "Prestado"),
            ("Denegado", "Denegado"),
        ),
        "Prestado": (
            ("Prestado", "Prestado"),
            ("Devuelto", "Devuelto"),
        ),
        "Devuelto": (
            ("Devuelto", "Devuelto"),
        ),
        "Denegado": (
            ("Denegado", "Denegado"),
        ),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_status = getattr(self.instance, 'status', None)

        if self.instance and self.instance.pk:
            self.fields["status"].choices = self.RESTRICTED_CHOICES.get(
                self.instance.status,
                [(self.instance.status, self.instance.status)]
            )

    class Meta:
        model = ItemOrder
        fields = ["item", "quantity", "code", "status"]
        widgets = {
            "item": forms.HiddenInput(),
            "quantity": forms.NumberInput(attrs={"style": "text-align: center"}),
            "code": forms.TextInput(attrs={"style": "text-align: center"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.instance and self.instance.pk:
            if self.original_status != "Devuelto" and instance.status == "Devuelto":
                instance.return_date = timezone.now()
                self._mark_items_as_available(instance)
            elif instance.status == "Denegado":
                self._mark_items_as_available(instance)

        if commit:
            instance.save()
        return instance

    def _mark_items_as_available(self, item_order):
        """
        Mark the corresponding items as available
        """
        items_to_update = Item.objects.filter(
            name=item_order.item.name,
            is_available=False
        )[:item_order.quantity]

        updated_count = 0
        for item in items_to_update:
            item.is_available = True
            item.save()
            updated_count += 1

        if updated_count < item_order.quantity:
            raise ValidationError(
                f"No se pudieron reactivar todos los ítems. Reactivados: {updated_count}/{item_order.quantity}"
            )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Form for change the password.
    """

    def clean_new_password1(self):
        """
        Verifica que la nueva contraseña no sea igual a la actual y cumple con los requisitos de seguridad.
        """
        old_password = self.cleaned_data.get("old_password")
        new_password1 = self.cleaned_data.get("new_password1")
        user = self.user

        if not user.check_password(old_password):
            raise ValidationError(_("La contraseña antigua es incorrecta."))
        if old_password == new_password1:
            raise ValidationError(_("La nueva contraseña no puede ser la misma que la anterior."))

        # Verificar que la nueva contraseña cumpla con requisitos mínimos de seguridad
        if len(new_password1) < 8:
            raise ValidationError(_("La nueva contraseña debe tener al menos 8 caracteres."))

        if not any(char.isdigit() for char in new_password1):
            raise ValidationError(_("La nueva contraseña debe contener al menos un número."))

        if not any(char.islower() for char in new_password1):
            raise ValidationError(_("La nueva contraseña debe contener al menos una letra minúscula."))

        if not any(char.isupper() for char in new_password1):
            raise ValidationError(_("La nueva contraseña debe contener al menos una letra mayúscula."))

        if not any(char in "!@#$%^&*()_+" for char in new_password1):
            raise ValidationError(_("La nueva contraseña debe contener al menos un carácter especial (como !@#$%^&*())."))

        return new_password1

    def clean_new_password2(self):
        """
        Verifica que las dos contraseñas nuevas coincidan.
        """
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password1 != new_password2:
            raise ValidationError(_("Las contraseñas nuevas no coinciden."))

        return new_password2
