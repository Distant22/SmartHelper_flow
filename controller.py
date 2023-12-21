from botbuilder.core import TurnContext
from trendychat.chain.report_chat import ReportChat
from trendychat.chain.memory_chat import MemoryChat
from trendychat.messages import ChatMessage
from data_models import State, DefaultQuickReply, DefaultResponse, ConversationFlow, Liberalism
from service import get_delay_messages, get_response, get_history, get_context, get_feedback
import asyncio


async def openai_response_controller(func, params) -> dict:
    
    # 呼叫 openai
    data = await func(**params)
    
    # 跟 Service 層確認是否要 Feedback
    feedback = get_feedback()
    
    # 暫時簡化邏輯：問題有 50% 機率詢問報表處理，50% 機率詢問回饋，兩個一定會問其中一個
    if feedback:
        result, result.suggested_actions = State.send_response([data.bot_text]), State.send_quick_replies(DefaultQuickReply.FEEDBACK)
    else:
        result, result.suggested_actions = State.send_response(DefaultResponse.DOCUMENT), State.send_quick_replies(DefaultQuickReply.DOCUMENT)

    return { "result": result, "feedback": feedback }


async def document_controller(self, turn_context: TurnContext, text: str):
    
    # 創建 ChatMessage 物件
    chat_message = ChatMessage(user_text=text, history=get_history(), context=get_context())
    
    # 等待 ReportChat 傳初始結果回來
    response = await get_response(
        ReportChat.async_generate_initial_response, { "message" : chat_message }
    )
    await turn_context.send_activity(response) 
    
    # 等待 ReportChat 傳最終結果回來 ; 如果使用者喊暫停，那就不回傳了
    response = await get_response(
        ReportChat.async_generate_final_response, { "message" : chat_message }
    )
    if self.is_processing:
        await turn_context.send_activity(response)
    
    self.is_processing = False
    return


async def feedback_controller(self, flow: ConversationFlow, turn_context: TurnContext, text: str):
    
    # 如果使用者回覆的內容在 FEEDBACK List 當中，就紀錄進資料庫
    if text in DefaultQuickReply.FEEDBACK:
        data = ["*已收到回饋*"]
        result = State.send_response(data)
        flow.set_state(Liberalism())
        return await turn_context.send_activity(result)
    
    else:
        # 如果使用者直接問新問題，改成處理問題
        return await question_controller(self, turn_context, text)


async def question_controller(self, turn_context: TurnContext, text: str):

    # 設成忙碌狀態
    self.is_processing = True
    
    # 創建 ChatMessage 物件並處理問題
    chat_message = ChatMessage(user_text=text, history=get_history(), context=get_context())
    answer_task = asyncio.create_task(
        openai_response_controller(MemoryChat.async_reply, { "chat_message" : chat_message })                                  
    )
    
    # 持續發送罐頭訊息
    delay_messages = get_delay_messages()
    for delay, message in delay_messages:
        sleep_task = asyncio.create_task(asyncio.sleep(delay))
        done, pending = await asyncio.wait(
            {answer_task, sleep_task}, return_when=asyncio.FIRST_COMPLETED
        )
        if answer_task in done:
            break
        elif sleep_task in done:
            if not answer_task.done():
                await turn_context.send_activity(message)
                
    response = answer_task.result()

    # 處理回饋跟狀態
    if not response == None:
        self.is_feedback = response["feedback"]
        self.is_processing = False
        await turn_context.send_activity(response["result"])
    
    return 

