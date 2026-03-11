import os
import re
from typing import Optional
import serpapi
from pydantic import BaseModel, Field, field_validator
from langchain_core.tools import tool
from datetime import datetime

# 配置 SerpAPI 密钥（注意：建议将密钥放在环境变量，不要硬编码）
os.environ["SERPAPI_API_KEY"] = "3942d2d2ae33793a1757061b3aa710a212c7794897d7c875a68ef00c05240463"

# 1. 完善参数校验（日期格式+范围）
class WeatherInput(BaseModel):
    city: str = Field(description='出游城市/景点，例如：杭州、西湖')
    date: str = Field(description='出游日期，支持两种格式：①单日期YYYY-MM-DD ②日期范围YYYY-MM-DD到YYYY-MM-DD')

    # 校验日期格式合法性
    @field_validator("date")
    def validate_date_format(cls, v):
        # 匹配单日期（YYYY-MM-DD）或日期范围（YYYY-MM-DD到YYYY-MM-DD）
        single_date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        range_date_pattern = r'^\d{4}-\d{2}-\d{2}到\d{4}-\d{2}-\d{2}$'
        
        if not re.match(single_date_pattern, v) and not re.match(range_date_pattern, v):
            raise ValueError(
                "日期格式错误！请使用：①单日期（如2026-03-15） ②日期范围（如2026-03-15到2026-03-20）"
            )
        return v

# 2. 核心工具：结构化解析百度天气结果
@tool(args_schema=WeatherInput)
def serpapi_weather(city: str, date: str) -> str:
    """
    使用SerpAPI调用百度搜索，查询指定城市/景点+日期（范围）的天气，返回结构化结果
    """
    # 构造 SerpAPI 参数
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'baidu',
        'hl': 'zh-CN',
        'gl': 'cn',
        'q': f"{city} {date} 天气预报",  # 优化关键词，提升精准度
        'num': 5  # 只返回前5条结果，减少解析压力
    }

    try:
        # 执行搜索
        search = serpapi.search(params)
        raw_result = search.data

        # 提取百度搜索的核心结果（organic_results 是百度的搜索结果列表）
        organic_results = raw_result.get("organic_results", [])
        if not organic_results:
            return f"❌ 未查询到{city} {date}的天气信息"

        # 结构化解析规则（正则匹配核心天气字段）
        weather_info = []
        # 匹配规则：温度（如 15℃~25℃）、天气（晴/多云/雨）、风力（东风3级）
        temp_pattern = r'(\d+℃[~-]\d+℃)|(\d+℃)'
        weather_pattern = r'(晴|多云|阴|小雨|中雨|大雨|暴雨|雪|雷阵雨|雾)'
        wind_pattern = r'([东南西北]风\d+级)|(微风|无风)'

        # 遍历搜索结果，提取有效信息
        for idx, result in enumerate(organic_results[:3], 1):  # 只解析前3条结果
            title = result.get("title", "")
            snippet = result.get("snippet", "")  # 百度搜索结果的摘要（核心信息）
            full_text = f"{title} {snippet}"

            # 提取字段
            temp = re.search(temp_pattern, full_text)
            weather = re.search(weather_pattern, full_text)
            wind = re.search(wind_pattern, full_text)

            # 只保留有有效信息的结果
            if temp or weather or wind:
                weather_info.append({
                    "来源": title[:50],  # 截断过长标题
                    "温度": temp.group() if temp else "未知",
                    "天气": weather.group() if weather else "未知",
                    "风力": wind.group() if wind else "未知"
                })

        # 格式化返回结果
        if not weather_info:
            return f"❌ 未解析到{city} {date}的结构化天气信息"
        
        # 拼接结构化结果
        result_str = f"🌤 {city} {date} 天气查询结果\n"
        result_str += "-" * 40 + "\n"
        for info in weather_info:
            result_str += (
                f"📌 来源：{info['来源']}\n"
                f"🌡 温度：{info['温度']}\n"
                f"☁ 天气：{info['天气']}\n"
                f"💨 风力：{info['风力']}\n"
                f"-" * 40 + "\n"
            )
        # 出行建议
        bad_weather = ["小雨", "中雨", "大雨", "暴雨", "雪", "雷阵雨"]
        has_bad_weather = any([info['天气'] in bad_weather for info in weather_info])
        result_str += f"💡 出行建议：{'建议携带雨具/注意保暖' if has_bad_weather else '天气良好，适合出行'}"

        return result_str

    except Exception as e:
        return f"❌ 查询失败：{str(e)}（可能原因：SerpAPI密钥无效/网络问题/日期格式错误）"
