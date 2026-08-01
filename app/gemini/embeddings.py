"""Vector embeddings and semantic search for Gemini responses"""

import logging
from typing import List, Dict, Any, Optional

try:
    from weaviate import Client
    from weaviate.util import generate_uuid5
except ImportError:
    Client = None
    generate_uuid5 = None

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """Vector database for semantic search and embeddings"""

    def __init__(self):
        """Initialize embedding store"""
        if not Client:
            logger.warning("Weaviate client not available")
            self.client = None
            return

        try:
            self.client = Client(settings.weaviate_url)
            logger.info(f"Connected to Weaviate at {settings.weaviate_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {str(e)}")
            self.client = None

    async def store_response(
        self,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store response with embeddings"""
        if not self.client:
            logger.warning("Weaviate client not available")
            return None

        try:
            properties = {
                "prompt": prompt,
                "response": response,
                "model": settings.gemini_model,
            }

            if metadata:
                properties.update(metadata)

            class_name = "GeminiResponse"
            uuid = generate_uuid5(prompt) if generate_uuid5 else None

            self.client.data_object.create(
                data_object=properties,
                class_name=class_name,
                uuid=uuid,
            )

            logger.info(f"Stored response in Weaviate with UUID: {uuid}")
            return uuid
        except Exception as e:
            logger.error(f"Failed to store response: {str(e)}")
            return None

    async def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Semantic search for similar responses"""
        if not self.client:
            logger.warning("Weaviate client not available")
            return []

        try:
            result = self.client.query.get(
                "GeminiResponse",
                ["prompt", "response", "model", "_additional {distance}"],
            ).with_near_text(
                {"concepts": [query]}
            ).with_limit(limit).do()

            objects = result.get("data", {}).get("Get", {}).get("GeminiResponse", [])
            logger.info(f"Found {len(objects)} similar responses")
            return objects
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []

    async def batch_store(
        self,
        items: List[Dict[str, Any]],
    ) -> int:
        """Batch store multiple responses"""
        if not self.client:
            return 0

        try:
            count = 0
            for item in items:
                prompt = item.get("prompt")
                response = item.get("response")
                metadata = item.get("metadata", {})

                if prompt and response:
                    uuid = await self.store_response(prompt, response, metadata)
                    if uuid:
                        count += 1

            logger.info(f"Batch stored {count} responses")
            return count
        except Exception as e:
            logger.error(f"Batch store error: {str(e)}")
            return 0

    async def delete_response(self, uuid: str) -> bool:
        """Delete response from vector database"""
        if not self.client:
            return False

        try:
            self.client.data_object.delete(
                uuid=uuid,
                class_name="GeminiResponse",
            )
            logger.info(f"Deleted response: {uuid}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete response: {str(e)}")
            return False


# Global embedding store instance
embedding_store = EmbeddingStore()
