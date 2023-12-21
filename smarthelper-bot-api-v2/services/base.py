from abc import ABC, abstractmethod

class BaseAction(ABC):
    def __init__(self) -> None:
        self.user_id: str = None
        
        pass
    @abstractmethod
    def run():
        pass
    