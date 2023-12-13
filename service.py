import os, random, asyncio
from data_models import DefaultResponse

def get_feedback():
    feedback = random.choice([True, False])
    print("本次是否要求回饋：",feedback)
    return feedback

def get_history():
    return [""]

async def get_response(text: str):
    await asyncio.sleep(3)
    return ["*回覆*"]
    
def get_current_path(file_name):
    if not file_name:
        return os.path.dirname(os.path.abspath(__file__))
    else:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_directory, file_name)

def get_delay_messages():
    messages = DefaultResponse.DELAY
    selected_messages = random.sample(messages, 5)
    selected_messages.append(
        "非常抱歉讓您稍作等待，由於目前使用者眾多，我們的系統暫時達到了服務高峰。若您仍未收到回覆，要麻煩您再次傳訊，感謝您的理解與耐心。"
    )
    time_cutting = [3, 8, 8, 8, 8, 8]
    return [(i, message) for i, message in zip(time_cutting, selected_messages)]

def get_context():
    return [
        str(
            {
                "file_name": "Y2207 CSP價格冊 (永久型 ＆軟體訂閱)-Sales.xlsx",
                "file_path": get_current_path("Y2207 CSP價格冊 (永久型 ＆軟體訂閱)-Sales.xlsx"),
                "file_description": "這是一個示例報表的描述",
                "file_sheets": [
                    {
                        "sheet_name": "CSP永久授權_商用",
                        "sheet_description": "分頁 'CSP永久授權_商用' 的描述",
                        "sheet_column": [
                            "Product",
                            "ProductId",
                            "SkuId",
                            "SkuTitle",
                            "Segment",
                            "建議售價未稅",
                            "經銷價(未稅)",
                            "聯強料號\n(便於查價用，請上CSP平台下單)",
                            "SkuDescription",
                        ],
                        "sheet_detail": '                                 Product     ProductId  SkuId  ...   經銷價(未稅)      聯強料號\\n(便於查價用，請上CSP平台下單)                                     SkuDescription\n0                       Access LTSC 2021  DG7GMGF0D7FV      1  ...    5400.0         CSP ACCESS LTSC 2021  Access LTSC 2021 lets you build and share a da...\n1             BizTalk Server 2020 Branch  DG7GMGF0G49Z      2  ...   38904.0                          NaN  This specialty version of BizTalk Server is de...\n2         BizTalk Server 2020 Enterprise  DG7GMGF0G49X      1  ...  680645.0                          NaN  For those with enterprise-level requirements f...\n3           BizTalk Server 2020 Standard  DG7GMGF0G49W      2  ...  156049.0                          NaN  For organizations with moderate volume and dep...\n4                        Excel LTSC 2021  DG7GMGF0D7FT      2  ...    5400.0          CSP EXCEL LTSC 2021  Excel LTSC 2021 allows you to analyze data wit...\n..                                   ...           ...    ...  ...       ...                          ...                                                ...\n65  Windows Server Data Center Core 2022  DG7GMGF0D65N      2  ...  189475.0   CSP WIN SVR 2022 DC 16Core  Windows Server 2022 is the cloud-ready operati...\n66     Windows Server Standard Core 2022  DG7GMGF0D5RK      5  ...   32902.0  CSP WIN SVR 2022 Std 16Core  Windows Server 2022 is the cloud-ready operati...\n67     Windows Server Standard Core 2022  DG7GMGF0D5RK      4  ...    4124.0   CSP WIN SVR 2022 Std 2Core  "Windows Server 2022 is the cloud-ready operat...\n68                        Word LTSC 2021  DG7GMGF0D7D3      2  ...    5400.0                          NaN  Word LTSC 2021 enables you to create compellin...\n69                Word LTSC for Mac 2021  DG7GMGF0D7DC      2  ...    5400.0                          NaN  Word 2021 for Mac enables you to create compel...\n\n[70 rows x 9 columns]',
                        "sheet_rows": 70,
                        "sheet_note": "在本分頁裡，全部內容應有70筆，此處提供70筆。",
                    }
                ],
            }
        )
    ]