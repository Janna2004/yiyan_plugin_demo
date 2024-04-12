from django.http import JsonResponse
import requests
import numpy as np
from sklearn.cluster import SpectralClustering


def day_plan(request):
    if request.method == "GET":
        # 获取请求中的城市和地址
        city = request.GET.get('city')
        address = request.GET.get('address')
        day = int(request.GET.get('day'))

        # 准备地理编码的参数
        params = {
            'address': address,
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

        # 构造距离矩阵
        distance_matrix = np.zeros((len(locations), len(locations)))
        for i, (src, src_dict) in enumerate(distances.items()):
            for j, dest in enumerate(locations.keys()):
                distance_matrix[i][j] = float(src_dict.get(dest, 0))

        # 转换距离矩阵为相似度矩阵
        sigma = 1.0  # 这个值需要根据你的数据进行调整
        similarity_matrix = np.exp(-distance_matrix ** 2 / (2. * sigma ** 2))

        # 应用谱聚类
        clustering = SpectralClustering(n_clusters=day, affinity='precomputed', random_state=0)
        labels = clustering.fit_predict(similarity_matrix)

        clusters = [{'day': i + 1, 'place': []} for i in range(day)]
        for idx, label in enumerate(labels):
            clusters[label]['place'].append({
                'name': list(locations.keys())[idx],
                'location': locations[list(locations.keys())[idx]]
            })

        return JsonResponse(clusters, safe=False)
    else:
        return JsonResponse({'error': 'Please use GET method to request.'}, safe=False)