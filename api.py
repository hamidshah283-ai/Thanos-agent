# ==================== FASTAPI ENDPOINTS ====================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
from chatbot import FinancialChatbot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="THANOS AI Stock Agent API",
    description="API for AI-powered stock analysis, news aggregation, and product research",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot instance (singleton)
chatbot = None

def get_chatbot():
    """Lazy initialization of chatbot"""
    global chatbot
    if chatbot is None:
        logger.info("Initializing FinancialChatbot...")
        chatbot = FinancialChatbot()
    return chatbot

# ==================== PYDANTIC MODELS ====================
class QueryRequest(BaseModel):
    query: str = Field(..., description="User query/question", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation tracking")

class QueryResponse(BaseModel):
    response: str = Field(..., description="AI agent's response")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    intent: Optional[Dict[str, Any]] = Field(None, description="Detected intent analysis")
    agents_used: Optional[list] = Field(None, description="List of agents used for this query")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    message: str = Field(..., description="Health check message")
    version: str = Field(..., description="API version")

# ==================== API ENDPOINTS ====================
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information"""
    return {
        "status": "healthy",
        "message": "THANOS AI Stock Agent API is running",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test chatbot initialization
        get_chatbot()
        return {
            "status": "healthy",
            "message": "API and chatbot are operational",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main endpoint to process user queries.
    
    This endpoint handles all types of queries:
    - Stock prices and market data
    - Financial news
    - General news
    - Product research
    """
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Get chatbot instance
        bot = get_chatbot()
        
        # Process the query
        response = bot.process_query(request.query)
        
        # Get intent analysis for additional context
        intent_analysis = None
        agents_used = []
        try:
            intent_analysis = bot.orchestrator.analyze_intent(request.query)
            # Determine which agents were used based on intent
            if intent_analysis.get('needs_stock'):
                agents_used.append("StockAgent")
            if intent_analysis.get('needs_news'):
                agents_used.append("NewsAgent")
            if intent_analysis.get('needs_research'):
                agents_used.append("ResearchAgent")
            if intent_analysis.get('needs_web_search'):
                agents_used.append("WebSearchAgent")
        except Exception as e:
            logger.warning(f"Could not get intent analysis: {e}")
            agents_used = ["All Agents"]
        
        return QueryResponse(
            response=response,
            session_id=request.session_id,
            intent=intent_analysis,
            agents_used=agents_used if agents_used else ["All Agents"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/api/intent")
async def analyze_intent(query: str):
    """
    Endpoint to analyze user intent without processing the full query.
    Useful for frontend to determine what type of response to expect.
    """
    try:
        bot = get_chatbot()
        intent_analysis = bot.orchestrator.analyze_intent(query)
        return {
            "query": query,
            "intent_analysis": intent_analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing intent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing intent: {str(e)}"
        )

@app.get("/api/agents")
async def list_agents():
    """
    Endpoint to list available agents and their capabilities.
    """
    return {
        "agents": [
            {
                "name": "WebSearchAgent",
                "description": "Performs web searches using DuckDuckGo",
                "capabilities": ["Web search", "Real-time information retrieval"]
            },
            {
                "name": "StockAgent",
                "description": "Fetches real-time stock data from Alpha Vantage API",
                "capabilities": ["Stock prices", "Market data", "Price history"]
            },
            {
                "name": "NewsAgent",
                "description": "Aggregates news from web search results",
                "capabilities": ["Financial news", "General news", "Market updates"]
            },
            {
                "name": "ResearchAgent",
                "description": "Scrapes product prices using ZenRows API",
                "capabilities": ["Product price research", "E-commerce scraping"]
            }
        ],
        "orchestrator": {
            "name": "MasterOrchestrator",
            "description": "Coordinates all agents based on user intent analysis"
        }
    }

# ==================== STARTUP/SHUTDOWN EVENTS ====================
@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on startup"""
    logger.info("🚀 Starting THANOS AI Stock Agent API...")
    try:
        get_chatbot()
        logger.info("✅ Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down API...")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

