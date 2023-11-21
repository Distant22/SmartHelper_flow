from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, ASCENDING
import os
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import tiktoken
import traceback

# 設定 logging
logging.basicConfig(level=logging.INFO)

# MongoDB 連接
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_COLLECTION_CHATLOG = os.getenv("MONGODB_COLLECTION_CHATLOG")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NANE")

# 檢查環境變數是否存在
if not MONGODB_URI or not MONGODB_COLLECTION_CHATLOG or not MONGODB_DATABASE_NAME:
    raise ValueError(
        "One or more environment variables are missing: 'MONGODB_URI', 'MONGODB_COLLECTION_CHATLOG', 'MONGODB_DATABASE_NANE'"
    )


# 異步客戶端
client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DATABASE_NAME]
chatlog = db[MONGODB_COLLECTION_CHATLOG]


def init_chatlog():
    # 檢查並創建集合
    inner_client = MongoClient(MONGODB_URI)
    inner_db = inner_client[MONGODB_DATABASE_NAME]
    inner_chatlog = inner_db[MONGODB_COLLECTION_CHATLOG]

    collection_names = inner_db.list_collection_names()
    if MONGODB_COLLECTION_CHATLOG not in collection_names:
        inner_db.create_collection(MONGODB_COLLECTION_CHATLOG)

    # 建立索引
    inner_chatlog.create_index([("user_id", ASCENDING), ("channel_id", ASCENDING)])
    inner_chatlog.create_index("feedback_status")
    inner_chatlog.create_index("user_timestmp")
    inner_chatlog.create_index("bot_timestmp")


async def get_chatlog_data(
    user_id: str, channel_id: str, minutes: int = 3, limit: int = 4
) -> list:
    """
    異步函數，用於從 MongoDB 的 chatlog 集合中獲取特定用戶的最新聊天記錄。

    Args:
        user_id (str): 要查詢的用戶 ID。
        channel_id (str): 聊天記錄的渠道。
        minutes (int, optional): 查詢的時間範圍（以分鐘為單位）。默認為過去 3 分鐘。
        limit (int, optional): 返回的記錄數量上限。默認為 10。

    Returns:
        list: 返回一個包含最新聊天記錄的列表。

    Raises:
        Exception: 查詢過程中發生的任何異常。
    """
    try:
        # 計算過去指定分鐘數的時間戳
        time_threshold = datetime.now() - timedelta(minutes=minutes)

        # 構建查詢條件
        query = {
            "user_id": user_id,
            "channel_id": channel_id,
            "user_timestamp": {"$gte": time_threshold},
        }

        # 異步查詢數據庫
        cursor = chatlog.find(query).sort("timestamp", -1).limit(limit)
        last_records = await cursor.to_list(length=limit)
        return last_records
    except Exception as e:
        # 可以根據需要進行日誌記錄或其他錯誤處理
        logging.error(f"Error retrieving chat logs: {e}\n{traceback.format_exc()}")
        return []


async def insert_chatlog_data(data):
    try:
        if isinstance(data, list):
            # 處理多筆資料的批量插入
            await chatlog.insert_many(data)
        else:
            # 處理單筆資料的插入
            chatlog.insert_one(data)
    except Exception as e:
        logging.error(f"Error in inserting data: {e}\n{traceback.format_exc()}")


class Reference(BaseModel):
    vector_id: str
    document_id: str
    document_name: Optional[str] = None
    document_source: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatlogData(BaseModel):
    service_url: str
    channel_id: str
    user_id: str
    user_name: Optional[str] = None
    user_text: Optional[str] = None
    user_text_tokens: Optional[int] = None
    bot_text_tokens: Optional[int] = None
    bot_text: Optional[str] = None
    feedback_status: int = Field(0, description="0: 沒有提供問卷, 1: 提供問卷, 2: 填寫完畢")
    feedback: Optional[Dict[str, str]] = None
    user_timestamp: Optional[datetime] = None
    bot_timestamp: Optional[datetime] = None
    reference: List[Reference] = []
    history: List[Dict[str, str]] = []


def count_tokens(
    text: str, encoding_name: str = "cl100k_base", model_name: str = "gpt-3.5-turbo"
) -> int:
    # import tiktoken
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens
