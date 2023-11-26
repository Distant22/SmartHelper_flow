# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

class UserFeedback:
    def __init__(
        self, 
        status: int = 0, 
        bot: str = "你是否滿意本次回答？", 
        user: str = None,
        handle_document: int = 0
    ):
        self.status = status
        self.bot = bot
        self.user = user 
        self.handle_document = handle_document