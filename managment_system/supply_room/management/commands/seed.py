from django.core.management.base import BaseCommand
from django.apps import apps
import json
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
from django.utils import timezone
from datetime import timezone as dt_timezone
import warnings

class Command(BaseCommand):
    help = 'Import data from a JSON file into multiple models'

    def handle(self, *args, **kwargs):
        # Suprimir los warnings específicos sobre datetime naive
        warnings.filterwarnings("ignore", category=RuntimeWarning, message="DateTimeField .* received a naive datetime.*")

        # Cargar el archivo JSON
        try:
            with open('seeds.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('The file seeds.json was not found.'))
            return

        models_to_import = [
            'item',
            'users',
            'class',
            'classgroups',
            'order',
            'itemorder',
            'userorder',
            'studentgroups'
        ]

        # Contador de registros creados
        records_created = 0
        records_failed = 0

        for model_name in models_to_import:
            model = apps.get_model('supply_room', model_name)  # Obtener el modelo desde la app
            
            if model_name in data:
                model_data = data[model_name]
                for record in model_data:
                    # Convertir las fechas a formato datetime (aware, en UTC)
                    for key, value in record.items():
                        if isinstance(value, str) and 'T' in value:  # Formato ISO 8601
                            parsed_date = parse_datetime(value)
                            if parsed_date:
                                # Convertir la fecha naive a aware (en UTC)
                                record[key] = timezone.make_aware(parsed_date, dt_timezone.utc)
                    
                    try:
                        # Crear el objeto con todos los campos disponibles en record
                        model.objects.create(**record)
                        records_created += 1  # Contabilizar los registros creados
                    except IntegrityError as e:
                        records_failed += 1  # Contabilizar errores de integridad
                        self.stderr.write(f'Error saving {model_name} record with id {record.get("id", "N/A")}: {e}')
                    except Exception as e:
                        records_failed += 1  # Contabilizar otros errores
                        self.stderr.write(f'Unexpected error: {e}')
            else:
                self.stdout.write(self.style.WARNING(f'No data found for {model_name}'))

        # Mensaje final
        if records_failed > 0:
            self.stdout.write(self.style.ERROR(f'Finished with {records_failed} errors.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Data imported successfully with {records_created} records created.'))
