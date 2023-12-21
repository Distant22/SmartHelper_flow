from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState
)
from data_models import ConversationFlow, Socialism, Liberalism
from controller import document_controller, feedback_controller, feedback_controller, question_controller

class FlowBot(ActivityHandler):
    
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        if conversation_state is None:
            raise TypeError(
                "[CustomPromptBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[CustomPromptBot]: Missing parameter. user_state is required but None was given"
            )
        self.is_processing = False
        self.is_feedback = False
        
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.flow_accessor = self.conversation_state.create_property("ConversationFlow")


    async def on_message_activity(self, turn_context: TurnContext):
        try:
            flow = await self.flow_accessor.get(turn_context, ConversationFlow)
            await self.handle_message(flow, turn_context)
            await self.conversation_state.save_changes(turn_context)
            await self.user_state.save_changes(turn_context)    
        except Exception as e:
            print("Error in message activity:",e)


    async def handle_message(
        self, flow: ConversationFlow, turn_context: TurnContext
    ):
        """
        這個函式會根據使用者目前的狀態調整Bot的回覆內容：
        
        State 為目前的政府狀態
        ----------------------------------
        Socialism - 社會主義｜僅處理一部份訊息
        Liberalism - 自由主義｜任何訊息都視為新的問題；預設狀態
        """
        user_input = turn_context.activity.text.strip() 
        print("使用者訊息是「",user_input,"」，目前狀態為",flow.last_state)

        # 1 - 進入自由主義：處理訊息 -> 處理完後進入社會主義
        if flow.last_state == "Liberalism" and not self.is_processing :
            flow.set_state(Socialism())
            await question_controller(self, turn_context, user_input)
            
        # 2 - 進入社會主義：根據是否在處理報表決定狀態
        else:
            
            # 3 - 紀錄使用者的回饋
            if self.is_feedback:
                self.is_feedback = False
                await feedback_controller(self, flow, turn_context, user_input)
            
            # 2.a - 正在處理報表：除非使用者喊暫停，否則一律回「在忙」
            elif self.is_processing:
                if user_input == "暫停":
                    self.is_processing = False
                    flow.set_state(Liberalism())
                else:
                    await turn_context.send_activity("在忙")
            
            # 2.b - 使用者同意調用報表：開始用報表來處理問題
            elif user_input == "調用報表":
                self.is_processing = True  
                await document_controller(self, turn_context, user_input)
            
            # 2.c - 使用者不同意調用報表：切回自由主義
            elif user_input == "不調用報表":  
                flow.set_state(Liberalism())
                
            # 2.d - 使用者直接開始問新問題：處理問題 
            else:
                flow.set_state(Socialism())
                await question_controller(self, turn_context, user_input)

