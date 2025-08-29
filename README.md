# ThreadMind 🧠

A sophisticated AI conversation engine that weaves together multiple capabilities through an intelligent thread-based system. Built with LangGraph, LangChain, and Streamlit, ThreadMind seamlessly handles web search, weather updates, stock prices, and calculations while maintaining contextual awareness.

## Features

- 🤖 Interactive chat interface built with Streamlit 
- 💬 Multi-turn conversation support with persistent chat history
- 🔍 Integrated tools and capabilities:
  - Web search using DuckDuckGo
  - Real-time stock price lookup
  - Current weather information
  - Basic calculator functions
- 📝 Conversation history management with unique thread IDs
- 💾 Persistent storage using SQLite database

## Technology Stack

- LangGraph - For building the conversational flow graph
- LangChain - For LLM integration and tools
- Streamlit - For the web interface
- OpenAI GPT Models - For natural language processing
- SQLite - For conversation persistence

## Setup

1. Clone this repository
2. Install dependencies:
```sh
pip install streamlit langchain langgraph python-dotenv requests
```

3. Create a `.env` file with your API keys:
```
OPENAI_KEY=your_openai_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=your_langchain_endpoint
LANGCHAIN_API_KEY=your_langchain_key
LANGCHAIN_PROJECT=your_project_name
```

## Running the Application

1. Start the Streamlit server:
```sh
streamlit run chatbot_frontend.py
```

2. Open your browser and navigate to http://localhost:8501

## Usage

- Start a new chat using the "New Chat" button in the sidebar
- View previous conversations by selecting their thread IDs
- Type your messages in the chat input at the bottom
- The chatbot will automatically detect when to use appropriate tools based on your queries

## Project Structure

- `chatbot_frontend.py` - Streamlit UI implementation
- `chatbot_backend.py` - Core chatbot logic and tool implementations
- `chatbot.db` - SQLite database for conversation storage

## Tools Available

1. **Web Search**: Search the internet using DuckDuckGo
2. **Calculator**: Perform basic arithmetic operations (add, subtract, multiply, divide)
3. **Stock Price**: Get real-time stock prices using Alpha Vantage API
4. **Weather**: Get current weather information for any city using Open-Meteo API

## License

MIT