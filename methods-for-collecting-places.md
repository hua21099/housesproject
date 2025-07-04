# 🗺️ 蒐集特定類型地點的各種方法

## 方法一：使用 Google Places API 🔍

### 🛠️ 操作步驟
1. **設定搜尋參數**：定義搜尋範圍、地點類型等
2. **發送 API 請求**：使用 `requests` 套件發送請求至 Google Places API
3. **處理回傳結果**：解析 JSON 格式的回傳資料，提取所需的地點資訊

### 📋 範例
見 `places-searcher` 專案

### ✅ 優點
- 資料品質高，Google 提供的地點資訊準確
- 支援多種地點類型，如餐廳、商店等
- API 彈性高

### ❌ 缺點
- 有使用次數限制，超過限制需要付費，且[費用](https://mapsplatform.google.com/pricing/?hl=zh-tw)可能**很高** 💰
- 舊版 Nearby Search API 回傳資料上限為 60 筆（需分頁處理）、新版回傳上限為 20 筆，對於密度高的地點類型很可能不夠使用

### ⚠️ 注意事項
- 考慮到上述缺點，需要對大區域查詢時，需搭配網格搜尋工具，將大範圍區域分割成小網格進行多次查詢

---

## 方法二：[Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) 🌐

### 📋 範例
1. 先取得[區域網格座標](https://tools.geofabrik.de/calc/#type=geofabrik_standard&bbox=120,21.8,122.1,25.4&tab=1&proj=EPSG:4326&places=1)
2. [查找台灣區域捷運站](https://overpass-api.de/api/interpreter?data=[out:json];node[subway](21.8,120.0,25.4,122.1);out;)

### 📚 資源
[入門指南](https://newtoypia.blogspot.com/2015/05/overpass-api.html)

### ✅ 優點
- 支援多種查詢語法，靈活性高
- 免費使用，無需 API 金鑰 🆓

### ❌ 缺點
- 需要了解 Overpass QL 語法
- 資料品質似乎不太好，以捷運站為範例，有些重複的捷運站資料、或是缺少名稱的不明資料。

---

## 方法三：[政府資料開放平台](https://data.gov.tw/) 🏛️

### 📋 範例
1. [捷運車站出入口](https://data.gov.tw/dataset/73233)
2. [便利超商](https://data.gov.tw/en/datasets/32086)

### ✅ 優點
- 資料來源可靠，官方提供
- 免費使用 🆓

### ❌ 缺點
- 提供的資料種類與欄位受限
- 資料更新頻率不一

### ⚠️ 注意事項
- 確認資料更新頻率，避免使用過時資料
- 有些資料需要再處理
- 可能需要透過 Google Geolocation API 轉換座標

---

## 📊 方法比較表

| 特性 | Google Places API | Overpass API | 政府資料開放平台 |
|------|------------------|--------------|----------------|
| 💰 費用 | 付費（有免費額度） | 免費 | 免費 |
| 📈 資料品質 | 高 | 中等 | 高 |
| 🔧 技術門檻 | 中等 | 高 | 低 |
| 📱 API 彈性 | 高 | 高 | 低 |
