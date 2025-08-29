# backend.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import os
from ddgs import ddg_search

load_dotenv()
api_key = os.getenv('OPENAI_KEY')

# -------------------
# 1. LLM
# -------------------
llm = ChatOpenAI(model='gpt-5-nano',api_key=api_key)

# -------------------
# 2. Tools
# -------------------
# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}




@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()


import requests


@tool
def get_weather(city: str) -> dict:
    """
    Fetch current weather for a given city using Open-Meteo API.
    Returns JSON only (city, temperature, windspeed, weather_code, description).
    """

    try:
        # Step 1: Convert city → latitude, longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url, timeout=10).json()

        if "results" not in geo_res or len(geo_res["results"]) == 0:
            return {"error": f"Could not find location for '{city}'"}

        latitude = geo_res["results"][0]["latitude"]
        longitude = geo_res["results"][0]["longitude"]

        # Step 2: Fetch current weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        weather_res = requests.get(weather_url, timeout=10).json()

        if "current_weather" not in weather_res:
            return {"error": f"Weather data not available for '{city}'"}

        current = weather_res["current_weather"]
        temp = current["temperature"]
        wind = current["windspeed"]
        code = current["weathercode"]

        # Map weather code → description
        weather_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
            61: "Light rain", 71: "Light snow", 80: "Rain showers"
        }

        description = weather_map.get(code, "Unknown conditions")

        return {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": temp,
            "windspeed_kmh": wind,
            "weather_code": code,
            "description": description
        }

    except Exception as e:
        return {"error": str(e)}




tools = [search_tool, get_stock_price, calculator, get_weather]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)

