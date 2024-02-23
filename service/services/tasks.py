from celery import shared_task
from django.db.models import F


@shared_task
def set_price(subcription_id):
    from services.models import Subscription
    # лучше хранить id чтобы при изменении записи в бд запись в очередь
    # была актуальной

    subcription = Subscription.objects.filter(id=subcription_id).annotate(
        annotated_price=F('service__full_price') -
              F('service__full_price') *
              F('plan__discount_percent') / 100.00).first()

    subcription.price = subcription.annotated_price
    subcription.save()
