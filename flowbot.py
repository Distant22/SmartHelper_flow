from datetime import datetime
from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    TurnContext,
    UserState,
    MessageFactory,
)

from data_models import ConversationFlow, State, UserFeedback
from botbuilder.schema import CardAction, ActionTypes, SuggestedActions
import random
import time

class ValidationResult:
    def __init__(
        self, is_valid: bool = False, value: object = None, message: str = None
    ):
        self.is_valid = is_valid
        self.value = value
        self.message = message

async def late_response(
    turn_context: TurnContext, question: str, feedback: UserFeedback, flow: ConversationFlow
):
    # 如果使用者沒有要處理報表 or 處理完了，就跑進來這裡
    if question == "handle_result":
        feedback.handle_document = 0
        flow.last_state = State.NONE
        if random.randint(0,1) == 0:
            return { "data":"＊執行結果＊", "feedback": False}
        else:
            return { "data":"＊執行結果＊", "feedback": True }
    elif flow.last_state == State.BUSY:
        # 設定使用者的回應選項：點“停止”便停下 ； 總共做三個階段
        time.sleep(3)
        feedback.handle_document += 1
        if feedback.handle_document == 4:
            return await late_response(turn_context,"handle_result", feedback, flow)
        send_msg = MessageFactory.text(question+" ; 目前在階段"+str(feedback.handle_document))
        send_msg.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="停止",
                    type=ActionTypes.im_back,
                    value="停止"
                )
            ]
        )
        await turn_context.send_activity(send_msg)  
        return await late_response(turn_context,"handle_document", feedback, flow)

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

        self.conversation_state = conversation_state
        self.user_state = user_state

        self.flow_accessor = self.conversation_state.create_property("ConversationFlow")
        self.feedback_accessor = self.user_state.create_property("UserFeedback")

    async def on_message_activity(self, turn_context: TurnContext):
        
        # 每次使用者傳訊息就進來這裡
        try:
            feedback = await self.feedback_accessor.get(turn_context, UserFeedback)
            flow = await self.flow_accessor.get(turn_context, ConversationFlow)

            await self._fill_out_user_feedback(flow, feedback, turn_context)

            # Save changes to UserState and ConversationState
            await self.conversation_state.save_changes(turn_context)
            await self.user_state.save_changes(turn_context)
        except Exception as e:
            print("Error in message activity:",e)


    async def _fill_out_user_feedback(
        self, flow: ConversationFlow, feedback: UserFeedback, turn_context: TurnContext
    ):
        """
        這個函式會根據使用者目前的狀態調整Bot的回覆內容：
        
        feedback - 紀錄本次訊息是否向使用者詢問回饋（回覆很好｜普通｜很差）
        ---------------------------------------------------------
        0 - 並沒有跟使用者要回饋
        1 - 跟使用者要回饋，使用者尚未答覆
        2 - 使用者給出回饋的答覆
        
        State - 紀錄Bot的目前訊息處理狀況
        ---------------------------------------------------------
        NONE - 預設狀態，接收使用者的問題並處理
        FEEDBACK - 處理完問題，準備向使用者詢問回饋（僅有一定機率會觸發）
        BUSY - 處理報表的狀態，處理報表結束後會回到 NONE
        
        """
        user_input = turn_context.activity.text.strip()  
        
        # FEEDBACK 狀態代表使用者給出了回饋 -> 儲存回饋並結束狀態
        if flow.last_state == State.FEEDBACK and (
            user_input == "不滿意" or user_input == "普通" or user_input == "滿意"
        ):
            await turn_context.send_activity(
                MessageFactory.text(
                    f"收到回饋： '{user_input}'"
                )
            )
            feedback.status = 2
            feedback.user = user_input
            # 在這邊將 Feedback 資訊存進 data_info

            # 重製使用者的狀態
            feedback.status = 0
            feedback.user = None
            flow.last_state = State.NONE

        # None 狀態代表使用者問了問題 -> 呼叫幫手＆詢問使用者回饋
        elif not flow.last_state == State.BUSY:
            
            await turn_context.send_activity(
                MessageFactory.text(f"收到訊息： '{user_input}'")
            )
            
            # 如果使用者要處理報表，讓使用者進入一連串的報表處理階段
            if user_input == "報表": 
                flow.last_state = State.BUSY
                try:
                    result = await late_response(turn_context,"handle_document", feedback, flow)
                    if not result == None:
                        await turn_context.send_activity(result['data'])
                    print("result 為",result)
                except Exception as e:
                    print("Error in handle document:",e)
                    flow.last_state = State.NONE
                    feedback.handle_document = 0
                    return await turn_context.send_activity("伺服器出錯，請重新問問題")
                
            # 使用者不是問報表 or 報表執行完了 -> 回傳結果
            else:
                result = await late_response(turn_context,"handle_result", feedback, flow)
                await turn_context.send_activity(result['data'])
            
            # 如果 Bot 有想跟使用者要 feedback 便進來這
            if result['feedback']:
                reply = MessageFactory.text(feedback.bot)
                reply.suggested_actions = SuggestedActions(
                    actions=[
                        CardAction(
                            title="不滿意",
                            type=ActionTypes.im_back,
                            value="不滿意"
                        ),
                        CardAction(
                            title="普通",
                            type=ActionTypes.im_back,
                            value="普通"
                        ),
                        CardAction(
                            title="滿意",
                            type=ActionTypes.im_back,
                            value="滿意"
                        ),
                    ]
                )
                await turn_context.send_activity(reply)
                feedback.status = 1
                flow.last_state = State.FEEDBACK
            else:
                flow.last_state = State.NONE
        
        # BUSY 狀態代表Bot正在忙，無視使用者的任何Input
        elif flow.last_state == State.BUSY:
            try:
                if user_input == "停止":
                    feedback.handle_document = 0
                    flow.last_state = State.NONE
                    return await turn_context.send_activity("報表停止處理。")
                else:
                    return await turn_context.send_activity("在忙別吵啦")
            except Exception as e:
                flow.last_state = State.NONE
                feedback.handle_document = 0
                print("Error in busy state:",e)
                return await turn_context.send_activity("伺服器出錯，請重新問問題")