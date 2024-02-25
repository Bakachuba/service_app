from django.conf import settings
from django.db.models import Prefetch, F, Sum
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.core.cache import cache

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client',
                 queryset=Client.objects.all().select_related('user').
                 only('company_name', 'user__email'))
    )  # .annotate(price=F('service__full_price') -
    #               F('service__full_price') *
    #              F('plan__discount_percent') / 100.00)

    '''("services_service"."full_price" - 
     (("services_service"."full_price" * "services_plan".
     "discount_percent") / 100.0)) AS "price"
     
     запрос в бд annotate = AS
     '''
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        # агрегационная функция
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.PRICE_CACHE_NAME)

        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60 * 60)

        response_data = {'result': response.data}
        response_data['total_amount'] = total_price
        # out: "total_amount": 637.5
        response.data = response_data
        # обертка выводимых данных на уровень
        # out: "result": []

        return response
