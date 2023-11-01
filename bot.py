'''
Author: Shawn
Date: 2023-09-05 14:03:31
LastEditTime: 2023-10-13 17:41:19
'''
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
# from modules.call_process import reply_message_sync
from trendychat.chain.simple_chat import SimpleChat


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    async def on_message_activity(self, turn_context: TurnContext):
        print("===>", turn_context.activity.text)
        # replay_text =  await reply_message_sync(turn_context.activity.text)
        replay_text = SimpleChat.reply(turn_context.activity.text)
        await turn_context.send_activity(replay_text)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")


# ================================================================================================
# import asyncio


# class MyBot(ActivityHandler):

#     async def on_message_activity(self, turn_context: TurnContext):
#         print("===>", turn_context.activity.text)

#         # 定義一個非同步函數來等待回覆
#         async def get_reply():
#             return SimpleChat.reply(turn_context.activity.text)

#         # 定義一個非同步函數來等待5秒並傳送"稍待片刻"的訊息
#         async def wait_and_notify():
#             await asyncio.sleep(3)
#             await turn_context.send_activity("稍待片刻...讓我想想...")
#             return "稍等"  # 這裡加上返回值

#         # 使用asyncio.gather來等待上述兩個任務
#         done, pending = await asyncio.wait([get_reply(), wait_and_notify()], return_when=asyncio.FIRST_COMPLETED)

#         # 如果get_reply任務已經完成，取消wait_and_notify任務
#         for task in pending:
#             task.cancel()

#         # 檢查已完成的任務
#         for task in done:
#             if task == get_reply:
#                 replay_text = task.result()
#                 if replay_text:
#                     await turn_context.send_activity(replay_text)

#     async def on_members_added_activity(self, members_added: ChannelAccount, turn_context: TurnContext):
#         for member_added in members_added:
#             if member_added.id != turn_context.activity.recipient.id:
#                 await turn_context.send_activity("Hello and welcome!")
