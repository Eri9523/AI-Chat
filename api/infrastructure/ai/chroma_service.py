import requests
import uuid
from typing import List, Dict, Any, Optional
from domain.services.vector_service import IVectorService
from domain.services.ai_service import IAIService
from infrastructure.config.environment import config


class ChromaService(IVectorService):
    def __init__(self, ai_service: IAIService):
        self.ai_service = ai_service
        self.base_url = f"http://{config['chroma']['host']}:{config['chroma']['port']}/api/v1"
        self.collection_name = config["chroma"]["collection_name"]
        self._ensure_collection()

    def _ensure_collection(self):
        """Crear colección si no existe"""
        try:
            response = requests.get(f"{self.base_url}/collections/{self.collection_name}")
            if response.status_code == 404:
                payload = {
                    "name": self.collection_name,
                    "metadata": {"hnsw:space": "cosine"}
                }
                requests.post(f"{self.base_url}/collections", json=payload)
        except Exception as e:
            print(f"Error ensuring collection: {e}")

    async def store_documents(
            self, 
            documents: List[str], 
            metadatas: List[Dict[str, Any]], 
            ids: Optional[List[str]] = None
            ) -> List[str]:
        
        # Generate embeddings
        embeddings = await self.ai_service.generate_embeddings(documents)

        # Generate ids if not given
        if not ids:
            ids = [str(uuid.uuid4()) for _ in documents]

        payload = {
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings,
            "ids": ids
        }

        requests.post(
            f"{self.base_url}/collections/{self.collection_name}/add",
            json=payload
        )

        return ids
    
    async def search_similar(
            self,
            query: str,
            n_results: int = 5,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        
        query_embeddings = await self.ai_service.generate_embeddings([query])

        where_clause = None
        if filters:
            where_clause = {}
            for key, value in filters.items():
                where_clause[key] = {"$eq": value}

        payload = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }

        if where_clause:
            payload["where"] = where_clause

        response = requests.post(
            f"{self.base_url}/collections/{self.collection_name}/query",
            json=payload
        )

        if response.status_code != 200:
            return []

        results = response.json()

        # Format results
        formatted_results = []
        if results.get("documents") and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i]
                })

        return formatted_results
    
    async def delete_documents(self, ids: List[str]) -> bool:
        try:
            payload = {"ids": ids}
            response = requests.post(
                f"{self.base_url}/collections/{self.collection_name}/delete",
                json=payload
            )
            return response.status_code == 200
        except Exception:
            return False
        
    async def get_collection_info(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/collections/{self.collection_name}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "count": data.get("count", 0),
                    "metadata": data.get("metadata", {})
                }
        except Exception:
            pass
        return {"name": self.collection_name, "count": 0, "metadata": {}}
    
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Método alias para compatibilidad"""
        return await self.delete_documents(vector_ids)
        
