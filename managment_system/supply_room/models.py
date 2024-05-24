from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

# specifying choices

STATUS_CHOICES = (
    ("requested", "Solicitado"),
    ("lent", "Prestado"),
    ("returned", "Devuelto"),
    ("denied", "Denegado"),
)

class Item(models.Model):
    name = models.CharField(max_length=200)

class Users(AbstractUser):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    role = models.CharField(max_length=200)
    student_id = models.CharField(max_length=200)



class Class(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
class Groups(models.Model):
    number = models.PositiveIntegerField()
    semester = models.CharField(max_length=200)
    professor = models.ForeignKey(Users, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)

class Order(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)

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
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)

