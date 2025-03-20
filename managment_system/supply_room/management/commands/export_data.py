from django.core.management.base import BaseCommand
from django.apps import apps
import json
from django.utils.dateformat import DateFormat
import datetime


class Command(BaseCommand):
    help = 'Export data for multiple models to a JSON file'

    def handle(self, *args, **kwargs):
        # Definir todos los modelos a exportar
        models_to_export = [
            'item',
            'users',
            'class',
            'classgroups',
            'order',
            'itemorder',
            'userorder',
            'studentgroups'
        ]

        data = {}

        # Exportar cada modelo
        for model_name in models_to_export:
            model = apps.get_model('supply_room', model_name)  # Usamos la app y el nombre del modelo
            model_data = list(model.objects.all().values())  # Exportamos todos los registros
            
            # Convertir campos datetime a formato ISO 8601
            for record in model_data:
                for key, value in record.items():
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        record[key] = DateFormat(value).format('Y-m-d H:i:s')  # Convertir a formato ISO

            data[model_name] = model_data  # Guardamos los datos de cada modelo en el diccionario

        # Guardamos los datos en un archivo JSON
        with open('seeds.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Data for models exported successfully.'))
