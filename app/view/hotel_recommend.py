from django.http import JsonResponse
from .get_token import get_token
import requests


def hotel_recommend(request):
    if request.method == 'GET':
        token = get_token()
        if token is None:
            return JsonResponse({'error': 'error token'}, status=500)
        else:
            priceRange = request.GET.get('priceRange')
            code = request.GET.get('code')
            radius = request.GET.get('radius')
            radiusUnit = request.GET.get('radiusUnit')
            roomQuantity = request.GET.get('roomQuantity')

            headers = {
                'Authorization': f'Bearer {token}'
            }

            params = {
                'cityCode': code,
                'radius': radius,
                'radiusUnit': radiusUnit
            }

            response = requests.get('https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city',
                                    headers=headers, params=params)
            data = response.json()

            hotel_ids = [hotel['hotelId'] for hotel in data['data']][:20]  # Only take the first 20 hotel IDs
            print(hotel_ids)

            results = []
            params = {
                'hotelIds': ','.join(hotel_ids),
                'roomQuantity': roomQuantity,
                'priceRange': priceRange,
                'currency': 'CNY',
                'lang': 'CN'
            }

            response = requests.get('https://test.api.amadeus.com/v3/shopping/hotel-offers', headers=headers,
                                    params=params)
            results.append(response.json())
            print(results)
            return JsonResponse(results, safe=False)
    else:
        return JsonResponse({'error': 'Please use GET method to request.'}, status=400)