from collections import defaultdict,deque

import asyncio
import threading
import numpy as np

from ..utils.stream_reader import live_video_reader
from ..services.embedding import EmbeddingService
from ..core.session_maker import get_all_live_streams
from ..utils.logger import logging
WINDOW_SIZE = 12
SCORE_THRESHOLD = 0.6
WINDOW_THRESHOLD = 0.7
MIN_SEQUENTIAL_MATCH = 2

def check_uploaded_video(path,embedding_service:EmbeddingService,match_queue:asyncio.Queue):
    session_windows = defaultdict(dict)
    frames = live_video_reader(path,5)
    for frame in frames:
        embedding = embedding_service.embed_frame(frame)
        for session_id, live_memory in get_all_live_streams():
            change_in_index = int(len(live_memory.embeddings) != live_memory.embeddings.maxlen)
            state = session_windows.get(session_id,None)
            if not state:
                scores, indices = live_memory.search(embedding,1)
                best_score = scores[0]
                best_index = indices[0]
                logging.debug(f"1st frame of video matched with stream frame {best_index} with score {best_score}; change in index = {change_in_index}")
                if best_score > SCORE_THRESHOLD:
                    session_windows[session_id] = {
                        "stream_id":session_id,
                        "video_path":path,
                        "count":1,
                        "confidence":best_score,
                        "last_match":best_index
                    }
            else:
                next_index = state["last_match"] + change_in_index
                if next_index >= len(live_memory.embeddings):
                    session_windows.pop(session_id)
                    continue
                live_embd = live_memory.embeddings[next_index]
                similarity_score:np.ndarray = cosine_similarity(embedding,live_embd)
                similarity_score = similarity_score.item()
                logging.debug(f"next frame of video matched with stream frame {next_index} with score {similarity_score}; change in index = {change_in_index}")
                if similarity_score>SCORE_THRESHOLD:
                    state["last_match"] = next_index
                    state["confidence"] += similarity_score
                    state["count"] += 1
                else:
                    session_windows.pop(session_id)
                    logging.debug(f"Similarity broke due to poor similarity {similarity_score}")
                    continue
                if state["count"] >= MIN_SEQUENTIAL_MATCH:
                    avg_score = state["confidence"] / state["count"]
                    data = {
                        "stream_id":session_id,
                        "video_path":path,
                        "score":round(avg_score.item(),3),
                        "matched_frames": state["count"],
                    }
                    logging.debug(f"sending data d{data}")
                    match_queue.put_nowait(data)



def cosine_similarity(a:np.ndarray,b:np.ndarray):
    return (np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b)))

