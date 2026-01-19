from settings import Settings
from market import run_market_script
from datetime import datetime

s = Settings()
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")

print("Running market script once for testing...")
run_market_script(s, dt_string)
print("Done.")
