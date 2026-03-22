import os
from sqlalchemy.orm import Session
from fastapi import FastAPI,UploadFile,Depends,File
from fastapi.exceptions import HTTPException

from src.db.models import Video
from src.services.embedding import EmbeddingService
from src.services.ingestion import sync_imagekit_files,run_ingestion
from src.db.chromadb_client import VectorDB
from src.db.deps import get_db
from src.services.imagekit_instance import list_all_files
from src.services.query import query_video
from src.db.database import Base,engine
from src.utils.file_handeling import save_temp,cleanup
from src.utils.logger import logging
embedding_service = EmbeddingService()
vector_db = VectorDB()
app = FastAPI()
Base.metadata.create_all(bind = engine)

@app.post("/query")
async def load_from_imagekit(threshold_count:int,threshold_score:float,file:UploadFile=File(...),db = Depends(get_db)):
    if not file.filename.endswith((".mp4", ".mov", ".avi")):
        raise HTTPException(status_code=400, detail="Invalid video format")
    path = None
    try:
        path = await save_temp(file.file)
        logging.debug("File loaded to local")
        results = query_video(path,embedding_service,vector_db,db=db,threshold_count=threshold_count,threshold_score=threshold_score)
        logging.debug("Result found")
        return {
            "status": "success",
            "matches": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if path:
            cleanup(path)

    

@app.post("/sync-imagekit")
def sync_imagekit(db = Depends(get_db)):
    all_files = list_all_files()
    newly_synced = sync_imagekit_files(db,all_files) 
    return {
        "total_recieved":len(all_files),
        "new_added": len(newly_synced),
    }  

@app.post("/run-ingestion")
def run_synced_ingestion(db = Depends(get_db)):
    run_ingestion(db,embedding_service,vector_db)
    return {
        "status": "ingestion complete",
    }

@app.post("/sync-ingest")
def sync_ingest(db = Depends(get_db)):
    all_files = list_all_files()
    newly_synced = sync_imagekit_files(db,all_files)
    run_ingestion(db,embedding_service,vector_db)
    return {
        "total_recieved":len(all_files),
        "new_added": len(newly_synced),
        "status": "ingestion complete",
    }  
@app.post("/cleanup")
def cleanup_dbs(db:Session=Depends(get_db)):
    vector_db.clear_collection()
    db.query(Video).delete(synchronize_session=False)
    db.commit()
    return {"status":"cleaned up"}