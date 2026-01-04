import json
import requests
from datetime import datetime
import time
from time import sleep
import os
import statistics
import numpy as np



def run_market_script(s, dt_string):

    # list all market data files
    files = os.listdir(s.base_file_path)
    market_data_files = [f for f in files if f.startswith("market_data_") and f.endswith(".json")]
    # find age of newest file in hours
    if market_data_files:
        newest_file = max(market_data_files, key=lambda x: os.path.getctime(os.path.join(s.base_file_path, x)))
        file_creation_time = os.path.getctime(os.path.join(s.base_file_path, newest_file))
        file_age_hours = (time.time() - file_creation_time) / 3600
        print(f"Newest market data file: {newest_file}, age: {file_age_hours:.2f} hours")

    if not market_data_files or file_age_hours > s.max_market_data_age_hours:
        print('No recent market data file found, fetching new data...')
        # fetch new market data
        url = s.endpoints["market"]
        response = requests.get(url)
        data_market = response.json()

        with open(s.base_file_path + "market_data_" + dt_string + ".json", "w") as f:
            json.dump(data_market, f, indent=4)

        data = data_market["data"]
        items = data["items"]

        suitable_items = []
        for entry in items:
            if entry['tier'] <= s.max_tier:
                if entry['buyOrders'] == 1:
                    suitable_items.append(entry['id'])
        
        print(f"Found {len(suitable_items)} suitable items.")
        print('this may take a while, fetching detailed data for suitable items...')

        # get detailed data for suitable items
        data_suitable_items = []
        if suitable_items:
            # display progress in percentages of suitable items fetched
            total_items = len(suitable_items)
            progress_interval = np.max([1, total_items // 10])  # update progress every 10%
            for index, item_id in enumerate(suitable_items):
                # print progress
                if index % progress_interval == 0:
                    progress_percent = (index / total_items) * 100
                    print(f'Progress: {progress_percent:.0f}% ({index}/{total_items})')
                
                sleep(0.25)  # to avoid hitting rate limits
                
                # fetch detailed data for item
                url = s.endpoints['market'] + '/' + str(item_id)
                response_item = requests.get(url)
                data_item = response_item.json()
                data_suitable_items.append(data_item)
            
            print(f'saving data for {len(data_suitable_items)} suitable items.')
            with open(s.base_file_path + "suitable_items_data_" + dt_string + ".json", "w") as f:
                json.dump(data_suitable_items, f, indent=4)

    # ----------------------------------------------------------------------------------------
    # analysis of the suitable items
    if True:
        # load data
        # list all suitable item data files
        files = os.listdir(s.base_file_path)
        suitable_files = [f for f in files if f.startswith("suitable_items_data_") and f.endswith(".json")]
        
        # check if any suitable items data files exist
        if not suitable_files:
            print("No suitable items data files found. Skipping analysis.")
        else:
            # find newest file
            newest_file = max(suitable_files, key=lambda x: os.path.getctime(os.path.join(s.base_file_path, x)))
            # load data from newest file
            with open(s.base_file_path + newest_file, "r") as f:
                data_suitable_items = json.load(f)

            # get buy orders
            extracted_data = []    
            for entry in data_suitable_items:
                try: # catching possible KeyError
                    item = entry['item']
                except KeyError:
                    continue
                name = entry['item']['name']
                all_buy_orders = entry['buyOrders']
                if not all_buy_orders:
                    continue

                # filter buy orders by target region
                buy_orders = [order for order in all_buy_orders if order['regionId'] == s.target_region]
                if not buy_orders:
                    continue

                # get list of unit prices and quantities
                unit_prices = []
                quantities = []
                claim_ids = []
                claim_names = []
                order_volumes = []
                for order in buy_orders:
                    if order['priceThreshold'] is not None and order['quantity'] is not None:
                        unit_prices.append(order['priceThreshold'])
                        quantities.append(order['quantity'])
                        claim_ids.append(order['claimEntityId'])
                        claim_names.append(order['claimName'])
                        order_volume = int(order['priceThreshold']) * int(order['quantity'])
                        order_volumes.append(order_volume)


                extracted_data.append({
                    'name': name,
                    'unit_prices': unit_prices,
                    'quantities': quantities,
                    'claim_ids': claim_ids,
                    'claim_names': claim_names,
                    'order_volumes': order_volumes
                })
            
            # sort by 1. mean order volume 2. median order volume descending
            from statistics import mean, median
            extracted_data.sort(key=lambda x: (mean(x['order_volumes']), median(x['order_volumes'])), reverse=True)

            # write data to human readable file
            with open(s.base_file_path + "extracted_market_data_" + dt_string + ".txt", "w") as f:
                for item in extracted_data:
                    f.write(f"Item: {item['name']}\n")
                    for price, qty, claim_name, order_volume in zip(item['unit_prices'], item['quantities'], item['claim_names'], item['order_volumes']):
                        f.write(f"  Price: {price}, Quantity: {qty}, Buyer: {claim_name}, Order Volume: {order_volume}\n")
                    f.write("\n")
    