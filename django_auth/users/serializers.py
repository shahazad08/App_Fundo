# from rest_framework.fields import ImageField
from rest_framework.validators import UniqueValidator
from .models import User
from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be

# converted to native Python data types that can then be easily rendered into JSON, XML or other content types
# ModelSerializer: It is a class which provides a useful shortcut for creating serializers
# that deal with model instances and query sets.

class UserSerializer(serializers.ModelSerializer):  # Created the User Serializer for all the fields in a model
    date_joined = serializers.ReadOnlyField()  # date joined should be in a read_only modes
    password = serializers.CharField(style={'input_type': 'password'})  # password should be properly validated
    # email = serializers.EmailField(validators=[UniqueValidator(queryset=User.object.all())])
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)

    class Meta:  # We have  use of Meta class is simply to provide metadata to the ModelForm class.
        model = User  # Shows that the User fields contain the model class
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'password')

class LoginSerializer(serializers.ModelSerializer):  # Created the user serializer for a Login
    password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)
    class Meta:
        model = User  # Contains the fields of email and a password
        fields = ['email', 'password']


class profile(serializers.ModelSerializer):  # Created the user serializer for a Login
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)
    image = serializers.ImageField(required=True)

    class Meta:
        model = User  # Contains the fields of email and a password
        fields = ['email', 'image']

class profile_delete(serializers.ModelSerializer):  # Created the user serializer for a Login
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)
    class Meta:
        model = User  # Contains the fields of email and a password
        fields = ['email']
