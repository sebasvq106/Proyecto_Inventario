import logging
from django.utils import timezone
from datetime import timedelta
from supply_room.models import ItemOrder

logger = logging.getLogger(__name__)


def clear_expired_requests():
    """Función para eliminar solicitudes vencidas (se llama desde django-crontab)"""
    try:
        logger.info("Ejecutando clear_expired_requests...")
        now = timezone.now()
        expiration_time = now - timedelta(hours=24)

        # Filtrar solicitudes vencidas
        expired_requests = ItemOrder.objects.filter(
            status='Solicitado',
            request_date__lt=expiration_time
        ).select_related('item')

        count = expired_requests.count()

        # Liberar artículos y eliminar solicitudes
        for item_order in expired_requests:
            item = item_order.item
            item.is_available = True
            item.save()
            item_order.delete()

        logger.info(f"Éxito: {count} solicitudes eliminadas y artículos liberados.")
        return True

    except Exception as e:
        logger.error(f"Error en clear_expired_requests: {str(e)}")
        return False