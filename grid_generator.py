import math
import os
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv(override=True)

DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

class GridGenerator:
    """
    這是一個動態網格產生器，用於生成指定區域的經緯度網格。
    網格產生器 - 基於指定的區域經緯度範圍與網格大小，動態生成覆蓋該區域的網格，並可調整重疊比例以確保完整覆蓋。
    參數:
        north (float): 區域最北端緯度。
        south (float): 區域最南端緯度。
        east (float): 區域最東端經度。
        west (float): 區域最西端經度。
    方法:
        generate_minimal_overlap_grid(grid_km: float, overlap_ratio: float = 0.1) -> List[Dict]:
            依據指定網格大小與重疊比例，動態計算每個網格的經緯度步進，產生最小重疊的網格清單，並自動驗證覆蓋範圍。
    用途:
        - 適用於地理資訊系統（GIS）、區域搜尋、地圖分割等應用。
        - 可自訂網格大小與重疊比例，確保區域完整覆蓋且重疊最小化。
    """

    # 最大搜尋半徑（公里） - 根據 Google Places API 的限制
    # ref https://developers.google.com/maps/documentation/places/web-service/nearby-search?hl=zh-tw
    MAX_RADIUS_KM = 50
    
    def __init__(self, north: float, south: float, east: float, west: float):

        # 檢查經緯度範圍是否合理
        if not (-90 <= north <= 90 and -90 <= south <= 90 and -180 <= east <= 180 and -180 <= west <= 180):
            raise ValueError("經緯度範圍不合理，請檢查輸入值。")
        if north <= south or east <= west:
            raise ValueError("經緯度範圍不正確，北緯應大於南緯，東經應大於西經。")

        # 查詢範圍
        self.bounds = {
            'north': north,    # 最北邊
            'south': south,    # 最南邊
            'east': east,      # 最東邊
            'west': west       # 最西邊
        }


    def debug_print(self, *args, **kwargs):
        """只在 DEBUG 模式下印出訊息"""
        if DEBUG:
            print(*args, **kwargs)

    def generate_minimal_overlap_grid(self,
                            grid_km: float, 
                            overlap_ratio: float = 0.1) -> List[Dict]:
        """
        使用最小重疊的網格產生 - 動態計算每個網格的經度步進
        
        Args:
            grid_km: 網格大小（公里）
            overlap_ratio: 重疊比例（0.1 = 10%重疊）
        """
        
        # 計算對角線半徑
        diagonal_km = math.sqrt(grid_km**2 + grid_km**2)
        base_radius_km = diagonal_km / 2
        
        # 添加最小重疊以避免邊界效應
        overlap_km = grid_km * overlap_ratio
        final_radius_km = base_radius_km + overlap_km
        
        self.debug_print(f"📐 網格計算：")
        self.debug_print(f"   對角線半徑：{base_radius_km:.2f} km")
        self.debug_print(f"   重疊緩衝：{overlap_km:.2f} km")
        self.debug_print(f"   最終搜尋半徑：{final_radius_km:.2f} km")
        self.debug_print(f"   網格步進：{grid_km:.2f} km")

        # 檢查搜尋半徑是否超過最大限制
        if final_radius_km > self.MAX_RADIUS_KM:
            raise ValueError(f"搜尋半徑 {final_radius_km:.2f} km 超過最大限制 {self.MAX_RADIUS_KM} km。請調整網格大小或重疊比例。")

        # 緯度轉換是固定的
        lat_per_km = 1 / 111.0  # 1公里約等於0.009度緯度
        step_lat = grid_km * lat_per_km
        
        self.debug_print(f"   緯度轉換：{lat_per_km:.6f} 度/km")
        self.debug_print(f"   緯度步進：{step_lat:.4f} 度")

        # 計算總緯度範圍和需要的列數
        total_lat_range = self.bounds['north'] - self.bounds['south']
        num_rows = math.ceil(total_lat_range / step_lat)
        
        self.debug_print(f"   總緯度範圍：{total_lat_range:.4f} 度")
        self.debug_print(f"   計算列數：{num_rows} 列")

        # 動態產生網格 - 不預先計算總行數
        grid_areas = []
        total_grids = 0
        
        for row in range(num_rows):
            # 計算當前列的緯度
            current_lat = self.bounds['south'] + row * step_lat + step_lat / 2
            
            # 在當前緯度動態計算經度轉換係數
            current_lng_per_km = self._get_lng_per_km_at_lat(current_lat)
            current_step_lng = grid_km * current_lng_per_km

            # 計算當前列需要多少行
            total_lng_range = self.bounds['east'] - self.bounds['west']
            current_num_cols = math.ceil(total_lng_range / current_step_lng)
            
            self.debug_print(f"   第{row+1}行 (緯度{current_lat:.4f}°)：")
            self.debug_print(f"     經度轉換：{current_lng_per_km:.6f} 度/km")
            self.debug_print(f"     經度步進：{current_step_lng:.6f} 度")
            self.debug_print(f"     需要列數：{current_num_cols} 列")
            
            # 產生當前行的所有網格
            for col in range(current_num_cols):
                # 計算網格位置
                start_lat = self.bounds['south'] + row * step_lat
                start_lng = self.bounds['west'] + col * current_step_lng
                
                center_lat = start_lat + step_lat / 2
                center_lng = start_lng + current_step_lng / 2
                
                # 檢查網格起始點是否在邊界內
                if (start_lat <= self.bounds['north'] and
                     start_lng <= self.bounds['east']):
                    
                    area = {
                        'name': f'GRID_{chr(65+row)}{col+1}',
                        'center': (round(center_lat, 6), round(center_lng, 6)),
                        'radius': round(final_radius_km * 1000),  # 轉換為M
                        'row': row,
                        'col': col,
                    }
                    grid_areas.append(area)
                    total_grids += 1
        
        self.debug_print(f"\n   實際產生：{total_grids} 個網格")
        
        
        return grid_areas

    def _get_lng_per_km_at_lat(self, lat: float) -> float:
        """在特定緯度計算每公里對應的經度"""
        return 1 / (111.0 * math.cos(math.radians(lat)))


def main():
    """網格產生器"""

    # 範例：
    # 以台北座標查詢範圍
    # ref: https://tools.geofabrik.de/calc/#type=geofabrik_standard&bbox=121.459808,24.959926,121.666727,25.210902&tab=1&proj=EPSG:4326&places=1
    # 121.4,24.9,121.7,25.3
    # generator = GridGenerator(north=25.3, south=24.9, east=121.7, west=121.4)
    # 以台灣座標查詢範圍
    # generator = GridGenerator(north=25.4, south=21.8, east=122.1, west=120.0)

    generator = GridGenerator(north=25.4, south=21.8, east=122.1, west=120.0)
    generator.generate_minimal_overlap_grid(grid_km=1, overlap_ratio=0.1)


if __name__ == "__main__":
    main()