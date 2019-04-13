from users import models
from users.models import User, CreateNotes
from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be
from django.core.paginator import Paginator
from rest_framework import pagination


class PageNoteSerializer(serializers.ModelSerializer): # Displays the Title and a Pages in a Page Note Serializer
    class Meta:
        model = CreateNotes
        fields = ('title', 'description')


class NoteSerializer(serializers.ModelSerializer):
    title = serializers.RegexField(regex=r"^[a-zA-Z0-9.' ']+$",
                                   required=True)  # Title can be a indicates number,name,spaces
    color = serializers.RegexField(regex=r"^[-\w\s]+[-\w\s]+(?:,[-\w\s]*)*$", required=True)

    class Meta:
        model = CreateNotes
        fields = '__all__'


class CollaborateSerializer(serializers.Serializer):
    collaborate=serializers.IntegerField()

class ColorSerializer(serializers.Serializer):
    color = serializers.RegexField(regex=r"^[-\w\s]+[-\w\s]+(?:,[-\w\s]*)*$", required=True)

class UpdateSerializer(serializers.ModelSerializer):
    title = serializers.RegexField(regex=r"^[a-zA-Z0-9.' ']+$",
                                   required=True)  # Title can be a indicates number,name,spaces
    color = serializers.RegexField(regex=r"^[-\w\s]+[-\w\s]+(?:,[-\w\s]*)*$", required=True)

    class Meta:
        model = CreateNotes
        fields = '__all__'

class RemainderSerializer(serializers.Serializer):
    remainder = serializers.DateTimeField()

class SearchSerializer(serializers.Serializer):
    title=serializers.CharField(max_length=20)








