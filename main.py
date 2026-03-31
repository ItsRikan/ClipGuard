from fastapi import FastAPI,UploadFile,Depends,File, WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading

from src.utils.logger import logging
from src.core.session_maker import create_session,delete_session,get_active_sessions,stop_session
from src.workers.stream_worker import start_stream_worker
from src.services.context_manager import ContextManager
from src.core.live_memory import LiveMemoryIndex
from src.workers.upload_worker import check_uploaded_video
from src.watcher.folder_watcher import start_watcher
from api.model import StartStreamRequestSchema



app = FastAPI()
context=ContextManager()
match_queue = asyncio.Queue()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Stream Manager

@app.post("/start_stream")
async def start_stream(request:StartStreamRequestSchema):
    session = create_session()
    live_memory = LiveMemoryIndex()
    session["live_memory"] = live_memory
    session["url"] = request.url
    worker = threading.Thread(
        target=start_stream_worker,
        args=(request.url,request.interval,context,live_memory)
    )
    worker.start()
    session["thread"] = worker
    return {
        "status":"successful",
        "session_id":session["id"]
    }

@app.post("/stop-stream/{session_id}")
def stop_stream(session_id:str):
    session = stop_session(session_id=session_id)
    return {
        "status":"successful",
        "session_id":session_id if session else None
        }

@app.websocket("/ws/{session_id}")
async def ws_route(ws:WebSocket,session_id:str):
    await context.manager.connect(session_id,ws)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        context.manager.active.pop(session_id,None)

@app.on_event("startup")
async def event_dispatcher():
    watcher = threading.Thread(
        target=start_watcher,
        args=(context.embedding_service,match_queue)
    )
    watcher.start()
    asyncio.create_task(dispatch_events())  
    

async def dispatch_events():
    while True:
        if not match_queue.empty():
            event = await match_queue.get()
            await context.manager.send(event["stream_id"],event)
        await asyncio.sleep(0.1)
    

#temp
@app.get("/show-sessions")
def show():
    return get_active_sessions()