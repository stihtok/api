from django.shortcuts import render
from random import shuffle
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from random import choice
from .models import Stih, Author, Tags
from .serializers import StihSerializer, AuthorSerializer, TagsSerializer
from django.http import HttpResponse
from rest_framework.exceptions import APIException
import random
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F
from django.db.models import Count

@api_view(["GET"])
def getRoutes(request):
    return Response("Our API")

@api_view(["GET"])
def getStih(request):
    pks = Stih.objects.values_list('pk', flat=True)
    random_pk = choice(pks)
    random_stih = Stih.objects.get(pk=random_pk)
    serializer = StihSerializer(random_stih, many=False)
    return Response(serializer.data)

@api_view(["GET"])
def getStihById(request, id):
    try:
        stih = Stih.objects.get(pk=id)
        serializer = StihSerializer(stih, many=False)
        return Response(serializer.data)
    except:
        raise APIException('getStihById error')
    
@api_view(["GET"])
def stihLike(request, id):
    try:
        Stih.objects.filter(pk=id).update(likes=F('likes') + 1)
        return HttpResponse(status=200)
    except:
        raise APIException('Like error')
    
@api_view(["GET"])
def stihDislike(request, id):
    try:
        Stih.objects.filter(pk=id).update(likes=F('likes') - 1)
        return HttpResponse(status=200)
    except:
        raise APIException('Dislike error')

@api_view(["GET"])
def getStihBundle(request):
    stih_pks = Stih.objects.values_list('pk', flat=True)
    selected_pks = random.sample(list(stih_pks), 10)
    stih_objects = Stih.objects.filter(pk__in=selected_pks).order_by('?')
    serializer = StihSerializer(stih_objects, many=True)

    return Response(serializer.data)

@api_view(["GET"])
def getAllStihByAuthorId(request, id):
    try:
        stih_objects = Stih.objects.order_by("-likes", "createdAt").all().filter(author__id=id)
        serializer = StihSerializer(stih_objects, many=True)
        return Response(serializer.data)
    except:
        raise APIException('getAllStihByAuthorId error')
    
@api_view(["GET"])
def getAllStihByAuthorIdRandom(request, id):
    try:
        stih_objects = list(Stih.objects.all().filter(author__id=id))
        shuffle(stih_objects)
        serializer = StihSerializer(stih_objects, many=True)
        return Response(serializer.data)
    except:
        raise APIException('getAllStihByAuthorIdRandom error')

@api_view(["GET"])
def getAllStihByYear(request, year):
    try:
        result = []
        authors_in_that_year = Stih.objects.all().filter(createdAt__contains=year).values('author').distinct();
        for author in authors_in_that_year:
            stihs_by_author_that_year = Stih.objects.all().filter(createdAt__contains=year).filter(author=author['author'])
            author = Author.objects.get(id = author['author'])
            stih_list=[]
            for s in stihs_by_author_that_year:
                stih_list.append({'title': s.title, 'epigraph': s.epigraph, 'body': s.body, 'createdAt': s.createdAt, 'id': s.id})
            result.append({'name': author.name, 'photo': author.photo.url, 'id': author.id, 'stihs': stih_list})
        return Response(result)
    except:
        raise APIException('getAllStihByYear error')


@api_view(["GET"])
def getAuthors(request):
    authors = Author.objects.all().order_by("?")
    serializer = AuthorSerializer(authors, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getTags(request):
    tags = Tags.objects.all().order_by("?")
    serializer = TagsSerializer(tags, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getStihsByTag(request,id):
    stihsByTag = Stih.objects.filter(tags__id=id)
    serializer = StihSerializer(stihsByTag, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getStihsByQuery(request):
    if "q" in request.GET:
        params = request.GET.getlist("q")
        if len(params) > 0:
            pks = list(Stih.objects.values_list('pk', flat=True))
            random.shuffle(pks)
            all = Stih.objects.filter(pk__in=pks)
            for q in params:
                all = all.filter(tags__id=q)
            serializer = StihSerializer(all, many=True)
            return Response(serializer.data)
    else:
        stih_pks = Stih.objects.values_list('pk', flat=True)
        selected_pks = random.sample(list(stih_pks), 10)
        stih_objects = Stih.objects.filter(pk__in=selected_pks).order_by('?')
        serializer = StihSerializer(stih_objects, many=True)

    return Response(serializer.data)
         
@api_view(["GET"])
def getAuthorById(request, id):
    try:
        author = Author.objects.get(pk=id)
        serializer = AuthorSerializer(author, many=False)
        return Response(serializer.data)
    except:
        raise APIException('getAuthorById error')
    
@api_view(["GET"])
def search(request, searchString):
    try:
        vector = SearchVector("body", "title", "epigraph")
        query = SearchQuery(searchString, search_type="phrase")
        stihSearch = Stih.objects.annotate(search=vector).filter(search=query)
        authorSearch = Author.objects.filter(name__search=searchString)
        authorSerializer = AuthorSerializer(authorSearch, many=True)
        stihSerializer = StihSerializer(stihSearch, many=True)
        data = authorSerializer.data + stihSerializer.data
        return Response(data)
    except:
        raise APIException('Search error')