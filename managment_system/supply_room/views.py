from django.shortcuts import render
from django.views.generic import CreateView

# Create your views here.
from django.views.generic.list import ListView
from .models import Item, Class


class ItemList(ListView):

	# specify the model for list view
	model = Item
	paginate_by = 10

	def get_queryset(self, *args, **kwargs):
		qs = super(ItemList, self).get_queryset(*args, **kwargs)
		qs = qs.order_by('name')
		return qs


class ItemCreate(CreateView):
	# specify the model for create view
	model = Item

	# specify the fields to be displayed
	fields = ['name']


class ClassList(ListView):

	# specify the model for list view
	model = Class
	paginate_by = 10

	def get_queryset(self, *args, **kwargs):
		qs = super(ClassList, self).get_queryset(*args, **kwargs)
		qs = qs.order_by('name')
		return qs

class ClassCreate(CreateView):
	# specify the model for create view
	model = Class

	# specify the fields to be displayed
	fields = ['name', 'code']