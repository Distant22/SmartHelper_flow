from abc import ABC
from botbuilder.schema import CardAction, ActionTypes, SuggestedActions
from botbuilder.core import (
    MessageFactory
)
import random
from typing import List, Union

class DefaultResponse:
    FEEDBACK = ["對於本次的回答滿意嗎？"]
    FEEDBACK_DOCUMENT = ["你覺得哪一次回答的比較好？"]
    DOCUMENT = ["我們認為本次問題需要調用報表來回答，請問是否接受調用報表？"]
    BUSY = ["在忙","快好了"]
    DELAY = [
        "稍等一下下，馬上就好！",
        "好問題！給我點時間來個完美回答～",
        "嗯～讓我思考一番，給您最佳答案！",
        "思考模式啟動中，請給我點靈感的時間。",
        "已經快完成啦，等一下下！",
        "耐心點，好東西正在醞釀中呢！"
    ]
    
class DefaultQuickReply:
    FEEDBACK = ["滿意","不滿意"]
    FEEDBACK_DOCUMENT = ["第一個","第二個","都很好"]
    STOP = ["暫停"]
    DOCUMENT = ["調用報表","不調用報表"]
    DEFAULT = ["選項一","選項二","選項三"]

class State(ABC):
    """
    State 為各個政府體制的父類別。
    
    send_response()
    回傳 Bot 在使用者傳訊息時要回覆的內容
    
    send_quick_replies()
    回傳 Bot 讓使用者可以選的選項
    """
    def send_response(response: Union[List[str], DefaultResponse] = None) -> str:
        text = ""
        if response == None:
            text = random.choice(DefaultResponse.FEEDBACK)
        else:
            text = random.choice(response)
        return MessageFactory.text(text)
    
    def send_quick_replies(replies: Union[List[str], DefaultQuickReply] = None) -> SuggestedActions:
        if replies == None:
            replies = DefaultQuickReply.FEEDBACK 
        """ 將每個選項用迴圈實作出來 """
        action_list = [
            CardAction(
                title=reply,
                type=ActionTypes.im_back,
                value=reply
            ) 
            for reply in replies
        ]
        return SuggestedActions(actions = action_list)

class Communism(State):
    """
    共產主義：傳任何訊息都不理會
    """

class Liberalism(State):
    """
    自由主義：一傳訊息就馬上視為新的問題
    """

class Socialism(State):
    """
    社會主義：僅處理一部份訊息
    """