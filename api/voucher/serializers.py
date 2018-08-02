from rest_framework import serializers
from app01 import models


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Voucher
        fields = '__all__'

    def create(self, validated_data):
        instance = super(VoucherSerializer, self).create(validated_data)
        instance.voucher_code += "-%05d" % instance.pk
        instance.save()
        return instance
