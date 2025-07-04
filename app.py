import os
import requests
import json
import time
from typing import List, Dict
from grid_generator import GridGenerator
from google_place_api_client import GooglePlaceApiClient
from dotenv import load_dotenv
load_dotenv(override=True)

API_ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"
API_KEY = os.environ.get('GOOGLE_MAP_API_KEY')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
TIME_WAIT = os.environ.get('TIME_WAIT', 0.1)

def save_places_to_json(places: List[Dict], filename: str) -> bool:
    """
    將地點資料儲存到 JSON 檔案
    """
    try:
        output_data = {
            'search_info': {
                'search_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_places': len(places),
            },
            'places': places
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"成功儲存 {len(places)} 個地點資料到 {filename}")
        return True
        
    except Exception as e:
        print(f"儲存檔案時發生錯誤：{e}")
        return False

if __name__ == "__main__":
    # 定義查詢範圍與條件
    # 以台北座標查詢範圍
    # ref: https://tools.geofabrik.de/calc/#type=geofabrik_standard&bbox=121.459808,24.959926,121.666727,25.210902&tab=1&proj=EPSG:4326&places=1
    # 121.4,24.9,121.7,25.3
    bounds = {
        'north': 25.2,
        'south': 24.7,
        'east': 121.6,
        'west': 120.9
    }

    # 設定網格大小（公里）
    grid_km = 3.0

    # 設定查詢地點類型
    # 參考：https://developers.google.com/maps/documentation/places/web-service/place-types?hl=zh-tw
    place_types = ['subway_station']  # 捷運站

    # 設定輸出檔案名稱
    filename = 'example_metro_stations2.json'

    # 初始化 Google Places API 客戶端
    if not API_KEY:
        raise ValueError("請設定 GOOGLE_MAP_API_KEY 環境變數以使用 Google Places API")

    client = GooglePlaceApiClient(api_endpoint=API_ENDPOINT, api_key=API_KEY)

    # 初始化網格產生器
    print("正在依據指定條件生成網格...")
    generator = GridGenerator(**bounds)
    grids = generator.generate_minimal_overlap_grid(grid_km)

    print(f"已生成 {len(grids)} 個網格")
    print("將依據網格查詢指定地點－預計呼叫 Google Places API 次數：", len(grids))
    print("請考慮 Google Places API 的查詢限制與費用：https://mapsplatform.google.com/pricing/?hl=zh-tw")

    is_confirmed = input("是否繼續？(y/n): ").strip().lower()
    if is_confirmed != 'y':
        print("操作已取消")
        exit(0)

    # 查詢捷運站
    places = []

    for grid in grids:
        name = grid['name']
        lat, lng = grid['center']
        radius = grid['radius']
        print(f"正在依據網格 {name}－中心點({lat:.4f}, {lng:.4f}), 半徑 {radius} 公尺－查詢地點...")
        places_found = client.get_places(lat=lat, lng=lng, radius=radius, place_types=place_types)
        print(f"查詢結果：{len(places_found)} 個地點")
        places.extend(places_found)
        time.sleep(TIME_WAIT)  # 避免過快呼叫 API

    if places:
        # 依據 id 進行去重
        unique_places = {place['id']: place for place in places}

        # 儲存到 JSON 檔案
        save_places_to_json(list(unique_places.values()), filename)

        print(f"\n查詢完成！資料已儲存到 {filename}")
    else:
        print("查詢失敗，請檢查 API 金鑰是否正確設定")
