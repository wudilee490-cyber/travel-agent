import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import serpapi

os.environ["SERPAPI_API_KEY"] = "3942d2d2ae33793a1757061b3aa710a212c7794897d7c875a68ef00c05240463"

class HEInput(BaseModel):
    departure: Optional[str] = Field(default=None, description="出发地")
    arrival: Optional[str] = Field(default=None, description="目的地")
    departure_time: Optional[str] = Field(default=None, description="出发时间")
    return_time: Optional[str] = Field(default=None, description="回程时间")
    adults: Optional[int] = Field(default=1, description="成人数量")
    children: Optional[int] = Field(default=0, description="儿童数量")
    infants_in_seat: Optional[int] = Field(default=0, description="占座婴儿数量")
    infants_without_seat: Optional[int] = Field(default=0, description="不占座婴儿数量")

    model_config = {
        "extra": "forbid"  # 禁止额外字段
    }

class HEInputSchema(BaseModel):
    params: HEInput
    
    model_config = {
        "extra": "forbid"  # 禁止额外字段
    }

@tool(args_schema=HEInputSchema)
def HE_finders(params: HEInput) -> str:
    """查询高铁或动车信息，返回结构化搜索结果"""
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'baidu',
        'hl': 'zh-CN',
        'gl': 'cn',
        'q': '高铁动车',
        'departure': params.departure,
        'arrival_id': params.arrival,
        'outbound_date': params.departure_time,
        'return_date': params.return_time,
        'currency': 'CNY',
        'adults': params.adults,
        'infants_in_seat': params.infants_in_seat,
        'infants_on_lap': params.infants_without_seat,
        'children': params.children

    }

    # 执行搜索
    try:
        result = serpapi.search(params).data
        # 取前 8 条有效搜索结果
        results = result.get("organic_results", [])[:8]
        return results
    except Exception as e:
        return f"❌ 查询失败：{str(e)}"
