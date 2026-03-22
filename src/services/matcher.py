from collections import defaultdict
from sqlalchemy.orm import Session
from ..db.models import Video
from ..db.chromadb_client import VectorDB
from ..utils.logger import logging

def search_frames(embeddings, vector_db: VectorDB):
    all_results = []

    for embd in embeddings:
        if len(embd.shape) != 1:  # Ensure embeddings are 1D vectors
            logging.error(f"Invalid embedding shape: {embd.shape}")
            continue
        logging.debug(f"Embedding: {embd}")
        result = vector_db.search(embd)
        logging.debug(f"Vector search result: {result}")
        all_results.append(result)
    return all_results


def aggregate_results(all_results,db:Session):
    scores = defaultdict(list)
    final = []

    for result in all_results:
        logging.debug(f"Search Result to aggrigate: {result}")
        for idx,metas in enumerate(result['metadatas'][0]):
            vid = metas["video_id"]
            sim = 1 - result["distances"][0][idx]
            scores[vid].append(sim)
    logging.debug(f"scores inserted according to vid")
    for vid,sims in scores.items():
        count = len(sims)
        logging.debug(f"Going to query for url in aggrigator with vid = {vid}")
        url = db.query(Video).filter(Video.id==vid).one().url
        logging.debug(f"Found url in aggrigator {url}")
        average_score = sum(sims) / count
        final.append({
            "video_id":vid,
            "url":url,
            "average_score":average_score,
            "count":count
        })
    logging.debug(f"Result is ready in aggrigator {final}")
    final = sorted(final,key=lambda x:x["average_score"],reverse=True)
    logging.debug(f"Sorted : {final}")
    return final

def filter_results(results,threshold_score=0.8,threshold_count=5):
    return [
        r for r in results if r["average_score"] > threshold_score and r["count"] > threshold_count
    ]


