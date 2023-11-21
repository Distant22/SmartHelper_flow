from dotenv import load_dotenv

load_dotenv()
from langchain.vectorstores import MongoDBAtlasVectorSearch
from trendychat.tools.db_connector import MongoSingleton
from trendychat.configs import EbeddingConfig, LLMConfig
from trendychat.llm import get_embedding_model
import os
from trendychat.llm import openai_reponse
from trendychat.chain.simple_chat import reply_message

#
message = """

user:研究發展處研發長是誰？
bot:東海大學的研究發展處研發長是林惠真老師喔！😊 你可以透過電子郵件hclin@thu.edu.tw或聯絡電話04-23590121 # 32418、32419與他聯繫。更多資訊可以參考他的個人網站 https://biology.thu.edu.tw/front/member/member2/Ecology/member.php?ID=dGh1X2Jpb2xvZ3kmRWNvbG9neQ==&P哦！👍
user:那共同學科暨通識教育中心有誰?
bot: 抱歉，我現在無法提供共同學科暨通識教育中心的具體人員名單。但你可以透過東海大學的官方網站或聯絡學校的相關部門來獲得更詳細的資訊哦！😊 如果你有其他問題，也歡迎隨時問我喔！👌
user:你沒有共同學科暨通識教育中心的名單？
bot:對不起，我剛剛的回答可能讓你誤解了。東海大學的共同學科暨通識教育中心的人員包括主任王崇名老師，專員李佩玲，組員游麗瑾，約聘組員劉麗珠，以及計畫人員吳孟珊。你可以透過他們的電子郵件或聯絡電話來與他們聯繫。😊 更多的資訊可以在[這裡](https://ge.thu.edu.tw/v2/4_members.php?cate=D)找到哦！👍
user:裡面有約聘的嗎？
bot:是的，共同學科暨通識教育中心的人員中有約聘組員劉麗珠老師哦！😊 你可以透過電子郵件lichu@thu.edu.tw或聯絡電話04-23590121#22701與她聯繫。更多的資訊可以在[這裡](https://ge.thu.edu.tw/v2/4_members.php?cate=D)找到哦！👍
user:研究發展處長官是誰？
"""

embedding_config = EbeddingConfig()
gpt_config = LLMConfig()
db_name = os.getenv("MONGODB_DATABASE_NANE")
collection_name = os.getenv("MONGODB_COLLECTION_VECTOR")
mongo_instance = MongoSingleton()

collection = mongo_instance[db_name][collection_name]
index_name = os.getenv("MONGODB_COLLECTION_VECTOR_SPECIAL_INDEX")

model_config = embedding_config.get()
embeddings = get_embedding_model(model_config=model_config)

vectorstore = MongoDBAtlasVectorSearch(
    collection=collection, embedding=embeddings, index_name=index_name
)

contexts = vectorstore.similarity_search(query=message, k=5)
print(contexts[0].page_content)
print("=" * 80)
print(contexts[1].page_content)
print("=" * 80)
print(contexts[2].page_content)
print("=" * 80)
print(contexts[3].page_content)
print("=" * 80)
print(contexts[4].page_content)
print("=" * 80)

print(contexts)
docs = [contexts[i].page_content for i in range(len(contexts))]
# answer = reply_message(message=message, contexts=contexts)

SYSTEM_PROMPT = (
    "Please respond to the user's question based on the dialogue history (history) and references provided by the assistant.Notices:\n\n "
    + os.getenv("SYSTEM_PROMPT", "")
)


prompt = {
    "system": SYSTEM_PROMPT,
    # "system": """Please respond to the user's question based on the dialogue history (history) and references provided by the assistant.Notices:\n\n
    #             Your name is 東東妞. You are a GPT4 AI rep from 東海大學. For queries: \n
    #             1.Without a direct answer, especially for personnel info, ask for details or direct to 'https://www.thu.edu.tw/'. No random replies.\n
    #             2.If an answer exists and that reference provides a URL, share it depending on the context.\n
    #             3.Answer with enthusiasm and emoticons, but be concise.\n
    #             4.Be mindful of the user's tone, especially when they are impatient. It's appropriate to apologize or clarify the user's question in such instances.\n
    #             5.Use traditional chinese to reply.
    # """,
    "assistant": {
        "history": [
            "研究發展處研發長是誰？",
            "東海大學的研究發展處研發長是林惠真老師喔！😊 你可以透過電子郵件hclin@thu.edu.tw或聯絡電話04-23590121 # 32418、32419與他聯繫。更多資訊可以參考他的個人網站 https://biology.thu.edu.tw/front/member/member2/Ecology/member.php?ID=dGh1X2Jpb2xvZ3kmRWNvbG9neQ==&P哦！👍",
            "那共同學科暨通識教育中心有誰?",
            "抱歉，我現在無法提供共同學科暨通識教育中心的具體人員名單。但你可以透過東海大學的官方網站或聯絡學校的相關部門來獲得更詳細的資訊哦！😊 如果你有其他問題，也歡迎隨時問我喔！👌",
            "你沒有共同學科暨通識教育中心的名單？",
            "對不起，我剛剛的回答可能讓你誤解了。東海大學的共同學科暨通識教育中心的人員包括主任王崇名老師，專員李佩玲，組員游麗瑾，約聘組員劉麗珠，以及計畫人員吳孟珊。你可以透過他們的電子郵件或聯絡電話來與他們聯繫。😊 更多的資訊可以在[這裡](https://ge.thu.edu.tw/v2/4_members.php?cate=D)找到哦！👍",
            "裡面有約聘的嗎？",
            "是的，共同學科暨通識教育中心的人員中有約聘組員劉麗珠老師哦！😊 你可以透過電子郵件lichu@thu.edu.tw或聯絡電話04-23590121#22701與她聯繫。更多的資訊可以在[這裡](https://ge.thu.edu.tw/v2/4_members.php?cate=D)找到哦！👍",
            "你是誰？",
            "東東妞",
        ],
        "references": docs,
    },
    "user": "你可以搞清楚再回答嗎？我是說你代表誰？",
}


message = [
    {"role": "system", "content": prompt["system"]},
    {"role": "assistant", "content": str(prompt["assistant"])},
    {"role": "user", "content": prompt["user"]},
]


answer = openai_reponse(messages=message, model_config=gpt_config.get())
print("*" * 100)
print(answer["choices"][0]["message"]["content"])
breakpoint()
