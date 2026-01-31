"""
FastAPI Backend Server for NEXUS
Provides REST API and WebSocket support for the frontend
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import json
import asyncio
from pathlib import Path

from backend.nexus_core import NexusCore
from backend.tools import get_system_metrics, get_system_info
from backend.chat_manager import chat_manager
from backend.file_handler import FileHandler
from backend.pdf_generator import PDFGenerator


app = FastAPI(
    title="NEXUS API",
    description="Next-generation Super AI Agent API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NEXUS Core
nexus = NexusCore()

# Initialize Chat Manager on startup
@app.on_event("startup")
async def startup_event():
    await chat_manager.initialize()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    stream: bool = True


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    model: str
    task_type: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "NEXUS",
        "version": "1.0.0",
        "status": "online",
        "message": "Next-generation Super AI Agent"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = await nexus.check_ollama_status()
    return {
        "status": "healthy",
        "ollama": ollama_status,
        "nexus": "operational"
    }


@app.get("/models")
async def get_models():
    """Get available models and their status"""
    ollama_status = await nexus.check_ollama_status()
    models_info = nexus.router.get_all_models()
    
    return {
        "models": models_info,
        "status": ollama_status
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "system": get_system_metrics(),
        "nexus": nexus.get_stats()
    }


@app.get("/system")
async def get_system():
    """Get system information"""
    return get_system_info()


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with streaming support
    
    If stream=True, returns SSE stream
    If stream=False, returns complete response
    """
    if request.stream:
        async def event_stream():
            """Server-sent events stream"""
            async for chunk in nexus.generate_response(request.message, stream=True):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream"
        )
    else:
        # Non-streaming response
        full_response = ""
        model_used = None
        task_type = None
        
        async for chunk in nexus.generate_response(request.message, stream=True):
            if chunk['type'] == 'model_selected':
                model_used = chunk['model']
                task_type = chunk['task_type']
            elif chunk['type'] == 'content':
                full_response += chunk['content']
        
        return ChatResponse(
            response=full_response,
            model=model_used,
            task_type=task_type
        )


@app.post("/reset")
async def reset_conversation():
    """Reset conversation history"""
    nexus.reset_conversation()
    return {"status": "reset", "message": "Conversation history cleared"}


# ========== FILE UPLOAD ENDPOINTS ==========

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file"""
    if not FileHandler.is_supported(file.filename):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Unsupported file type"}
        )
    
    content = await file.read()
    result = await FileHandler.process_file(file.filename, content)
    return result


# ========== CHAT HISTORY ENDPOINTS ==========

@app.get("/history")
async def get_history(limit: int = 50):
    """Get all conversations"""
    conversations = await chat_manager.get_conversations(limit)
    return {"conversations": conversations}


@app.get("/history/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get a specific conversation"""
    conversation = await chat_manager.get_conversation(conversation_id)
    if not conversation:
        return JSONResponse(status_code=404, content={"error": "Conversation not found"})
    return conversation


@app.post("/history/create")
async def create_conversation(title: str = Form(...), model: str = Form(None)):
    """Create a new conversation"""
    conversation_id = await chat_manager.create_conversation(title, model)
    return {"id": conversation_id, "title": title}


@app.post("/history/{conversation_id}/message")
async def add_message_to_history(
    conversation_id: int,
    role: str = Form(...),
    content: str = Form(...),
    model: str = Form(None)
):
    """Add a message to conversation history"""
    await chat_manager.add_message(conversation_id, role, content, model)
    return {"status": "success"}


@app.delete("/history/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """Delete a conversation"""
    await chat_manager.delete_conversation(conversation_id)
    return {"status": "deleted"}


@app.delete("/history")
async def clear_all_history():
    """Clear all chat history"""
    await chat_manager.clear_all_history()
    return {"status": "cleared"}


@app.get("/history/search/{query}")
async def search_history(query: str, limit: int = 20):
    """Search across all conversations"""
    results = await chat_manager.search_conversations(query, limit)
    return {"results": results}


# ========== PDF EXPORT ENDPOINT ==========

@app.get("/export/pdf/{conversation_id}")
async def export_conversation_pdf(conversation_id: int):
    """Export conversation to PDF"""
    conversation = await chat_manager.get_conversation(conversation_id)
    if not conversation:
        return JSONResponse(status_code=404, content={"error": "Conversation not found"})
    
    pdf_buffer = PDFGenerator.generate_chat_pdf(conversation)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="nexus_chat_{conversation_id}.pdf"'
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            query = message_data.get('message', '')
            
            if not query:
                continue
            
            # Stream response
            async for chunk in nexus.generate_response(query, stream=True):
                await websocket.send_text(json.dumps(chunk))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


# Mount static files (frontend)
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗            ║
    ║   ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝            ║
    ║   ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗            ║
    ║   ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║            ║
    ║   ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║            ║
    ║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝            ║
    ║                                                           ║
    ║         Next-generation Super AI Agent                    ║
    ║              Powered by Ollama                            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 NEXUS is starting...
    📡 API Server: http://localhost:8080
    🌐 Web UI: http://localhost:8080/app
    📊 Health Check: http://localhost:8080/health
    📚 API Docs: http://localhost:8080/docs
    
    """)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
