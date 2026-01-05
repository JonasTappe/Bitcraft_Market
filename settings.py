






class Settings:
    def __init__(self):

        # settings a user needs to configure:

        # market filters
        self.max_market_data_age_hours = 5 # if market data file is older than this, fetch new data (fetching takes time)
        self.max_tier = 2 # maximum tier of items to consider
        self.min_tier = 1 # minimum tier of items to consider
        self.target_region = 7 # region ID to filter for buyers






        # advanced settings (can usually be left at default):
        self.max_old_files_to_keep = 10   # maximum number of old files to keep when cleaning up






        # ----------------- settings below this line usually do not need to be changed -----------------
        # File paths and names
        self.base_file_path = "./data/"
        self.market_data_filename = "market_data.json"
        self.chat_data_filename = "chat_data.json"

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