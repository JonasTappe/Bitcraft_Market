






class Settings:
    def __init__(self):
        # File paths and names
        self.base_file_path = "./data/"
        self.market_data_filename = "market_data.json"
        self.chat_data_filename = "chat_data.json"

        # market filters
        self.max_market_data_age_hours = 5
        self.max_tier = 2
        self.target_region = 7

        # API Endpoints
        self.base_url = "https://bitjita.com/api/"
        self.endpoints = {
            "market": self.base_url + "market",
            "chat": self.base_url + "chat/messages",
            #"claims": self.base_url + "claims",
            "crafts": self.base_url + "crafts",
            "empires": self.base_url + "empires",
            "exploration_leaderboard": self.base_url + "leaderboards/exploration",
            "skills_leaderboard": self.base_url + "leaderboards/skills",
            "deals": self.base_url + "market/deals",
            "regions": self.base_url + "regions",
            "status": self.base_url + "status",
        }
        # API Parameters
        self.api_params = {
            "chat": {"limit": 100},
            "crafts": {"completed": "true"},
        }