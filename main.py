import json
import requests
from datetime import datetime

from settings import Settings
from market import run_market_script
from cleanup import run_cleanup_script

s = Settings()

# get current date and time as string YYYY-MM-DD_HH-MM-SS
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")


print("Running market script...")
run_market_script(s, dt_string)

print("Running cleanup script...")
run_cleanup_script(s)

print("All done.")