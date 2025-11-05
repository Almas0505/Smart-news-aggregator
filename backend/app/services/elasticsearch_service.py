"""
Elasticsearch Service - Full-text search and indexing

Provides:
- Index management (create, delete, update mappings)
- Document indexing (news articles)
- Full-text search with filters
- Aggregations and facets
- Semantic search integration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk

from app.core.config import settings
from app.models.news import News
from app.schemas.search import SearchQuery, SearchResponse, SearchFilters

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for Elasticsearch operations."""
    
    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client = AsyncElasticsearch(
            hosts=[settings.ELASTICSEARCH_URL],
            verify_certs=False,  # В production: True с SSL
            retry_on_timeout=True,
            max_retries=3
        )
        self.index_name = "news"
    
    async def close(self):
        """Close Elasticsearch connection."""
        await self.client.close()
    
    # ===== INDEX MANAGEMENT =====
    
    async def create_index(self, delete_if_exists: bool = False) -> bool:
        """
        Create news index with mappings.
        
        Args:
            delete_if_exists: Delete index if it already exists
            
        Returns:
            True if created successfully
        """
        try:
            # Delete existing index if requested
            if delete_if_exists:
                await self.delete_index()
            
            # Check if index exists
            exists = await self.client.indices.exists(index=self.index_name)
            if exists:
                logger.info(f"Index {self.index_name} already exists")
                return True
            
            # Define mappings
            mappings = {
                "properties": {
                    # Basic fields
                    "id": {"type": "integer"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "english": {"type": "text", "analyzer": "english"}
                        }
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "english",
                        "fields": {
                            "standard": {"type": "text", "analyzer": "standard"}
                        }
                    },
                    "summary": {
                        "type": "text",
                        "analyzer": "english"
                    },
                    "url": {"type": "keyword"},
                    "image_url": {"type": "keyword"},
                    
                    # Relations
                    "source_id": {"type": "integer"},
                    "source_name": {"type": "keyword"},
                    "category_id": {"type": "integer"},
                    "category_name": {"type": "keyword"},
                    
                    # ML fields
                    "sentiment": {"type": "keyword"},
                    "sentiment_score": {"type": "float"},
                    
                    # Tags and entities
                    "tags": {"type": "keyword"},
                    "entities": {
                        "type": "nested",
                        "properties": {
                            "text": {"type": "keyword"},
                            "type": {"type": "keyword"},
                            "confidence": {"type": "float"}
                        }
                    },
                    
                    # Dates
                    "published_at": {"type": "date"},
                    "scraped_at": {"type": "date"},
                    "indexed_at": {"type": "date"},
                    
                    # Stats
                    "views_count": {"type": "integer"},
                    "bookmarks_count": {"type": "integer"},
                    
                    # Embedding for semantic search
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,  # sentence-transformers/all-MiniLM-L6-v2
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
            
            # Settings
            settings_config = {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "english_analyzer": {
                            "type": "english"
                        }
                    }
                }
            }
            
            # Create index
            await self.client.indices.create(
                index=self.index_name,
                mappings=mappings,
                settings=settings_config
            )
            
            logger.info(f"✅ Created index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False
    
    async def delete_index(self) -> bool:
        """Delete news index."""
        try:
            exists = await self.client.indices.exists(index=self.index_name)
            if exists:
                await self.client.indices.delete(index=self.index_name)
                logger.info(f"Deleted index: {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index: {e}")
            return False
    
    async def index_exists(self) -> bool:
        """Check if index exists."""
        try:
            return await self.client.indices.exists(index=self.index_name)
        except Exception as e:
            logger.error(f"Error checking index existence: {e}")
            return False
    
    # ===== DOCUMENT OPERATIONS =====
    
    async def index_news(self, news: News, embedding: Optional[List[float]] = None) -> bool:
        """
        Index a single news article.
        
        Args:
            news: News model instance
            embedding: Optional text embedding vector
            
        Returns:
            True if indexed successfully
        """
        try:
            # Prepare document
            doc = {
                "id": news.id,
                "title": news.title,
                "content": news.content or "",
                "summary": news.summary or "",
                "url": news.url,
                "image_url": news.image_url,
                "source_id": news.source_id,
                "source_name": news.source.name if news.source else None,
                "category_id": news.category_id,
                "category_name": news.category.name if news.category else None,
                "sentiment": news.sentiment,
                "sentiment_score": news.sentiment_score,
                "tags": [tag.name for tag in news.tags] if news.tags else [],
                "entities": [
                    {
                        "text": entity.entity_text,
                        "type": entity.entity_type,
                        "confidence": entity.confidence
                    }
                    for entity in news.entities
                ] if news.entities else [],
                "published_at": news.published_at.isoformat() if news.published_at else None,
                "scraped_at": news.scraped_at.isoformat() if news.scraped_at else None,
                "indexed_at": datetime.utcnow().isoformat(),
                "views_count": news.views_count or 0,
                "bookmarks_count": news.bookmarks_count or 0,
            }
            
            # Add embedding if provided
            if embedding:
                doc["embedding"] = embedding
            
            # Index document
            await self.client.index(
                index=self.index_name,
                id=news.id,
                document=doc
            )
            
            logger.debug(f"Indexed news: {news.id} - {news.title[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index news {news.id}: {e}")
            return False
    
    async def bulk_index_news(
        self,
        news_list: List[News],
        embeddings: Optional[Dict[int, List[float]]] = None
    ) -> tuple[int, int]:
        """
        Bulk index multiple news articles.
        
        Args:
            news_list: List of News models
            embeddings: Optional dict {news_id: embedding}
            
        Returns:
            (success_count, error_count)
        """
        try:
            # Prepare actions
            actions = []
            for news in news_list:
                embedding = embeddings.get(news.id) if embeddings else None
                
                doc = {
                    "_index": self.index_name,
                    "_id": news.id,
                    "_source": {
                        "id": news.id,
                        "title": news.title,
                        "content": news.content or "",
                        "summary": news.summary or "",
                        "url": news.url,
                        "image_url": news.image_url,
                        "source_id": news.source_id,
                        "source_name": news.source.name if news.source else None,
                        "category_id": news.category_id,
                        "category_name": news.category.name if news.category else None,
                        "sentiment": news.sentiment,
                        "sentiment_score": news.sentiment_score,
                        "tags": [tag.name for tag in news.tags] if news.tags else [],
                        "entities": [
                            {
                                "text": entity.entity_text,
                                "type": entity.entity_type,
                                "confidence": entity.confidence
                            }
                            for entity in news.entities
                        ] if news.entities else [],
                        "published_at": news.published_at.isoformat() if news.published_at else None,
                        "scraped_at": news.scraped_at.isoformat() if news.scraped_at else None,
                        "indexed_at": datetime.utcnow().isoformat(),
                        "views_count": news.views_count or 0,
                        "bookmarks_count": news.bookmarks_count or 0,
                    }
                }
                
                if embedding:
                    doc["_source"]["embedding"] = embedding
                
                actions.append(doc)
            
            # Bulk index
            success, errors = await async_bulk(
                self.client,
                actions,
                raise_on_error=False
            )
            
            logger.info(f"Bulk indexed: {success} success, {len(errors)} errors")
            return success, len(errors)
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return 0, len(news_list)
    
    async def delete_news(self, news_id: int) -> bool:
        """Delete news document from index."""
        try:
            await self.client.delete(
                index=self.index_name,
                id=news_id
            )
            logger.debug(f"Deleted news from index: {news_id}")
            return True
        except NotFoundError:
            logger.warning(f"News not found in index: {news_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete news {news_id}: {e}")
            return False
    
    async def update_news(self, news_id: int, updates: Dict[str, Any]) -> bool:
        """Update specific fields of a news document."""
        try:
            await self.client.update(
                index=self.index_name,
                id=news_id,
                doc=updates
            )
            logger.debug(f"Updated news in index: {news_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update news {news_id}: {e}")
            return False
    
    # ===== SEARCH OPERATIONS =====
    
    async def search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "_score"
    ) -> SearchResponse:
        """
        Full-text search with filters.
        
        Args:
            query: Search query string
            filters: Optional filters (category, source, sentiment, dates)
            page: Page number (1-based)
            size: Results per page
            sort_by: Sort field (_score, published_at, views_count)
            
        Returns:
            SearchResponse with results and aggregations
        """
        try:
            # Calculate offset
            from_offset = (page - 1) * size
            
            # Build query
            search_query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "title^3",  # Title is most important
                                    "summary^2",
                                    "content",
                                    "source_name",
                                    "category_name"
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ],
                    "filter": []
                }
            }
            
            # Apply filters
            if filters:
                if filters.category_ids:
                    search_query["bool"]["filter"].append({
                        "terms": {"category_id": filters.category_ids}
                    })
                
                if filters.source_ids:
                    search_query["bool"]["filter"].append({
                        "terms": {"source_id": filters.source_ids}
                    })
                
                if filters.sentiment:
                    search_query["bool"]["filter"].append({
                        "term": {"sentiment": filters.sentiment}
                    })
                
                if filters.date_from or filters.date_to:
                    date_range = {}
                    if filters.date_from:
                        date_range["gte"] = filters.date_from.isoformat()
                    if filters.date_to:
                        date_range["lte"] = filters.date_to.isoformat()
                    
                    search_query["bool"]["filter"].append({
                        "range": {"published_at": date_range}
                    })
                
                if filters.tags:
                    search_query["bool"]["filter"].append({
                        "terms": {"tags": filters.tags}
                    })
            
            # Sort
            sort_options = {
                "_score": [{"_score": {"order": "desc"}}],
                "published_at": [{"published_at": {"order": "desc"}}],
                "views_count": [{"views_count": {"order": "desc"}}],
            }
            sort = sort_options.get(sort_by, sort_options["_score"])
            
            # Aggregations
            aggs = {
                "categories": {
                    "terms": {"field": "category_name", "size": 20}
                },
                "sources": {
                    "terms": {"field": "source_name", "size": 20}
                },
                "sentiments": {
                    "terms": {"field": "sentiment", "size": 3}
                },
                "tags": {
                    "terms": {"field": "tags", "size": 30}
                }
            }
            
            # Execute search
            response = await self.client.search(
                index=self.index_name,
                query=search_query,
                from_=from_offset,
                size=size,
                sort=sort,
                aggs=aggs,
                track_total_hits=True
            )
            
            # Parse results
            hits = response["hits"]
            total = hits["total"]["value"]
            results = [hit["_source"] for hit in hits["hits"]]
            
            # Parse aggregations
            aggregations = {}
            if "aggregations" in response:
                for agg_name, agg_data in response["aggregations"].items():
                    aggregations[agg_name] = [
                        {"key": bucket["key"], "count": bucket["doc_count"]}
                        for bucket in agg_data["buckets"]
                    ]
            
            return SearchResponse(
                results=results,
                total=total,
                page=page,
                size=size,
                query=query,
                aggregations=aggregations
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return SearchResponse(
                results=[],
                total=0,
                page=page,
                size=size,
                query=query,
                aggregations={}
            )
    
    async def semantic_search(
        self,
        embedding: List[float],
        filters: Optional[SearchFilters] = None,
        size: int = 20,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using embeddings.
        
        Args:
            embedding: Query embedding vector
            filters: Optional filters
            size: Number of results
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of results with scores
        """
        try:
            # Build query
            search_query = {
                "bool": {
                    "must": [
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                    "params": {"query_vector": embedding}
                                }
                            }
                        }
                    ],
                    "filter": []
                }
            }
            
            # Apply filters (same as regular search)
            if filters:
                if filters.category_ids:
                    search_query["bool"]["filter"].append({
                        "terms": {"category_id": filters.category_ids}
                    })
                # ... more filters
            
            # Execute search
            response = await self.client.search(
                index=self.index_name,
                query=search_query,
                size=size,
                min_score=min_score
            )
            
            # Parse results
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["_score"] = hit["_score"]
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def suggest(self, text: str, size: int = 5) -> List[str]:
        """
        Get search suggestions/autocomplete.
        
        Args:
            text: Partial search text
            size: Number of suggestions
            
        Returns:
            List of suggested queries
        """
        try:
            response = await self.client.search(
                index=self.index_name,
                suggest={
                    "title_suggest": {
                        "prefix": text,
                        "completion": {
                            "field": "title.keyword",
                            "size": size,
                            "skip_duplicates": True
                        }
                    }
                }
            )
            
            suggestions = []
            for option in response["suggest"]["title_suggest"][0]["options"]:
                suggestions.append(option["text"])
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggest failed: {e}")
            return []
    
    # ===== UTILITY METHODS =====
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = await self.client.indices.stats(index=self.index_name)
            
            return {
                "total_documents": stats["_all"]["primaries"]["docs"]["count"],
                "index_size_bytes": stats["_all"]["primaries"]["store"]["size_in_bytes"],
                "index_size_mb": round(
                    stats["_all"]["primaries"]["store"]["size_in_bytes"] / (1024 * 1024), 2
                )
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Elasticsearch health."""
        try:
            health = await self.client.cluster.health()
            return {
                "status": health["status"],
                "cluster_name": health["cluster_name"],
                "number_of_nodes": health["number_of_nodes"]
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}


# Singleton instance
elasticsearch_service = ElasticsearchService()
