from rest_framework import serializers

from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('__all__')


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()

    client_name = serializers.CharField(source='client.company_name')
    # source - чтобы в подписке видеть какая компания подписана на сервис
    email = serializers.EmailField(source='client.user.email')
    price = serializers.SerializerMethodField()
    #при использовании methodfield можно прописать fetch в views.py

    def get_price(self, instance):
        return instance.price
    # instance - model = Subscription

    class Meta:
        model = Subscription
        fields = ['id', 'plan_id', 'client_name', 'email', 'plan', 'price']
