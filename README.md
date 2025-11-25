# 🚀 THANOS-LEVEL AI STOCK AGENT

A comprehensive AI agent system for stock analysis, news aggregation, and product research with multi-agent orchestration.

## 📁 Project Structure

```
.
├── config.py                    # Configuration and environment variables
├── main.py                      # CLI entry point for the application
├── api.py                       # FastAPI REST API server
├── frontend_example.html        # Example frontend HTML file
├── agents/                      # Individual agent modules
│   ├── __init__.py
│   ├── web_search_agent.py     # DuckDuckGo web search agent
│   ├── stock_agent.py          # Alpha Vantage stock price agent
│   ├── news_agent.py           # News aggregation agent
│   └── research_agent.py       # Product price research agent (ZenRows)
├── orchestrator/                # Orchestration logic
│   ├── __init__.py
│   └── master_orchestrator.py  # Main orchestrator coordinating all agents
├── chatbot/                     # Chatbot interface
│   ├── __init__.py
│   └── financial_chatbot.py    # Main chatbot class
└── requirements.txt             # Python dependencies
```

## 🏗️ Architecture

### Agents (`agents/`)
- **WebSearchAgent**: Handles web searches using DuckDuckGo
- **StockAgent**: Fetches real-time stock data from Alpha Vantage API
- **NewsAgent**: Aggregates news from web search results
- **ResearchAgent**: Scrapes product prices using ZenRows API

### Orchestrator (`orchestrator/`)
- **MasterOrchestrator**: 
  - Analyzes user intent using GPT-4
  - Coordinates multiple agents based on query type
  - Synthesizes responses from all agent results

### Chatbot (`chatbot/`)
- **FinancialChatbot**: Main interface for user interactions

## 🚀 Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
ZENROWS_KEY=your_zenrows_key
```

3. Run the application:

**Option A: CLI Mode (Command Line)**
```bash
python main.py
```

**Option B: FastAPI Server (for Frontend Integration)**
```bash
python api.py
```
Then visit:
- API Documentation: http://localhost:8000/docs
- Example Frontend: Open `frontend_example.html` in your browser

## 🌐 FastAPI REST API

The application is now wrapped in a FastAPI REST API for frontend integration.

### Quick Start with API

1. Start the FastAPI server:
```bash
python api.py
```

2. The API will be available at `http://localhost:8000`

3. Main endpoint: `POST /api/query`
   ```json
   {
     "query": "What's the price of AAPL?",
     "session_id": "optional-session-id"
   }
   ```

4. View interactive API docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Available Endpoints

- `GET /health` - Health check
- `POST /api/query` - Process user queries (main endpoint)
- `GET /api/intent` - Analyze user intent
- `GET /api/agents` - List available agents

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API documentation.

### Frontend Example

An example HTML frontend is included in `frontend_example.html`. Simply:
1. Start the API server: `python api.py`
2. Open `frontend_example.html` in your browser
3. Start chatting!

## 📝 Usage

The chatbot supports various query types:
- Stock prices: "What's the price of AAPL?"
- Financial news: "Latest news about Tesla"
- General news: "What's happening in politics?"
- Product research: "PS5 Pro price in Pakistan"

**CLI Mode:** Type `quit` or `exit` to close the application.

## 🔧 Key Features

- Multi-agent architecture with specialized agents
- Intent analysis using GPT-4
- Real-time stock data integration
- Web search integration for news and context
- Product price scraping with ZenRows
- Intelligent orchestration based on query type

