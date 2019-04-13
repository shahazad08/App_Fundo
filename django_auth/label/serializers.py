from users.models import User, CreateNotes,Labels
from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be

class ReadLabel(serializers.ModelSerializer):
    label_name=serializers.CharField()

    class Meta:
        model = Labels
        fields = ['label_name']

class LabelSerializer(serializers.ModelSerializer):
    label_id=serializers.IntegerField()

    class Meta:
        model = CreateNotes
        fields = ['label_id']







