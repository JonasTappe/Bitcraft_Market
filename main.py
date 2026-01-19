import json
import requests
from time import sleep
from datetime import datetime, timedelta

from settings import Settings
from market import run_market_script
from cleanup import run_cleanup_script

s = Settings()


while True:
    # get current date and time as string YYYY-MM-DD_HH-MM-SS
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")


    print("Running market script...")
    run_market_script(s, dt_string)

    print("Running cleanup script...")
    run_cleanup_script(s)

    print("Sleeping for " + str(s.run_interval / 3600) + " hours, from " + datetime.now().strftime("%Y-%m-%d_%H-%M") + " to " + (datetime.now() + timedelta(seconds=s.run_interval)).strftime("%Y-%m-%d_%H-%M"))
    sleep(s.run_interval)