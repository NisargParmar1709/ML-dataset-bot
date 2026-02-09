"""
Service for interacting with the GitHub API.
"""

import requests
import logging
from typing import List, Dict
from config import Config

logger = logging.getLogger(__name__)

class GitHubService:
    """
    Handles interactions with GitHub API for repository searching.
    """
    
    def __init__(self):
        """
        Initialize GitHub service with options auth headers.
        """
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if Config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"

    def search_repositories(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for repositories on GitHub.

        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing title and url.
        """
        url = "https://api.github.com/search/repositories"
        # Optimize query for dataset-like repos
        q_enhanced = f"{query} topic:dataset OR topic:data" 
        
        params = {
            "q": q_enhanced,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results
        }
        
        try:
            # First attempt: Specific dataset query
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Second attempt: Broaden if no results
            if not data.get("items"):
                 params["q"] = f"{query} topic:machine-learning"
                 response = requests.get(url, headers=self.headers, params=params, timeout=10)
                 response.raise_for_status()
                 data = response.json()

            results = []
            for item in data.get("items", []):
                results.append({
                    "platform": "GitHub",
                    "title": item["full_name"],
                    "url": item["html_url"],
                })
            return results
            
        except requests.RequestException as e:
            logger.error(f"Network error searching GitHub repositories: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching GitHub repositories: {e}", exc_info=True)
            return []
