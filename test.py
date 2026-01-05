

##  this is a second main file to test code snippets  ##


import json
import requests
from datetime import datetime

from settings import Settings
from market import run_market_script
from cleanup import run_cleanup_script

import market as mk
import cleanup as cu

s = Settings()

# get current date and time as string YYYY-MM-DD_HH-MM-SS
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")


market_data = mk.load_market_data(s)

tags = []
item_with_tag = []
for item in market_data['data']["items"]:
    if item['totalOrders']:
        tags.append(item['tag'])
        item_with_tag.append((item['name'], item['tag']))


unique_tags = set(tags)

with open(s.base_file_path + 'unique_tags.txt', 'w') as f:
    for tag in unique_tags:
        f.write(f'{tag}\n')

# ------------
gatherables_tags = [
    'Sapling',
    'Rock Output',
    'Rare Mushroom',
    'Berry',
    'Clay',
    'Common Slayer Material',
    'Ore Chunk'
]
gatherables = []

craftables_tags = [
    'Fertilizer',
    'Plank',
]
craftables = []

for relation in item_with_tag:
    if relation[1] in gatherables_tags:
        gatherables.append(relation)
    if relation[1] in craftables_tags:
        craftables.append(relation)


with open(s.base_file_path + 'gatherables.txt', 'w') as f:
    for gatherable in gatherables:
        f.write(f'{gatherable}\n')

with open(s.base_file_path + 'craftables.txt', 'w') as f:
    for craftable in craftables:
        f.write(f'{craftable}\n')

with open(s.base_file_path + 'leftover_tags.txt', 'w') as f:
    for name, tag in item_with_tag:
        if tag not in gatherables_tags and tag not in craftables_tags:
            f.write(f'{tag} - {name}\n')