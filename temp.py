from typing import Literal

class ProcessEntry:
    pass


class ProcessList:
    @staticmethod
    def set_active(channel_id, user_id):
        """设置用户状态为活跃（1）。"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, is_active=True
        )

    @staticmethod
    def set_inactive(channel_id, user_id):
        """设置用户状态为非活跃（0）。"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, is_active=False
        )

    @staticmethod
    def is_active(channel_id, user_id):
        """检查用户是否活跃。"""
        entry = ProcessEntry.objects(channel_id=channel_id, user_id=user_id).first()
        return entry.is_active if entry else False

    @staticmethod
    def delete_user(channel_id, user_id):
        """删除用户记录。"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).delete()
        
    @staticmethod
    def set_state_document(channel_id, user_id):
        """設成處理報表"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, is_active=True, state="Document"
        )
    
    @staticmethod
    def set_state_document_processing(channel_id, user_id):
        """設成報表忙碌"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, is_active=True, state="Document_processing"
        )
    
    @staticmethod
    def set_state_feedback(channel_id, user_id):
        """設成處理回饋"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, is_active=True, state="Feedback"
        )
    
    @staticmethod
    def set_state_none(channel_id, user_id):
        """設成無狀態"""
        ProcessEntry.objects(channel_id=channel_id, user_id=user_id).update_one(
            upsert=True, is_active=True, state="None"
        )
        
    @staticmethod
    def get_state(channel_id, user_id):
        """取得目前狀態"""
        entry = ProcessEntry.objects(channel_id=channel_id, user_id=user_id).first()
        return entry.state if entry.state else None
        
    @staticmethod
    def get_state_choice(channel_id, user_id):
        """取得 Quick Reply 選項"""
        entry = ProcessEntry.objects(channel_id=channel_id, user_id=user_id).first()
        return entry.state.choice if entry.state.choices else None
    
    
class Feedback:
    channel_id: str
    user_id: str
    busy: bool
    type:str
    
    def set_info(self, info:dict):
        pass
        
    def get_info(self):
        return {
            "channel_id": self.channel_id,
            "user_id": self.user_id,
            "state":{
                "busy": self.busy,
                "type": self.type
            }
        }
    
    ["處理報表","不處理報表"]
    
    
    
    
    








class Temp:
    type: {
        "Document": [{ "調用" : True }, { "不調用" : False }],
        "Feedback": [{ "更好" : False }, { "更差" : False }],
        "Idle": []
    }







class Temp: 
    @staticmethod
    def get_state_type(channel_id, user_id):
        """取得目前狀態"""
        entry = ProcessEntry.objects(channel_id=channel_id, user_id=user_id).first()
        return entry.state.type if entry.state.type else None
    

