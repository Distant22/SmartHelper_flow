from typing import Dict
from model import MessageStatus
class MessageStatusDAO:
    @staticmethod
    def get(user_id, channel_id)->Dict:
        return MessageStatus.objects(channel_id=channel_id, user_id=user_id).first()
    @staticmethod
    def upsert(channel_id:str, user_id:str, contents:Dict)->None:
        return MessageStatus.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, **contents
        )
        
