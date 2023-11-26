from enum import Enum
    
class State(Enum):
    NONE = 0
    FEEDBACK = 1
    BUSY = 2

class ConversationFlow:
    def __init__(
        self, last_state: State = State.NONE,
    ):
        self.last_state = last_state