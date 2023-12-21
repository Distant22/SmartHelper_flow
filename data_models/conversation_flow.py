from .state import State, Socialism, Liberalism

class ConversationFlow:
    """
    ConversationFlow 藉由控制 State 來管理目前的對話階段 Bot 應該回覆什麼。

    切換體制：
    flow.set_state(Liberalism())
    
    取得目前體制：
    flow.last_state 
    """
    def __init__(
        self, last_state: State = Liberalism()
    ):
        self.last_state = last_state.__class__.__name__
    
    def set_state(self, new_state: State):
        self.last_state = new_state.__class__.__name__
        return new_state