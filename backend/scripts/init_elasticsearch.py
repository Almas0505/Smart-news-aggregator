"""
Initialize Elasticsearch index and index existing news.

Usage:
    python -m scripts.init_elasticsearch
    python -m scripts.init_elasticsearch --rebuild
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.elasticsearch_service import elasticsearch_service
from app.services.news_service import NewsService
from app.core.logging import get_logger

logger = get_logger(__name__)


async def init_elasticsearch(rebuild: bool = False):
    """
    Initialize Elasticsearch and index news.
    
    Args:
        rebuild: If True, delete and recreate index
    """
    try:
        logger.info("🚀 Initializing Elasticsearch...")
        
        # Check connection
        health = await elasticsearch_service.health_check()
        logger.info(f"Elasticsearch status: {health.get('status', 'unknown')}")
        
        if health.get('status') == 'error':
            logger.error("❌ Cannot connect to Elasticsearch!")
            return False
        
        # Create index
        logger.info("Creating index...")
        success = await elasticsearch_service.create_index(delete_if_exists=rebuild)
        
        if not success:
            logger.error("❌ Failed to create index")
            return False
        
        logger.info("✅ Index created successfully")
        
        # Index existing news
        logger.info("Fetching news from database...")
        
        async with AsyncSessionLocal() as db:
            # Get all news (in batches if needed)
            all_news, total = await NewsService.get_list(db, limit=10000)
            
            if not all_news:
                logger.warning("No news found in database")
                return True
            
            logger.info(f"Found {len(all_news)} news articles (total: {total})")
            
            # Bulk index
            logger.info("Indexing news...")
            success_count, error_count = await elasticsearch_service.bulk_index_news(all_news)
            
            logger.info(f"✅ Indexed: {success_count} success, {error_count} errors")
        
        # Get stats
        stats = await elasticsearch_service.get_stats()
        logger.info(f"📊 Index stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await elasticsearch_service.close()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Initialize Elasticsearch")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild index (delete if exists)"
    )
    
    args = parser.parse_args()
    
    success = await init_elasticsearch(rebuild=args.rebuild)
    
    if success:
        logger.info("✅ Elasticsearch initialization completed!")
        sys.exit(0)
    else:
        logger.error("❌ Elasticsearch initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
