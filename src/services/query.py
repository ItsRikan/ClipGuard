from sqlalchemy.orm import Session

from ..utils.videos import extract_frames
from ..utils.logger import logging
from .embedding import EmbeddingService
from ..db.chromadb_client import VectorDB
from .matcher import search_frames, aggregate_results, filter_results

def query_video(video_path, embedding_service: EmbeddingService, vector_db: VectorDB, db: Session, threshold_score=0.8, threshold_count=5):
    logging.debug("Querying for video")
    frames = extract_frames(video_path)  # No resizing, use original dimensions
    embeddings = embedding_service.embed_frames(frames)
    logging.debug(f"Embedding extracted: {len(embeddings)} : {embeddings[0].shape}")
    search_result = search_frames(embeddings, vector_db)
    logging.debug("Found searched results")
    aggregated = aggregate_results(search_result, db)
    logging.debug(f"Results aggregated : {aggregated}")
    filtered = filter_results(aggregated, threshold_score, threshold_count)
    logging.debug(f"Result filtered out : {filtered}")
    return filtered
