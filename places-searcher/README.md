# Google Places API 網格搜尋工具

這是一個使用 Google Places API 進行地點搜尋的工具，透過動態網格產生器來分割大範圍區域，確保完整且高效的地點資料收集。

## 專案特色

- 🗺️ **動態網格產生器** - 根據指定區域自動產生最佳網格分割
- 📍 **智慧座標轉換** - 考慮緯度差異的精確經度計算
- 🔍 **Google Places API 整合** - 支援多種地點類型搜尋
- 📊 **完整資料輸出** - 包含地址組件、評分等詳細資訊
- ♻️ **自動去重處理** - 避免重複地點資料
- 🐛 **除錯模式支援** - 詳細的執行日誌與偵錯資訊

## 檔案結構

```
places/
├── app.py                      # 主要應用程式
├── grid_generator.py           # 網格產生器核心邏輯
├── google_place_api_client.py  # Google Places API 客戶端
├── requirements.txt            # Python 相依套件
├── .env.example               # 環境變數範例檔案
└── README.md                  # 專案說明文件
```

## 系統需求

- Python 3.8+
- Google Places API 金鑰
- 網路連線

## 安裝步驟

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

複製環境變數範例檔案：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，設定您的 Google Places API 金鑰：

```bash
GOOGLE_MAP_API_KEY=您的_API_金鑰
DEBUG=False
```

### 3. 取得 Google Places API 金鑰

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Places API (New)
4. 建立 API 金鑰

## 使用方法

### 基本使用

```python
from grid_generator import GridGenerator
from google_place_api_client import GooglePlaceApiClient

# 1. 定義搜尋區域（經緯度邊界）
bounds = {
    'north': 25.3,   # 最北緯度
    'south': 24.9,   # 最南緯度  
    'east': 121.7,   # 最東經度
    'west': 121.4    # 最西經度
}

# 2. 建立網格產生器
generator = GridGenerator(**bounds)

# 3. 產生網格（2公里大小，10%重疊）
grids = generator.generate_minimal_overlap_grid(grid_km=2.0, overlap_ratio=0.1)

# 4. 初始化 API 客戶端
client = GooglePlaceApiClient(
    api_endpoint="https://places.googleapis.com/v1/places:searchNearby",
    api_key="您的_API_金鑰"
)

# 5. 搜尋地點
places = []
for grid in grids:
    lat, lng = grid['center']
    radius = grid['radius']
    results = client.get_places(
        lat=lat, 
        lng=lng, 
        radius=radius, 
        place_types=['subway_station']
    )
    places.extend(results)
```

### 執行範例程式

直接執行內建的捷運站搜尋範例：

```bash
python app.py
```

此範例會：
1. 搜尋台北地區的捷運站
2. 使用 2 公里網格進行區域分割
3. 自動去重並儲存結果至 `example_metro_stations.json`

## 核心元件說明

### GridGenerator（網格產生器）

動態產生覆蓋指定區域的最佳網格：

```python
class GridGenerator:
    def __init__(self, north: float, south: float, east: float, west: float):
        """初始化網格產生器，定義搜尋區域邊界"""
        
    def generate_minimal_overlap_grid(self, grid_km: float, overlap_ratio: float = 0.1):
        """產生最小重疊的網格陣列"""
```

**特色功能：**
- 考慮地球曲率的精確經度計算
- 可調整網格大小與重疊比例
- 自動驗證 Google Places API 半徑限制
- 支援除錯模式輸出詳細資訊

### GooglePlaceApiClient（API 客戶端）

封裝 Google Places API 的呼叫邏輯：

```python
class GooglePlaceApiClient:
    def get_places(self, lat: float, lng: float, radius: float, place_types: List[str]):
        """查詢指定座標範圍內的地點"""
        
    def process_address_components(self, address_components: List[Dict]):
        """處理地址組件資料"""
```

**支援功能：**
- 多種地點類型搜尋
- 完整地址組件解析
- 自動錯誤處理與重試
- 支援中文本地化

## 支援的地點類型

系統支援所有 [Google Places API 地點類型](https://developers.google.com/maps/documentation/places/web-service/place-types?hl=zh-tw)，包括：

- `subway_station` - 捷運站
- `restaurant` - 餐廳
- `hospital` - 醫院
- `school` - 學校
- `gas_station` - 加油站
- `bank` - 銀行
- 更多類型請參考官方文件

## 輸出格式

搜尋結果會以 JSON 格式儲存，包含以下資訊：

```json
{
  "search_info": {
    "search_date": "2025-06-15 19:48:53",
    "total_places": 126
  },
  "places": [
    {
      "id": "ChIJ_yVt2OscaDQRj1BAJ1qo7qY",
      "name": "頂埔",
      "place_id": "ChIJ_yVt2OscaDQRj1BAJ1qo7qY",
      "latitude": 24.9594071,
      "longitude": 121.4197519,
      "address": "23671台灣新北市土城區中央路四段51號 之 6 號B3",
      "rating": 4.2,
      "types": ["subway_station", "transit_station"],
      "addressComponents": {
        "street_number": "51號 之 6 號",
        "route": "中央路四段",
        "administrative_area_level_2": "土城區",
        "administrative_area_level_1": "新北市",
        "country": "台灣",
        "postal_code": "23671"
      }
    }
  ]
}
```

## 設定參數

### 環境變數

- `GOOGLE_MAP_API_KEY` - Google Places API 金鑰（必須）
- `DEBUG` - 除錯模式開關（`True`/`False`）
- `TIME_WAIT` - API 呼叫間隔秒數（預設：1）

### 網格參數

- `grid_km` - 網格大小（公里），建議 1-10 公里
- `overlap_ratio` - 重疊比例（0-1），建議 0.1（10%）

## 費用考量

使用前請了解 [Google Places API 計費方式](https://mapsplatform.google.com/pricing/?hl=zh-tw)：

- Places API (New) 費用依據請求次數計算
- 網格數量直接影響 API 呼叫次數
- 建議先用小範圍測試，確認費用後再擴大搜尋

## 常見問題

### Q: 為什麼有些地點會重複？
A: 由於網格重疊設計，同一地點可能出現在多個網格中。系統會自動根據 `place_id` 進行去重處理。

### Q: 為什麼範例中有些新北市捷運站也會被納入結果？
A: 由於網格搜尋的範圍可能跨越行政區域，系統會搜尋所有符合條件的地點。若需特定區域，需自行針對輸出結果藉由 `addressComponents` 欄位進行篩選。

### Q: 如何調整搜尋精度？
A: 減少 `grid_km` 值可提高精度，但會增加 API 呼叫次數和費用。

### Q: API 回傳 20 個結果的警告是什麼意思？
A: Google Places API 單次最多回傳 20 個結果。如果某網格達到此限制，可能還有更多地點未搜尋到，建議縮小網格大小。

### Q: 如何處理 API 限制錯誤？
A: 調整 `TIME_WAIT` 參數增加請求間隔，或檢查 API 金鑰的配額設定。

## 參考資料

- [Google Places API (New) 文件](https://developers.google.com/maps/documentation/places/web-service/overview?hl=zh-tw)
- [地點類型參考](https://developers.google.com/maps/documentation/places/web-service/place-types?hl=zh-tw)
- [API 計費資訊](https://mapsplatform.google.com/pricing/?hl=zh-tw)

## 更新記錄

- **v1.0** (2025-06-15) - 初始版本，支援基本網格搜尋功能
- 新增動態網格產生器
- 整合 Google Places API (New)
- 支援自動去重與資料匯出
