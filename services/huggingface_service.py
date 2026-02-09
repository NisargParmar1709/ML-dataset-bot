"""
Service for interacting with the HuggingFace Hub API.
"""

import logging
from typing import List, Dict
from huggingface_hub import HfApi, list_datasets
from config import Config

logger = logging.getLogger(__name__)

class HuggingFaceService:
    """
    Handles interactions with HuggingFace Hub for dataset searching.
    """
    
    def __init__(self):
        """
        Initialize the HuggingFace API client.
        """
        self.api = HfApi(token=Config.HF_TOKEN)
        self.token = Config.HF_TOKEN

    def search_datasets(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for datasets on HuggingFace Hub.

        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing title and url.
        """
        try:
            # Use robust search params; 'direction' is removed as it's deprecated elsewhere
            datasets = list_datasets(
                search=query, 
                limit=max_results, 
                token=self.token,
                sort="downloads"
            )
            
            results = []
            for ds in datasets:
                ds_id = getattr(ds, 'id', 'Unknown')
                url = f"https://huggingface.co/datasets/{ds_id}"
                
                results.append({
                    "platform": "HuggingFace",
                    "title": ds_id,
                    "url": url
                })
            return results
            
        except Exception as e:
            logger.error(f"Error searching HF datasets: {e}", exc_info=True)
            return []
