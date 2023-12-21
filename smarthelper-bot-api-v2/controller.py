from services.action_manager import ActionManager
from DAO.message_status_dao import MessageStatusDAO

from data_models import ConversationFlow, Socialism, Liberalism
from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState
)


class BotController(ActivityHandler):
    
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        pass

    async def on_message_activity(self, turn_context: TurnContext):
        try:
            flow = await self.flow_accessor.get(turn_context, ConversationFlow)
            await self.handle_message(flow, turn_context)
            await self.conversation_state.save_changes(turn_context)
            await self.user_state.save_changes(turn_context)    
        except Exception as e:
            print("Error in message activity:",e)



    async def handle_message(
        self, turn_context: TurnContext
    ):
        """
        這個函式會根據使用者目前的狀態調整Bot的回覆內容：
        
        State 為目前的政府狀態
        ----------------------------------
        Socialism - 社會主義｜僅處理一部份訊息
        Liberalism - 自由主義｜任何訊息都視為新的問題；預設狀態
        """
        
        
        channel_id = turn_context.activity.channel_id 
        user_id = turn_context.activity.from_property.id
        user_message = turn_context.activity.text.strip() 
        
        user_status = MessageStatusDAO.get(channel_id=channel_id,user_id=user_id)
        action_name = user_status.get("status","")
        action_info = user_status.get("info","")
        
        Action = ActionManager.get(action_name)(user_id=user_id,channel_id=channel_id, user_message=user_message, **action_info)
        Action.run()
        
        
        
        
        