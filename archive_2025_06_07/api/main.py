# Save this file in the api/ directory as: main.py

"""
FastAPI backend for Hedge Intelligence
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from embeddings.vector_store import VectorStoreManager
from chat.rag_chain import FinancialRAGChain
from ipo_dashboard.ipo_data_manager import IPODataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hedge Intelligence API",
    description="API for financial document analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
vector_manager = VectorStoreManager()
rag_chain = FinancialRAGChain()
ipo_manager = IPODataManager()


# Pydantic models
class ChatRequest(BaseModel):
    ticker: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict]


@app.get("/")
async def root():
    return {"message": "Hedge Intelligence API", "version": "1.0.0"}


@app.get("/api/tickers")
async def list_tickers():
    """List all available tickers"""
    tickers = vector_manager.list_tickers()
    return {"tickers": tickers}


@app.post("/api/chat/{ticker}")
async def chat_with_ticker(ticker: str, request: ChatRequest):
    """Chat with a specific ticker's documents"""
    vectorstore = vector_manager.get_ticker_store(ticker.upper())
    
    if not vectorstore:
        raise HTTPException(status_code=404, detail=f"No documents found for ticker {ticker}")
    
    try:
        response = rag_chain.answer_question(vectorstore, request.question)
        return ChatResponse(
            answer=response['answer'],
            sources=response.get('source_documents', [])
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ipos")
async def get_ipos():
    """Get IPO calendar"""
    ipos = ipo_manager.get_ipo_data()
    return {"ipos": ipos}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)