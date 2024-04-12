import requests
import itertools
from django.http import JsonResponse


def route_plan(request):
    if request.method == 'GET':
        # 获取请求中的城市和地址
        city = request.GET.get('city')
        address = request.GET.get('address')
        hotel = request.GET.get('hotel')

        place = hotel + "|" + address
        # 准备地理编码的参数
        params = {
            'address': place,
            'city': city,
            'batch': 'true',
            'output': 'JSON',
            'Key': 'ad73b35909a0935ce997bae3818a6c02'  # 替换为你的实际 API 密钥
        }

        # 发送地理编码请求
        response = requests.get('https://restapi.amap.com/v3/geocode/geo', params=params)
        data = response.json()
        print("Geocode API Response:", data)  # 打印地理编码API的返回值

        locations = {}
        distances = {}

        for geocode in data.get('geocodes', []):
            locations[geocode['formatted_address']] = geocode['location']

        for dest_name, destination in locations.items():
            origins = '|'.join([loc for name, loc in locations.items()])
            params = {
                'origins': origins,
                'destination': destination,
                'type': '1',
                'output': 'JSON',
                'Key': 'ad73b35909a0935ce997bae3818a6c02'  # 替换为你的实际 API 密钥
            }
            response = requests.get('https://restapi.amap.com/v3/distance', params=params)
            data = response.json()
            print("Distance API Response:", data)  # 打印距离API的返回值

            for result in data.get('results', []):
                origin_name = list(locations.keys())[int(result['origin_id']) - 1]
                if dest_name not in distances:
                    distances[dest_name] = {}
                distances[dest_name][origin_name] = result['distance']

        print(distances)
        if not distances:
            return JsonResponse({'error': 'No distance data available'}, status=400)

        # 将距离转换为整数
        for src, src_dict in distances.items():
            for dest, distance in src_dict.items():
                src_dict[dest] = int(distance)

        # 获取所有地点的名称
        places = list(distances.keys())

        # 生成所有可能的路径
        routes = list(itertools.permutations(places))

        # 初始化最短路径和对应的距离
        shortest_route = None
        shortest_distance = float('inf')

        # 遍历所有路径，找出最短的那个
        for route in routes:
            # 计算当前路径的总距离
            total_distance = sum(distances[route[i]][route[i + 1]] for i in range(len(route) - 1))
            total_distance += distances[route[-1]][route[0]]  # 加上从最后一个地点返回起点的距离

            # 如果当前路径比已知的最短路径还要短，就更新最短路径和对应的距离
            if total_distance < shortest_distance:
                shortest_route = route
                shortest_distance = total_distance

        # 打印最短路径和对应的距离
        print('Shortest route: ', ' -> '.join(shortest_route))
        print('Shortest distance: ', shortest_distance)

        # 返回最短路径和对应的距离
        result = {
            "shortest_route": shortest_route,
            "shortest_distance": shortest_distance
        }
        return JsonResponse(result)
    else:
            return JsonResponse({'error': 'Please use GET method to request.'}, status=400)