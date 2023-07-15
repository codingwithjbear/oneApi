from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.views import APIView
import requests
import os
import json
from .models import Search

class SearchView(APIView):
    print(os.getenv('USDA_API_KEY', 'DEMO_KEY'))
    print(os.environ)
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
            Search.objects.create(term=query)

        try:
            response = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search?', params={
                'api_key': os.getenv('USDA_API_KEY', 'DEMO_KEY'),
                'q': query})

            # Check the status code of the response
            if response.status_code != 200:
                print('API request failed with status code', response.status_code)
                return JsonResponse({'error': 'API request failed'}, status=500)

            # Try to parse the response as JSON, and cache and return it
            data = response.json()
            cache.set(query, data, 3600)  # Cache the data for 1 hour
            return JsonResponse(data)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            # Catch both request errors and JSON decoding errors here
            print('Failed to make API request or parse response as JSON:', e)
            return JsonResponse({'error': 'Failed to make API request or parse response as JSON'}, status=500)
