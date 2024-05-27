from django.shortcuts import render
from django.views.generic import CreateView

# Create your views here.
from django.views.generic.list import ListView
from .models import Item

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
