"""
Service for interacting with the Kaggle API.
"""

import logging
from typing import List, Dict, Any
from kaggle.api.kaggle_api_extended import KaggleApi

logger = logging.getLogger(__name__)

class KaggleService:
    """
    Handles interactions with Kaggle API for dataset searching.
    """
    
    def __init__(self):
        """
        Initialize and authenticate the Kaggle API client.
        """
        self.api = KaggleApi()
        self.available = False
        try:
            self.api.authenticate()
            logger.info("Kaggle API authenticated successfully.")
            self.available = True
        except Exception as e:
            logger.error(f"Failed to authenticate Kaggle API: {e}")
            self.available = False

    def search_datasets(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for datasets on Kaggle.

        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing title and url.
        """
        if not self.available:
            logger.warning("Kaggle service unavailable, skipping search.")
            return []
        
        try:
            # Using sort_by='votes' for better quality default
            datasets = self.api.dataset_list(search=query, sort_by='votes', page=1)
            results = []
            
            # Use strict slicing to ensure we respect max_results
            for ds in datasets[:max_results]:
                # Safe attribute access with defaults
                ref = getattr(ds, 'ref', '')
                title = getattr(ds, 'title', ref)
                url = getattr(ds, 'url', f"https://www.kaggle.com/{ref}")
                
                results.append({
                    "platform": "Kaggle",
                    "title": title,
                    "url": url
                })
            return results
            
        except Exception as e:
            logger.error(f"Error searching Kaggle datasets: {e}", exc_info=True)
            return []
