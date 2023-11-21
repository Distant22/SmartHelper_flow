# """
# Author: Shawn
# Date: 2023-09-05 14:03:31
# LastEditTime: 2023-10-13 17:41:19
# """
import asyncio
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from typing import Optional, Union

# 假定 SimpleChat.async_reply 是您将要实现的异步方法
from trendychat.chain.simple_chat import SimpleChat
from trendychat.chain.memory_chat import MemoryChat, MemoryMessage
import logging
import random
from datetime import datetime
import os

# from collections import deque
from utils import (
    get_chatlog_data,
    insert_chatlog_data,
    ChatlogData,
    count_tokens,
)

CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", 0))


# 设定延时消息列表
# 定義一個函數來隨機抽取五組訊息，並且每次給予不同的隨機數字以增加活潑感
def generate_lively_messages():
    messages = [
        "稍等一下下，馬上就好！",
        "好問題！給我點時間來個完美回答～",
        "嗯～讓我思考一番，給您最佳答案！",
        "思考模式啟動中，請給我點靈感的時間。",
        "已經快完成啦，等一下下！",
        "耐心點，好東西正在醞釀中呢！",
        "您的請求正在被神速處理中！",
        "感謝等候，您將會聽到令人振奮的答案！",
        "快要準備好給您驚喜了！",
        "答案正疾速向您飛來！",
        "答案正趕來，不遠啦！",
        "給我一點點時間，絕對值得等待！",
        "您的問題太有趣了，讓我仔細研究下！",
        "研究中... 這問題真是挑戰性十足！",
        "稍微等一會，驚喜馬上揭曉！",
        "全力以赴找答案中，不會讓您失望的！",
        "這個問題好，讓我來好好琢磨一番。",
        "我們即將揭曉結果，敬請期待！",
        "安心，我們在為您準備答案。",
        "您的好奇心即將得到滿足，稍候！",
        "一切都在掌握中，答案即將到來。",
    ]
    # 從列表中隨機選取五個不同的訊息
    selected_messages = random.sample(messages, 5)
    selected_messages.append(
        "非常抱歉讓您稍作等待，由於目前使用者眾多，我們的系統暫時達到了服務高峰。若您仍未收到回覆，要麻煩您再次傳訊，感謝您的理解與耐心。"
    )
    time_cutting = [3, 8, 8, 8, 8, 8]
    # 將選取的訊息與一個隨機數字結合，數字範圍1到5

    return [(i, message) for i, message in zip(time_cutting, selected_messages)]


# 呼叫函數並打印結果
delay_messages = generate_lively_messages()


def extract_chatlog(history: list, token_limit: int):
    """
    根據 token_limit 篩選聊天記錄，優先保留較新的資料。
    每次留都要留一組 {"user_text":"...", "bot_text":"..."}。
    如果 token_limit 不夠，則整組不留。
    """
    accumulated_tokens = 0
    filtered_history = []

    # 從最新的記錄開始迭代
    for record in reversed(history):
        user_tokens = int(record.get("user_text_token", 0))
        bot_tokens = int(record.get("bot_text_token", 0))
        if accumulated_tokens + user_tokens + bot_tokens <= token_limit:
            # 如果累加的 token 數量沒有超過限制，則保留該記錄
            filtered_history.append(record["bot_text"])
            filtered_history.append(record["user_text"])
            # filtered_history.append(
            #     {"user": record["user_text"], "bot": record["bot_text"]}
            # )
            accumulated_tokens += user_tokens + bot_tokens
        else:
            # 如果超過限制，則停止迭代
            break

    # 因為我們從最新記錄開始迭代，所以需要反轉列表來保持原始順序
    return list(reversed(filtered_history))


class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        try:
            # 儲存使用者提問相關資訊
            channel_id = turn_context.activity.channel_id
            user_id = turn_context.activity.from_property.id

            chatlog_data = ChatlogData(
                service_url=turn_context.activity.service_url,
                channel_id=channel_id,
                user_id=user_id,
                user_name=turn_context.activity.from_property.name,
                user_text=turn_context.activity.text,
                user_timestamp=datetime.now(),
            )

            # 參照歷史紀錄，並過濾條件
            CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", 0))  # 參考歷史紀錄的筆數

            if CHAT_HISTORY_LIMIT:  # 如果有設定參考歷史紀錄的筆數或大於0
                CHAT_SESSION_DURATION = int(
                    os.getenv("CHAT_SESSION_DURATION", "3")
                )  # 參考歷史紀錄的時間長度
                history = await get_chatlog_data(
                    user_id=user_id,
                    channel_id=channel_id,
                    limit=CHAT_HISTORY_LIMIT,
                    minutes=CHAT_SESSION_DURATION,
                )
                CHAT_TOKEN_LIMIT = int(
                    os.getenv("CHAT_TOKEN_LIMIT", 3000)
                )  # 參考歷史紀錄的token限制
                history = (
                    extract_chatlog(history, token_limit=CHAT_TOKEN_LIMIT)
                    if history
                    else []
                )

            else:
                history = []

            memory_message = MemoryMessage(
                user_text=chatlog_data.user_text,
                history=history,
                user_timestamp=chatlog_data.user_timestamp,
            )

            # 开始获取答案的异步任务
            answer_task = asyncio.create_task(
                self.process_question_and_send_updates(memory_message)
            )

            for delay, message in delay_messages:
                sleep_task = asyncio.create_task(asyncio.sleep(delay))
                done, pending = await asyncio.wait(
                    {answer_task, sleep_task}, return_when=asyncio.FIRST_COMPLETED
                )

                if answer_task in done:
                    result = await answer_task  # .result()
                    await turn_context.send_activity(result.bot_text)
                    # 補充機器人回覆使相關資訊
                    chatlog_data.bot_text = result.bot_text
                    chatlog_data.bot_timestamp = result.bot_timestamp
                    chatlog_data.reference = result.reference
                    chatlog_data.history = history  # 加入歷史對話紀錄
                    # 計算本次的token數量
                    chatlog_data.bot_text_tokens = count_tokens(
                        text=chatlog_data.bot_text
                    )
                    chatlog_data.user_text_tokens = count_tokens(
                        text=chatlog_data.user_text
                    )
                    await insert_chatlog_data(chatlog_data.dict())

                    return
                elif sleep_task in done:
                    if not answer_task.done():
                        await turn_context.send_activity(message)

            # 如果答案还没准备好，等待它完成
            if not answer_task.done():
                result = await answer_task
                await turn_context.send_activity(answer_task.result())
        except Exception as e:
            logging.error(f"Error in on_message_activity: {e}", exc_info=True)
            # 此处可以发送一个自定义的错误消息给用户
            await turn_context.send_activity("抱歉，處理您的訊息時發生了錯誤。")
            raise

    async def process_question_and_send_updates(self, messages: MemoryMessage):
        try:
            # if CHAT_HISTORY_LIMIT >= 0:
            # 处理字典类型的 question
            return await MemoryChat.async_reply(messages)  # 这里添加处理字典的逻辑

            # return {"message": "機器人訊息", "reference": []}

        except Exception as e:
            # 在这里添加更详细的错误日志
            logging.error(
                f"Error in process_question_and_send_updates: {str(e)}", exc_info=True
            )
            raise  # 这里改为重新抛出异常，让 FastAPI 捕获并处理

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("歡迎使用我們的Bot!")
