# """
# Author: Shawn
# Date: 2023-09-05 14:03:31
# LastEditTime: 2023-10-13 17:41:19
# """
import asyncio
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

# 假定 SimpleChat.async_reply 是您将要实现的异步方法
from trendychat.chain.simple_chat import SimpleChat
import logging
import random
import time
from collections import deque

class HistoryQueue:
    max_size = 10  # Maximum size for the queue
    queue = deque(maxlen=max_size)  # Initializing the queue as a class variable

    @classmethod
    def push(cls, item)->list:
        cls.queue.append(item)

    @classmethod
    def display(cls, show_num=3):
        return list(cls.queue)[-show_num:] if show_num else list(cls.queue)

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

def bot_add_queue(text: str, id: str, url: str):
    HistoryQueue.push({
        "text": text,
        "time": int(time.time()),
        "role": "bot",
        "id": id,
        "url": url
    })

class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        try:
            user_message = turn_context.activity.text

            # 开始获取答案的异步任务
            answer_task = asyncio.create_task(
                self.process_question_and_send_updates(user_message)
            )

            for delay, message in delay_messages:
                sleep_task = asyncio.create_task(asyncio.sleep(delay))
                done, pending = await asyncio.wait(
                    {answer_task, sleep_task}, return_when=asyncio.FIRST_COMPLETED
                )

                if answer_task in done:
                    await turn_context.send_activity(answer_task.result())
                    bot_add_queue(answer_task.result(), turn_context.activity.recipient.id, turn_context.activity.service_url)
                    return
                elif sleep_task in done and not answer_task.done():
                    await turn_context.send_activity(message)

            # 如果答案还没准备好，等待它完成
            if not answer_task.done():
                await answer_task
                await turn_context.send_activity(answer_task.result())
                bot_add_queue(answer_task.result(), turn_context.activity.recipient.id, turn_context.activity.service_url)
        except Exception as e:
            logging.error(f"Error in on_message_activity: {e}", exc_info=True)
            # 此处可以发送一个自定义的错误消息给用户
            await turn_context.send_activity("抱歉，處理您的訊息時發生了錯誤。")
            raise

    async def process_question_and_send_updates(self, question):
        try:
            # 异步调用自定义回复函数
            # return await SimpleChat.async_reply(question)
            return "機器人訊息"
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
