import os
from typing import Optional
import serpapi
from pydantic import BaseModel, Field
from langchain_core.tools import tool
os.environ["SERPAPI_API_KEY"] = "3942d2d2ae33793a1757061b3aa710a212c7794897d7c875a68ef00c05240463"

class WeatherInput(BaseModel):
    city: str = Field(description='出游城市')
    date: str = Field(description='出游日期，格式:YYYY-MM-DD到YYYY-MM-DD')

@tool(args_schema=WeatherInput)
def serpapi_weather(city: str, date: str) -> str:
    """
    使用SerpAPI查询指定地点(城市/景点)和日期的天气，返回结构化结果
    """
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'baidu',
        'hl': 'zh-CN',
        'gl': 'cn',
        'city': city,
        'date':date

    }
    try:
        # 执行搜索
        search = serpapi.search(params)
        result = search.data
        # 解析并格式化结果
        return f"🌤 {city} {date} 天气\n{result}"
    except Exception as e:
        return f"查询失败：{str(e)}"