"""
FastAPI endpoint for the chat functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.ai_chat import AIChat
from services.document_indexer import DocumentIndexer
import logging
from datetime import datetime
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Hedge Fund Intelligence API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_chat = AIChat()
doc_indexer = DocumentIndexer()

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hedge Fund Intelligence API", "status": "running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests"""
    try:
        user_message = request.message
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        logger.info(f"Received message: {user_message[:100]}...")
        
        # Search for relevant documents
        search_results = doc_indexer.search(user_message, limit=5)
        
        # Prepare context from search results
        context = ""
        sources = []
        
        if search_results:
            logger.info(f"Found {len(search_results)} relevant documents")
            for result in search_results:
                context += f"\n\nFrom {result['company']} {result['document']}:\n{result['text']}"
                sources.append({
                    'company': result['company'],
                    'document': result['document'],
                    'score': result.get('score', 0)
                })
        
        # Get AI response
        ai_response = ai_chat.get_response(user_message, context)
        
        return {
            'response': ai_response,
            'sources': sources,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(request: SearchRequest):
    """Direct document search"""
    try:
        results = doc_indexer.search(request.query, limit=request.limit)
        
        return {
            'results': results,
            'count': len(results),
            'query': request.query
        }
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        doc_count = doc_indexer.collection.count()
        return {
            'status': 'healthy',
            'documents_indexed': doc_count,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    print("=" * 70)
    print("Hedge Fund Intelligence API - FastAPI Server")
    print("=" * 70)
    print(f"Documents indexed: {doc_indexer.collection.count()}")
    print(f"Starting server at http://localhost:5002")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=5002)
