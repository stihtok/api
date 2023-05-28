from rest_framework.serializers import ModelSerializer
from .models import Stih, Author
from rest_framework import serializers


class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ['name', 'photo', 'id', 'description']


class StihSerializer(ModelSerializer):

    author = AuthorSerializer(many=False, read_only=True)
    class Meta:
        model = Stih
        many = True
        fields = ['author', 'title', 'epigraph', 'body' , 'createdAt', 'id']


# class StihSerializer(ModelSerializer):
#     author = serializers.SlugRelatedField(
#         many=False,
#         read_only=True,
#         slug_field='name'
#     )

#     photo = serializers.HyperlinkedRelatedField(
#         many=False,
#         read_only=True,
#         view_name='author-details'
#     )
#     class Meta:
#         model = Stih
#         fields = ('author', 'photo', 'title', 'epigraph', 'body' , 'createdAt')