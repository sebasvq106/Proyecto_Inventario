from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.apps import apps
from django.contrib.auth.hashers import make_password

# specifying choices

STATUS_CHOICES = (
    ("requested", "Solicitado"),
    ("lent", "Prestado"),
    ("returned", "Devuelto"),
    ("denied", "Denegado"),
)

class CustomUserManager(UserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super(CustomUserManager, self).create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        return super(CustomUserManager, self).create_superuser(username, email, password, **extra_fields)

    def _create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

class Item(models.Model):
    name = models.CharField(max_length=200)

class Users(AbstractUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=200)
    student_id = models.CharField(max_length=200, null=True)
    username =  models.CharField(max_length=50, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "role"]



class Class(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.code})"
class ClassGroups(models.Model):
    number = models.PositiveIntegerField()
    semester = models.CharField(max_length=200)
    professor = models.ForeignKey(Users, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)

class Order(models.Model):
    group = models.ForeignKey(ClassGroups, on_delete=models.CASCADE)

class ItemOrder(models.Model):
    status = models.CharField(
        max_length = 20,
        choices = STATUS_CHOICES,
        default = 'requested'
        )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    code = models.CharField(max_length=200)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

class UserOrder(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

class StudentGroups(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(ClassGroups, on_delete=models.CASCADE)

