import os
from typing import Optional
import serpapi
from pydantic import BaseModel, Field
from langchain_core.tools import tool
os.environ["SERPAPI_API_KEY"] = "3942d2d2ae33793a1757061b3aa710a212c7794897d7c875a68ef00c05240463"

class HotelInput(BaseModel):
    q : str = Field(description='酒店位置')
    check_in_data : str = Field(description='入住日期，格式:YYYY-MM-DD. e.g. 2024-06-22')
    check_out_data :str = Field(description='离店日期，格式:YYYY-MM-DD. e.g. 2024-06-28')
    hotel_class :Optional[str] = Field(None,description='酒店类型')
    room_class : Optional[str] = Field(None,description='房间类型')
    rooms : Optional[int] = Field(1,description='房间个数')
    adults : Optional[int] = Field(1,description='成人人数')
    children : Optional[int] = Field(0,description='儿童人数')
    sort_by : Optional[str]


class HotelInputSchema(BaseModel):
    params: HotelInput
    

@tool(args_schema=HotelInputSchema)
def Hotel_finders(params: HotelInput) -> str:
    """查询酒店信息，返回酒店搜索结果"""
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'baidu',
        'hl': 'zh-CN',
        'gl': 'cn',
        'q': params.q,
        'check_in_date': params.check_in_date,
        'check_out_date': params.check_out_date,
        'currency': 'CNY',
        'adults': params.adults,
        'children': params.children,
        'rooms': params.rooms,
        'sort_by': params.sort_by,
        'hotel_class': params.hotel_class,
        'room_class': params.room_class
    }


    # 执行搜索
    try:
        result = serpapi.search(params).data
        # 取前 8 条有效搜索结果
        results = result.get("organic_results", [])[:8]
        return results
    except Exception as e:
        return f"❌ 查询失败：{str(e)}"