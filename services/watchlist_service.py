"""Watchlist Service - Dummy Implementation"""
import json
from pathlib import Path

class WatchlistService:
    def __init__(self):
        self.watchlist_path = Path("data/watchlists")
        self.watchlist_path.mkdir(exist_ok=True)
        
    def get_watchlist(self, user_id="default"):
        """Get user watchlist"""
        file_path = self.watchlist_path / f"{user_id}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
        
    def add_to_watchlist(self, ticker, user_id="default"):
        """Add ticker to watchlist"""
        watchlist = self.get_watchlist(user_id)
        if ticker not in watchlist:
            watchlist.append(ticker)
            file_path = self.watchlist_path / f"{user_id}.json"
            with open(file_path, 'w') as f:
                json.dump(watchlist, f)
        return watchlist
