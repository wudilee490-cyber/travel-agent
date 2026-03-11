import os
import serpapi
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# 你的密钥
os.environ["SERPAPI_API_KEY"] = "3942d2d2ae33793a1757061b3aa710a212c7794897d7c875a68ef00c05240463"

# 输入模型
class CityInput(BaseModel):
    city: str = Field(description="城市名称，如：杭州、成都、西安")

@tool(args_schema=CityInput)
def city_travel_guide(city: str) -> str:
    """
    查询一个城市的热门景点和特色美食，返回结构化、干净的结果
    """
    params = {
        "api_key": os.environ["SERPAPI_API_KEY"],
        "engine": "google",  # 关键：必须用 google
        "q": f"{city} 必去景点 特色美食",
        "hl": "zh-CN",
        "gl": "cn",
        "google_domain": "google.com.hk",
    }

    try:
        result = serpapi.search(params).data
        # 取前 8 条有效搜索结果
        results = result.get("organic_results", [])[:8]
        return results

    except Exception as e:
        return f"查询失败：{str(e)}"
