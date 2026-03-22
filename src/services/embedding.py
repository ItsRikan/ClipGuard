from transformers import CLIPProcessor, CLIPModel
import torch
import numpy
from PIL import Image
from ..utils.logger import logging

class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        #self.model.to(self.device)
        self.model.eval()

    def embed_frame(self, frame):
        image = Image.fromarray(frame)
        inputs = self.processor(images=image, return_tensors="pt") #.to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)

        vector = outputs[1].squeeze().cpu().numpy()
        vector = vector / numpy.linalg.norm(vector)
        return vector

    def embed_frames(self, frames):
        embedded_vectors = []

        for frame in frames:
            vector = self.embed_frame(frame)
            embedded_vectors.append(vector)
        return embedded_vectors

