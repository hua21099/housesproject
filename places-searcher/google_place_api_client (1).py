import os
import requests
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv(override=True)

DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

class GooglePlaceApiClient:
    """
    Google Places API 客戶端，用於查詢指定座標範圍內的地點。
    """
    api_endpoint: str
    api_key: str

    def __init__(self, api_endpoint: str, api_key: str):
        if not api_key:
            raise ValueError("API 金鑰未設定，請提供 GOOGLE_MAP_API_KEY。")
        self.api_key = api_key
        self.api_endpoint = api_endpoint


    def process_address_components(self, address_components: List[Dict]) -> Dict[str, str]:
        """
        將 addressComponents 轉換為 key-value 形式
        key: component 的 type，value: longText
        """
        result = {}
        if not address_components:
            return result
        
        for component in address_components:
            types = component.get('types', [])
            long_text = component.get('longText', '')
            
            # 對每個類型都建立對應
            for component_type in types:
                result[component_type] = long_text
        
        return result

    def get_places(self, lat: float, lng: float, radius: float, place_types: List[str]) -> List[Dict]:
        """
        使用 Google Places API 查詢指定座標範圍內的所有地點
        """

        params = {
            'includedTypes': place_types,
            'languageCode': 'zh-TW',
            'locationRestriction': {
                'circle': {
                    'center': {
                        'latitude': lat,
                        'longitude': lng
                    },
                    'radius': radius
                }
            },
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.displayName,places.location,places.formattedAddress,places.addressComponents,places.id,places.rating,places.types'
        }
        
        places = []
        
        try:
            # 第一次查詢
            response = requests.post(self.api_endpoint, json=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if response.status_code != 200:
                raise requests.exceptions.RequestException(f"API 錯誤，狀態碼：{response.status_code}")
            
            if DEBUG: 
                print(data)

            # 結果
            if 'places' in data:
                for place in data['places']:
                    # 處理 addressComponents
                    address_components = place.get('addressComponents', [])
                    address_components_dict = self.process_address_components(address_components)
                    place = {
                        'id': place.get('id', ''),
                        'name': place.get('displayName', {}).get('text', 'N/A'),
                        'place_id': place.get('id', ''),
                        'latitude': place.get('location', {}).get('latitude', 0),
                        'longitude': place.get('location', {}).get('longitude', 0),
                        'address': place.get('formattedAddress', ''),
                        'rating': place.get('rating', 'N/A'),
                        'types': place.get('types', []),
                        'addressComponents': address_components_dict
                    }
                    places.append(place)
                    if DEBUG: 
                        print(f"找到地點：{place['name']}")
                if DEBUG and len(data['places']) == 20:
                    # Google Places API NearbySearch 最多返回 20 個結果
                    raise Warning(f"查詢結果為 20 個，可能還有更多地點，請考慮減少網格大小－查詢依據：lat={lat}, lng={lng}, radius={radius}, place_types={place_types}")

            print(f"\n總共查詢到 {len(places)} 個地點")
            return places
            
        except requests.exceptions.RequestException as e:
            print(f"網路請求錯誤：{e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤：{e}")
            return []