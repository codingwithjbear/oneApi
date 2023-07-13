from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.views import APIView
import requests
import os
from .models import Search

class SearchView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        cached_data = cache.get(query)
        if cached_data is not None:
            return JsonResponse(cached_data)

        try:
            # Try to increment the search count
            search = Search.objects.get(term=query)
            search.count += 1
            search.save()
        except Search.DoesNotExist:
            # This is a new search term, create a new search object
            Search.objects.create(term=query)

        response = requests.get('https://api.nal.usda.gov/ndb/search/', params={
            'api_key': os.getenv('USDA_API_KEY', ''),
            'q': query
        })

        data = response.json()
        cache.set(query, data, 3600)  # Cache the data for 1 hour

        return JsonResponse(data)
