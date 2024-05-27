from django.urls import path

# importing views from views.py
from .views import ItemList, ItemCreate
from django.urls import reverse

urlpatterns = [
	path('articulos', ItemList.as_view(template_name='page/articulos.html'), name='articulos'),
	path('crear-articulo', ItemCreate.as_view(template_name='page/crear-articulo.html', success_url='articulos'), name='crear-articulo'),
]
