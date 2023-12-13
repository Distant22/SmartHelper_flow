from botbuilder.core import TurnContext
from data_models import State, DefaultQuickReply, DefaultResponse
from service import get_feedback, get_delay_messages, get_response
import asyncio, random

async def question_controller(text: str) -> dict:
    
    # 用異步的方式處理問題；這個函式會被 async_task_controller() 呼叫
    data = asyncio.create_task(
        get_response(text)                                
    )
    done, pending = await asyncio.wait(
        {data}, return_when=asyncio.FIRST_COMPLETED
    )
    if data in done:
        data = data.result()
    
    feedback = get_feedback()
    
    # 暫時簡化邏輯：問題有 50% 機率詢問報表處理，50% 機率詢問回饋，兩個一定會問其中一個
    if feedback:
        result, result.suggested_actions = State.send_response(data), State.send_quick_replies(DefaultQuickReply.FEEDBACK)
    else:
        result, result.suggested_actions = State.send_response(DefaultResponse.DOCUMENT), State.send_quick_replies(DefaultQuickReply.DOCUMENT)

    return { "result": result, "feedback": feedback }


async def document_controller(func, params):
    
    # 呼叫處理報表的函式
    data = await func(**params)
    
    # 暫時簡化邏輯：用 bot_text / analysis_description 判斷文件處理到哪個階段
    if not data.bot_text == None:
        result = State.send_response([data.bot_text])
    elif not data.analysis_description == None:
        result, result.suggested_actions = State.send_response([data.analysis_description]), State.send_quick_replies(DefaultQuickReply.STOP)
    
    return result


async def feedback_controller(text: str):
    """
    判斷使用者是不是在提供回饋（Quick Reply）
    
    text : 只要不是 Quick Reply 中的選項，就視為新的問題做處理（回傳 None，讓主程式改去呼叫 Question Controller)
    """
    if text in DefaultQuickReply.FEEDBACK:
        data = ["*已收到回饋*"]
        result = State.send_response(data)
        return result
    else:
        return None


async def async_task_controller(turn_context: TurnContext, text: str):
    """
    處理罐頭訊息的函式
    
    text : 使用者傳的訊息，這邊會呼叫 question_controller 來處理訊息
    """
    answer_task = asyncio.create_task(
        question_controller(text)                                  
    )
    delay_messages = get_delay_messages()
    for delay, message in delay_messages:
        sleep_task = asyncio.create_task(asyncio.sleep(delay))
        done, pending = await asyncio.wait(
            {answer_task, sleep_task}, return_when=asyncio.FIRST_COMPLETED
        )
        if answer_task in done:
            response = answer_task.result()
            break
        elif sleep_task in done:
            if not answer_task.done():
                await turn_context.send_activity(message)
    return response

