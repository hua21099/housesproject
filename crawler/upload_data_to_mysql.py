# 匯入必要套件
import pandas as pd  # 用來處理資料表（DataFrame）
from loguru import logger  # 日誌工具，用來輸出 log 訊息
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）

if __name__ == "__main__":
    # 定義資料庫連線字串（MySQL 資料庫）
    # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
    address = "mysql+pymysql://root:test@35.209.212.46:3306/Taoyuan_house"

    # 建立 SQLAlchemy 引擎物件
    engine = create_engine(address)

    # 建立連線（可用於 Pandas、原生 SQL 操作）
    connect = engine.connect()

    # 建立一個空的 DataFrame 並加入一個欄位 column_1，內容是 0~9
    # df = pd.DataFrame()

    # 4.讀取 CSV 檔案
    df = pd.read_csv("taoyuan_cleaned_no.csv", encoding="utf-8")  

    logger.info(f"upload \n{df.head()}")  # 只印前幾筆確認內容

    # 5.上傳資料至資料表
    df.to_sql(
        "Taoyuan_house_price",     # MySQL 中的資料表名稱
        con=connect,
        if_exists="append",     
        index=False,
    )

    
    # 上傳成功後，輸出 log 訊息
    logger.info("upload success")
