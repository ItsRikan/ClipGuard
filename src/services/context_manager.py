from .embedding import EmbeddingService
from .connection_manager import ConnectionManager
class ContextManager:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.manager = ConnectionManager()