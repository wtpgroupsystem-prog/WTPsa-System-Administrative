from rest_framework import serializers
from .models import Venta, Cisterna

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'

class CisternaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cisterna
        fields = '__all__'
