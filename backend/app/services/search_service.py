"""Search service for ElasticSearch operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class SearchService:
    """Service for search operations using ElasticSearch."""
    
    INDEX_NAME = "news"
    
    def __init__(self):
        """Initialize ElasticSearch connection."""
        self.es_client: Optional[AsyncElasticsearch] = None
    
    async def connect(self):
        """Connect to ElasticSearch."""
        try:
            self.es_client = AsyncElasticsearch(
                [settings.ELASTICSEARCH_URL],
                verify_certs=False
            )
            
            # Create index if not exists
            await self.create_index()
            
            logger.info("Connected to ElasticSearch")
        except Exception as e:
            logger.error(f"Failed to connect to ElasticSearch: {e}")
            self.es_client = None
    
    async def disconnect(self):
        """Disconnect from ElasticSearch."""
        if self.es_client:
            await self.es_client.close()
            logger.info("Disconnected from ElasticSearch")
    
    async def create_index(self):
        """Create news index with mappings."""
        if not self.es_client:
            return
        
        try:
            exists = await self.es_client.indices.exists(index=self.INDEX_NAME)
            
            if not exists:
                mapping = {
                    "mappings": {
                        "properties": {
                            "title": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "content": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "summary": {
                                "type": "text"
                            },
                            "url": {
                                "type": "keyword"
                            },
                            "category_id": {
                                "type": "integer"
                            },
                            "source_id": {
                                "type": "integer"
                            },
                            "sentiment": {
                                "type": "keyword"
                            },
                            "published_at": {
                                "type": "date"
                            },
                            "tags": {
                                "type": "keyword"
                            }
                        }
                    }
                }
                
                await self.es_client.indices.create(
                    index=self.INDEX_NAME,
                    body=mapping
                )
                logger.info(f"Created index: {self.INDEX_NAME}")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
    
    async def index_news(self, news_id: int, news_data: Dict[str, Any]) -> bool:
        """Index news article.
        
        Args:
            news_id: News ID
            news_data: News data to index
            
        Returns:
            True if successful, False otherwise
        """
        if not self.es_client:
            return False
        
        try:
            await self.es_client.index(
                index=self.INDEX_NAME,
                id=news_id,
                document=news_data
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing news {news_id}: {e}")
            return False
    
    async def delete_news(self, news_id: int) -> bool:
        """Delete news from index.
        
        Args:
            news_id: News ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.es_client:
            return False
        
        try:
            await self.es_client.delete(
                index=self.INDEX_NAME,
                id=news_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting news {news_id}: {e}")
            return False
    
    async def search(
        self,
        query: str,
        category_id: Optional[int] = None,
        source_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        size: int = 20,
        from_: int = 0
    ) -> Dict[str, Any]:
        """Search news articles.
        
        Args:
            query: Search query
            category_id: Filter by category
            source_id: Filter by source
            date_from: Filter from date
            date_to: Filter to date
            size: Number of results
            from_: Offset
            
        Returns:
            Search results
        """
        if not self.es_client:
            return {"hits": {"total": {"value": 0}, "hits": []}}
        
        try:
            # Build query
            must = []
            
            # Text search
            if query:
                must.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "content", "summary"],
                        "fuzziness": "AUTO"
                    }
                })
            
            # Filters
            filters = []
            
            if category_id:
                filters.append({"term": {"category_id": category_id}})
            
            if source_id:
                filters.append({"term": {"source_id": source_id}})
            
            if date_from or date_to:
                date_range = {}
                if date_from:
                    date_range["gte"] = date_from.isoformat()
                if date_to:
                    date_range["lte"] = date_to.isoformat()
                
                filters.append({"range": {"published_at": date_range}})
            
            # Build full query
            search_body = {
                "query": {
                    "bool": {
                        "must": must if must else [{"match_all": {}}],
                        "filter": filters
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                },
                "size": size,
                "from": from_
            }
            
            # Execute search
            response = await self.es_client.search(
                index=self.INDEX_NAME,
                body=search_body
            )
            
            return response
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {"hits": {"total": {"value": 0}, "hits": []}}
    
    async def suggest(self, prefix: str, size: int = 5) -> List[str]:
        """Get search suggestions.
        
        Args:
            prefix: Search prefix
            size: Number of suggestions
            
        Returns:
            List of suggestions
        """
        if not self.es_client:
            return []
        
        try:
            response = await self.es_client.search(
                index=self.INDEX_NAME,
                body={
                    "suggest": {
                        "title_suggest": {
                            "prefix": prefix,
                            "completion": {
                                "field": "title",
                                "size": size
                            }
                        }
                    }
                }
            )
            
            suggestions = []
            for option in response["suggest"]["title_suggest"][0]["options"]:
                suggestions.append(option["text"])
            
            return suggestions
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []
    
    async def bulk_index(self, news_list: List[Dict[str, Any]]) -> int:
        """Bulk index news articles.
        
        Args:
            news_list: List of news data
            
        Returns:
            Number of indexed documents
        """
        if not self.es_client:
            return 0
        
        try:
            operations = []
            for news in news_list:
                operations.append({"index": {"_index": self.INDEX_NAME, "_id": news["id"]}})
                operations.append(news)
            
            response = await self.es_client.bulk(operations=operations)
            
            if response["errors"]:
                logger.warning("Some documents failed to index")
            
            return len([item for item in response["items"] if item["index"]["status"] == 201])
        except Exception as e:
            logger.error(f"Error bulk indexing: {e}")
            return 0


# Global search service instance
search_service = SearchService()


async def get_search_service() -> SearchService:
    """Get search service instance.
    
    Returns:
        Search service instance
    """
    if not search_service.es_client:
        await search_service.connect()
    return search_service
