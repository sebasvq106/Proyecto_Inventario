from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django_select2 import forms as s2forms

from .models import ClassGroups, Order, Users


class RegistrationForm(UserCreationForm):
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
    search_fields = [
        "name__icontains",
        "email__icontains",
    ]


class GroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroups
        fields = ["semester", "number", "professor", "student"]
        widgets = {"student": StudentWidget}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["student"]
        widgets = {"student": StudentWidget}
