from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator
from django.db import models

# specifying choices

STATUS_CHOICES = (
    ("Solicitado", "Solicitado"),
    ("Prestado", "Prestado"),
    ("Devuelto", "Devuelto"),
    ("Denegado", "Denegado"),
)

ROLE_CHOICES = (
    ("student", "Estudiante"),
    ("teacher", "Profesor"),
)


class CustomUserManager(UserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super(CustomUserManager, self).create_user(
            username, email, password, **extra_fields
        )

    def create_superuser(
        self, username=None, email=None, password=None, **extra_fields
    ):
        return super(CustomUserManager, self).create_superuser(
            username, email, password, **extra_fields
        )

    def _create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class Item(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"


class Users(AbstractUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=200, choices=ROLE_CHOICES, default="student")
    student_id = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=50, null=True)
    groups = models.ManyToManyField(
        "ClassGroups", related_name="group_student", blank=True
    )
    orders = models.ManyToManyField("Order", related_name="order_student", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "role"]

    def save(self, *args, **kwargs):
        # Set username to the part of the email before the '@' symbol
        if not self.username:
            self.username = self.email.split("@")[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email}"


class Class(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassGroups(models.Model):
    number = models.PositiveIntegerField()
    semester = models.CharField(max_length=200)
    professor = models.ForeignKey(
        Users, related_name="group_professor", on_delete=models.PROTECT
    )
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ManyToManyField(
        Users, related_name="group_student", through=Users.groups.through, blank=True
    )

    def __str__(self):
        return f"{self.class_id} ({self.number}, {self.semester})"


class Order(models.Model):
    group = models.ForeignKey(
        ClassGroups, related_name="order_group", on_delete=models.CASCADE
    )
    student = models.ManyToManyField(
        Users, related_name="Order_student", through=Users.orders.through, blank=True
    )

    def __str__(self):
        return f"{self.group.id}"

    @property
    def needs_attention(self):
        order_items = ItemOrder.objects.filter(order=self)
        return any([item.status == "Solicitado" for item in order_items])


class ItemOrder(models.Model):
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Solicitado"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    code = models.CharField(max_length=200, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.order.id}, {self.item.id}"


class UserOrder(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name}, {self.order.id}"


class StudentGroups(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(ClassGroups, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.id}, {self.group.id}"
