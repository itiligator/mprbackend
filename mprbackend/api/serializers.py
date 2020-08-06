from rest_framework import serializers
from .models import ChecklistQuestion, ChecklistAnswer, Price, Product


class ChecklistQuestionSerializer(serializers.ModelSerializer):
    clientType = serializers.CharField(source='client_type')

    class Meta:
        model = ChecklistQuestion
        fields = ['UUID', 'clientType', 'text', 'active', 'section']


class ChecklistAnswerSerializer(serializers.ModelSerializer):
    visitUUID = serializers.SlugRelatedField(source='visit', slug_field='UUID', read_only=True)
    questionUUID = serializers.PrimaryKeyRelatedField(source='question', read_only=True)

    class Meta:
        model = ChecklistAnswer
        fields = ['visitUUID', 'questionUUID', 'answer1', 'answer2', 'UUID']


class PriceSerializer(serializers.ModelSerializer):
    priceType = serializers.CharField(source='price_type')
    productItem = serializers.CharField(source='product_item')
    dataBase = serializers.BooleanField(source='database')

    class Meta:
        model = Price
        fields = ['priceType', 'productItem', 'amount', 'dataBase']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['item', 'name', 'description', 'active']
