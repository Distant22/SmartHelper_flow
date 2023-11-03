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

# 设定延时消息列表
delay_messages = [
    (2, "請稍待片刻"),
    (3, "這是一個好問題"),
    (4, "讓我仔細想一想"),
    (20, "還在思考中..."),
    (25, "幾乎完成..."),
]


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
                    return
                elif sleep_task in done and not answer_task.done():
                    await turn_context.send_activity(message)

            # 如果答案还没准备好，等待它完成
            if not answer_task.done():
                await answer_task
                await turn_context.send_activity(answer_task.result())
        except Exception as e:
            logging.error(f"Error in on_message_activity: {e}", exc_info=True)
            # 此处可以发送一个自定义的错误消息给用户
            await turn_context.send_activity("抱歉，處理您的訊息時發生了錯誤。")
            raise

    async def process_question_and_send_updates(self, question):
        try:
            # 异步调用自定义回复函数
            return await SimpleChat.async_reply(question)
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
