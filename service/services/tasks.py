import datetime
import time

from celery_singleton import Singleton
from celery import shared_task
from django.db import transaction
from django.db.models import F


@shared_task(base=Singleton)
def set_price(subcription_id):
    from services.models import Subscription
    # лучше хранить id чтобы при изменении записи в бд запись в очередь
    # была актуальной

    with transaction.atomic():
        # все действия будут применяться атомарно (только все вместе)
        # time.sleep(5)

        subcription = Subscription.objects.select_for_update().filter(id=subcription_id).annotate(
            annotated_price=F('service__full_price') -
                            F('service__full_price') *
                            F('plan__discount_percent') / 100.00).first()

        # time.sleep(20)

        subcription.price = subcription.annotated_price
        subcription.save()


@shared_task(base=Singleton)
def set_comment(subcription_id):
    from services.models import Subscription
    # лучше хранить id чтобы при изменении записи в бд запись в очередь
    # была актуальной

    with transaction.atomic():
        subcription = Subscription.objects.select_for_update().get(id=subcription_id)
        # закрывает subcscription, только по выполнению отдает другим таскам

        # time.sleep(27)

        subcription.comment = str(datetime.datetime.now())
        subcription.save()
