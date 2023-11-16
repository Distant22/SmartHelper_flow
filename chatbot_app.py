import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.schema import Activity
from bot import MyBot,HistoryQueue
import time
import logging
import traceback

load_dotenv()

class AzureBotConfig:
    """Bot Configuration"""

    PORT = int(
        os.environ.get("PORT", 3978)
    )  # PORT from env variable or default to 3978
    APP_ID = os.environ.get("AZUREBOT_ID", "")
    APP_PASSWORD = os.environ.get("AZUREBOT_PASSWORD", "")


CONFIG = AzureBotConfig()
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


async def on_error(context: TurnContext, error: Exception):
    # Log the error to console or app insights (make sure to import logging)
    # Send a message to the user
    await context.send_activity("The bot encounted an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )


# Catch-all for errors to be logged and to prevent the app from crashing
async def on_turn_error(turn_context: TurnContext, error: Exception):
    # Handle error as needed
    await on_error(turn_context, error)


ADAPTER.on_turn_error = on_error

BOT = MyBot()

# Initialize FastAPI app and queue
app = FastAPI()

@app.post("/api/messages")
async def messages(request: Request):
    try:
        body = await request.json()
        activity = Activity().deserialize(body)
        HistoryQueue.push({
            "text": body['text'],
            "time": int(time.time()),
            "role": "user",
            "id": body['from']['id'],
            "url": body.get('service_url',None)
        })
        print("\nQueue的儲存結果：\n",HistoryQueue.display(),"\n")
        auth_header = request.headers.get("Authorization", "")
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

        # 如果 ADAPTER.process_activity 有返回值，则使用该返回值的状态码和内容
        if response:
            return JSONResponse(status_code=response.status, content=response.body)

        # 否则返回默认的 200 OK 响应
        return JSONResponse(status_code=200, content={})  # 使用空字典作为响应内容
    except Exception as e:
        logging.error(f"Error processing message: {e}", exc_info=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=CONFIG.PORT)
    # uvicorn.run(app, port=CONFIG.PORT)
