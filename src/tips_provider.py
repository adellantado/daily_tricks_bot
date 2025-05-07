import openai
import os
from dotenv import load_dotenv
import logging
import numpy as np
import faiss
import asyncio

from langchain_openai import OpenAIEmbeddings
# from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TipsProvider:

    def __init__(self, 
            index_path: str, 
            model: str, 
            model_messages: list, 
            similarity_threshold: float = 0.95, 
            max_generation_attempts: int = 5, 
            dimension: int = 1536
        ):
        
        self.index_path = index_path
        self.model = model
        self.model_messages = model_messages
        self.similarity_threshold = similarity_threshold
        self.max_generation_attempts = max_generation_attempts
        self.dimension = dimension

        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            logger.critical("OpenAI API key not found!")
            raise ValueError("OpenAI API key not found in environment variables.")
        try:
            self.embedding_model = OpenAIEmbeddings()
            test_emb = self.embedding_model.embed_query("test")
            actual_dimension = len(test_emb)
            if actual_dimension != dimension:
                logger.warning(f"Provided dimension {dimension} does not match OpenAI model dimension {actual_dimension}. Using {actual_dimension}.")
                dimension = actual_dimension
            self.dimension = dimension
        except Exception as e:
            logger.critical(f"Failed to initialize OpenAIEmbeddings: {e}")
            raise

        self.faiss_index = self._load_faiss_index(self.index_path, self.dimension)
        logger.info(f"TipsProvider initialized. FAISS index size: {self.faiss_index.ntotal}")

    def _load_faiss_index(self, path, dimension):
        try:
            if os.path.exists(path):
                logger.info(f"Loading FAISS index from {path}")
                index = faiss.read_index(path)
                if index.d != dimension:
                     logger.warning(f"Index dimension mismatch ({index.d} != {dimension}) in {path}. Creating new index.")
                     index = faiss.IndexFlatIP(dimension)
                else:
                     if not isinstance(index, faiss.IndexFlatIP):
                         logger.warning(f"Loaded index is not IndexFlatIP. Recreating.")
                         index = faiss.IndexFlatIP(dimension)

                logger.info(f"FAISS index loaded with {index.ntotal} vectors.")
                return index
            else:
                logger.info(f"FAISS index file not found at {path}. Creating new IndexFlatIP.")
                return faiss.IndexFlatIP(dimension)
        except Exception as e:
            logger.error(f"Error loading FAISS index from {path}: {e}. Creating new index.")
            return faiss.IndexFlatIP(dimension)

    def _save_faiss_index(self):
        if self.faiss_index is None:
            logger.warning("Attempted to save a None index.")
            return
        try:
            logger.info(f"Saving FAISS index to {self.index_path} with {self.faiss_index.ntotal} vectors...")
            faiss.write_index(self.faiss_index, self.index_path)
            logger.info("FAISS index saved successfully.")
        except Exception as e:
            logger.error(f"Error saving FAISS index to {self.index_path}: {e}")

    def get_embedding(self, text):
        try:
            embedding = self.embedding_model.embed_query(text)
            embedding_np = np.array(embedding).astype('float32')
            faiss.normalize_L2(embedding_np.reshape(1, -1))
            return embedding_np
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def is_tip_similar(self, new_tip_embedding, threshold):
        """Checks similarity using FAISS index search."""
        if self.faiss_index.ntotal == 0:
            return False

        if new_tip_embedding is None or new_tip_embedding.ndim != 1:
             logger.warning("Invalid embedding provided for similarity check.")
             return False

        try:
            distances, indices = self.faiss_index.search(new_tip_embedding.reshape(1, -1), 1)

            similarity_score = distances[0][0]
            logger.debug(f"Highest similarity score found: {similarity_score:.4f}")

            if similarity_score >= threshold:
                logger.info(f"Similarity score {similarity_score:.4f} >= threshold {threshold}. Tip is too similar.")
                return True
            return False
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return False

    async def get_new_tip_content(self):
        try:
            logger.info(f"Requesting tip from OpenAI...")
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model=self.model,
                messages=self.model_messages,
            )
            tip_content = response.choices[0].message.content.strip()
            logger.info(f"Received tip content from OpenAI (length: {len(tip_content)}).")
            return tip_content
        except Exception as e:
            logger.error(f"Error generating tip content: {e}")
            return None

    async def get_unique_tip(self):
        for attempt in range(self.max_generation_attempts):
            logger.info(f"Attempt {attempt + 1}/{self.max_generation_attempts} to generate a unique tip...")
            new_tip_content = await self.get_new_tip_content()

            if not new_tip_content:
                logger.warning("Failed to generate tip content. Retrying after delay...")
                await asyncio.sleep(2)
                continue

            new_tip_embedding = self.get_embedding(new_tip_content)

            if new_tip_embedding is None:
                 logger.warning("Failed to generate embedding for the tip. Skipping similarity check for this one.")
                 return new_tip_content

            if not self.is_tip_similar(new_tip_embedding, self.similarity_threshold):
                logger.info("Generated tip is unique.")
                try:
                    if self.faiss_index is not None:
                        new_index = self.faiss_index.ntotal
                        self.faiss_index.add(new_tip_embedding.reshape(1, -1))
                        logger.info(f"Added unique tip embedding to FAISS. Index size now {new_index+1}")
                        self._save_faiss_index()
                    else:
                        logger.error("FAISS index is None, cannot add embedding.")

                except Exception as e:
                     logger.error(f"Error adding embedding to FAISS index: {e}")

                return new_tip_content
            else:
                logger.warning("Duplicate tip detected based on embedding similarity, fetching a new one...")
                await asyncio.sleep(1)

        logger.error(f"Failed to find a unique tip after {self.max_generation_attempts} attempts.")
        return new_tip_content