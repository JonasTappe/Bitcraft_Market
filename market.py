import json
import requests
from datetime import datetime
import time
from time import sleep
import os
import statistics
import numpy as np
from statistics import mean, median



def run_market_script(s, dt_string):

    # load or fetch market data
    market_data_files, file_age_hours = market_data_files_check(s)

    if not market_data_files or file_age_hours > s.max_market_data_age_hours:
        print('No recent market data file found, fetching new data...')
        data = fetch_market_overview(s, dt_string)
    else:
        print('Loading market data from file...')
        data = load_market_data(s)
    
    # find suitable items in current market overview
    if data:
        items = data['data']["items"]
        # filter market overview for suitable items
        suitable_items = find_suitable_items(s, items)
        print(f'Found {len(suitable_items)} suitable items (tier {s.min_tier} to {s.max_tier} with buy orders).')

    # load data for suitable items if it exists
    data_suitable_items = load_suitable_items_data(s)

    # fetch detailed data for suitable items if not loaded
    if suitable_items and not data_suitable_items:
        data_suitable_items = fetch_detailed_data_for_items(s, suitable_items, dt_string)


    # ----------------------------------------------------------------------------------------
    # analysis of the suitable items

    if data_suitable_items:
        print('Running analysis on suitable items...')
        # run analysis
        extracted_data = extract_relevant_information(s, data_suitable_items)
        
        # add score to items
        scored_data = calculate_scores(s, extracted_data)

        # sort the data
        sorted_data = sorted(scored_data, key=lambda x: x['score'], reverse=True)

        # write data to human readable file
        write_human_readable_output(s, sorted_data, dt_string)
    


def market_data_files_check(s):
    # list all market data files
    files = os.listdir(s.base_file_path)
    market_data_files = [f for f in files if f.startswith("market_data_") and f.endswith(".json")]
    # find age of newest file in hours
    if market_data_files:
        newest_file = max(market_data_files, key=lambda x: os.path.getctime(os.path.join(s.base_file_path, x)))
        file_creation_time = os.path.getctime(os.path.join(s.base_file_path, newest_file))
        file_age_hours = (time.time() - file_creation_time) / 3600
        print(f"Newest market data file: {newest_file}, age: {file_age_hours:.2f} hours")

    return market_data_files, file_age_hours

def fetch_market_overview(s, dt_string):
    # fetch new market data
    url = s.endpoints["market"]
    response = requests.get(url)
    data_market = response.json()

    with open(s.base_file_path + "market_data_" + dt_string + ".json", "w") as f:
        json.dump(data_market, f, indent=4)

    return data_market

def find_suitable_items(s, items):
    suitable_items = []
    for entry in items:
        if s.min_tier <= entry['tier'] <= s.max_tier:
            if entry['buyOrders'] == 1:
                suitable_items.append(entry['id'])
    
    return suitable_items

def fetch_detailed_data_for_items(s, suitable_items, dt_string):
    data_suitable_items = []
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
    with open(s.base_file_path + "suitable_items_data_" + dt_string + "_" + str(s.min_tier) + str(s.max_tier) + str(s.target_region) + ".json", "w") as f:
        json.dump(data_suitable_items, f, indent=4)

    return data_suitable_items

def extract_relevant_information(s, data_suitable_items):
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
            'order_volumes': order_volumes,
            'total_volume': sum(order_volumes) if order_volumes else 0,
            'average_volume': mean(order_volumes) if order_volumes else 0,
            'median_volume': median(order_volumes) if order_volumes else 0,
        })

    return extracted_data

def load_suitable_items_data(s):
    # list all suitable item data files
    files = os.listdir(s.base_file_path)
    suitable_files = [f for f in files if f.startswith("suitable_items_data_") and f.endswith(".json")]
    if not suitable_files:
        return False
    # find newest file
    newest_file = max(suitable_files, key=lambda x: os.path.getctime(os.path.join(s.base_file_path, x)))
    # load data from newest file
    with open(s.base_file_path + newest_file, "r") as f:
        data_suitable_items = json.load(f)

    return data_suitable_items

def load_market_data(s):
    # list all market data files
    files = os.listdir(s.base_file_path)
    market_data_files = [f for f in files if f.startswith("market_data_") and f.endswith(".json")]
    if not market_data_files:
        return False
    # find newest file
    newest_file = max(market_data_files, key=lambda x: os.path.getctime(os.path.join(s.base_file_path, x)))
    # load data from newest file
    with open(s.base_file_path + newest_file, "r") as f:
        data_market = json.load(f)

    return data_market

def calculate_scores(s, data):
    # normalize total_volume, average_volume and mean volume to 0-1 scale
    total_volumes = [item['total_volume'] for item in data]
    average_volumes = [item['average_volume'] for item in data]
    median_volumes = [item['median_volume'] for item in data]
    
    max_total_volume = max(total_volumes) if total_volumes else 1
    max_average_volume = max(average_volumes) if average_volumes else 1
    max_median_volume = max(median_volumes) if median_volumes else 1
    
    for item in data:
        norm_total_volume = item['total_volume'] / max_total_volume if max_total_volume > 0 else 0
        norm_average_volume = item['average_volume'] / max_average_volume if max_average_volume > 0 else 0
        norm_median_volume = item['median_volume'] / max_median_volume if max_median_volume > 0 else 0
        
        # calculate score
        score = (norm_total_volume + norm_average_volume) / 2
        item['score'] = score

    return data


def write_human_readable_output(s, data, dt_string):
    with open(s.base_file_path + "extracted_market_data_" + dt_string + ".txt", "w") as f:
        for item in data:
            f.write(f"Item: {item['name']}\n")
            f.write(f"Score: {item['score']}\n")
            for price, qty, claim_name, order_volume in zip(item['unit_prices'], item['quantities'], item['claim_names'], item['order_volumes']):
                f.write(f"  Price: {price}, Quantity: {qty}, Buyer: {claim_name}, Order Volume: {order_volume}\n")
            f.write("\n")