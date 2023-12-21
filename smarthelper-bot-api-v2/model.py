from mongoengine import connect, Document, StringField, BooleanField, DictField
import os
import logging
 
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
 
 
# 同步客戶端
connect(db=os.getenv("MONGODB_DATABASE_NANE"), host=os.getenv("MONGODB_URI"))
 
 
class MessageStatus(Document):
    channel_id = StringField(required=True)
    user_id = StringField(required=True)
    state = StringField(required=True)
    info = DictField(required=True)
    
 
    # 设置联合唯一索引
    meta = {
        "collection": "message_status",
        "indexes": [
            {
                "fields": ["channel_id", "user_id"],
                "unique": True,
            },
            "state"  
        ],
    }