from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState
)
from data_models import ConversationFlow, Socialism, Liberalism
from controller import document_controller, feedback_controller, feedback_controller, async_task_controller
from service import get_history, get_context
from trendychat.chain.report_chat import ReportChat
from trendychat.messages import ChatMessage
import asyncio

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
        
        self.stop_event = asyncio.Event() 

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
            await self.process_question(flow, turn_context, user_input)
            
        # 2 - 進入社會主義：根據是否在處理報表決定狀態
        else:
            # 3 - 紀錄使用者的回饋
            if self.is_feedback:
                self.is_feedback = False
                await self.process_feedback(flow, turn_context, user_input)
            
            # 2.a - 正在處理報表：除非使用者喊暫停，否則一律回「在忙」
            elif self.is_processing:
                if user_input == "暫停":
                    self.stop_event.set()
                    self.is_processing = False
                    flow.set_state(Liberalism())
                else:
                    await turn_context.send_activity("在忙")
            
            # 2.b - 使用者同意調用報表：開始用報表來處理問題
            elif user_input == "調用報表":
                self.is_processing = True  
                await self.process_document(turn_context, user_input)
            
            # 2.c - 使用者不同意調用報表：切回自由主義
            elif user_input == "不調用報表":  
                flow.set_state(Liberalism())
                
            # 2.d - 使用者直接開始問新問題：處理問題 
            else:
                await self.process_question(flow, turn_context, user_input)


    async def process_document(self, turn_context: TurnContext, text: str):
        chat_message = ChatMessage(user_text=text, history=get_history(), context=get_context())
        response = await document_controller(
            ReportChat.async_generate_initial_response, { "message" : chat_message }
        )
        await turn_context.send_activity(response)
        response = await document_controller(
            ReportChat.async_generate_final_response, { "message" : chat_message }
        )
        self.is_processing = False 
        await turn_context.send_activity(response)
        return
    
    
    async def process_feedback(self, flow: ConversationFlow, turn_context: TurnContext, text: str):
        
        # 如果使用者回覆的內容在 FEEDBACK List 當中，就紀錄進資料庫
        response = await feedback_controller(text)
        flow.set_state(Liberalism())
        
        # 如果使用者直接問新問題，改成處理問題
        if response == None:
            response = await self.process_question(flow, turn_context, text)
            
        # 回傳結果
        return await turn_context.send_activity(response)
    

    async def process_question(self, flow: ConversationFlow, turn_context: TurnContext, text: str):
        
        # 設成社會主義
        flow.set_state(Socialism())
        self.is_processing = True
        
        # 處理問題
        response = await async_task_controller(turn_context, text)

        self.is_feedback = response["feedback"]
        self.is_processing = False
        
        return await turn_context.send_activity(response["result"])