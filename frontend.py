import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import os
import glob
from datetime import datetime
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import statistics

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Bitcraft Market Analysis"

# Apply ProxyFix for Caddy/Reverse Proxy compatibility
app.server.wsgi_app = ProxyFix(app.server.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


# Layout
app.layout = html.Div([
    html.H1("Bitcraft Market Analysis", style={'textAlign': 'center', 'color': '#FFFFFF'}),
    
    html.Div("This project is fanmade and not associated with BitCraft or Clockwork Labs", 
             style={'textAlign': 'center', 'marginBottom': '10px', 'fontStyle': 'italic', 'color': '#AAAAAA'}),

    html.Div(id='last-updated', style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#E0E0E0'}),

    html.Div([
        html.Label("Item Name: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='name-filter', type='text', placeholder='Filter by name...', style={'marginRight': '20px'}),

        html.Label("Min Buyer Count: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='min-buyer-filter', type='number', value=0, style={'marginRight': '20px', 'width': '80px'}),

        html.Label("Min Avg Volume: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='min-avg-vol-filter', type='number', value=0, style={'marginRight': '20px', 'width': '80px'}),
        
        html.Label("Min Median Volume: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='min-median-vol-filter', type='number', value=0, style={'marginRight': '20px', 'width': '80px'}),

        html.Label("Min Median Price: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='min-median-price-filter', type='number', value=0, style={'marginRight': '20px', 'width': '80px'}),

        html.Label("Min Tier: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='min-tier-filter', type='number', placeholder='Min', style={'marginRight': '10px', 'width': '60px'}),

        html.Label("Max Tier: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='max-tier-filter', type='number', placeholder='Max', style={'marginRight': '20px', 'width': '60px'}),

        html.Label("Rarity ID: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='rarity-filter', type='number', placeholder='ID', style={'marginRight': '20px', 'width': '60px'}),

        html.Label("Rarity Name: ", style={'color': '#E0E0E0', 'marginRight': '10px'}),
        dcc.Input(id='rarity-str-filter', type='text', placeholder='Name...', style={'marginRight': '20px', 'width': '100px'}),

        html.Button('Apply', id='apply-filter-btn', n_clicks=0)
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        dash_table.DataTable(
            id='market-table',
            columns=[
                {"name": "Item Name", "id": "name"},
                {"name": "Item Tier", "id": "tier"},
                {"name": "Rarity", "id": "rarityStr"},
                {"name": "Buyer Count", "id": "buyer_count"},
                {"name": "Median Volume", "id": "median_volume"},
                {"name": "Total Volume", "id": "total_volume"},
                {"name": "Median Price", "id": "median_price"},
            ],
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': '#1F1F1F',
                'color': 'white',
                'fontWeight': 'bold',
                'border': '1px solid #333'
            },
            style_data={
                'backgroundColor': '#121212',
                'color': '#E0E0E0',
                'border': '1px solid #333'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#1c1c1c'
                }
            ],
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_current=0,
            page_size=20,
            row_selectable='single'
        )
    ], style={'marginTop': '20px'}),

    html.Div([
        html.H3(id='details-title', style={'textAlign': 'center', 'color': '#FFFFFF', 'marginTop': '30px'}),
        dash_table.DataTable(
            id='details-table',
            columns=[
                {"name": "Buyer", "id": "buyer"},
                {"name": "Price", "id": "price"},
                {"name": "Quantity", "id": "quantity"},
                {"name": "Total Value", "id": "total_value"},
            ],
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': '#1F1F1F',
                'color': 'white',
                'fontWeight': 'bold',
                'border': '1px solid #333'
            },
            style_data={
                'backgroundColor': '#121212',
                'color': '#E0E0E0',
                'border': '1px solid #333'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#1c1c1c'
                }
            ],
            sort_action="native",
            page_action="native",
            page_current=0,
            page_size=10,
        )
    ], style={'marginTop': '20px', 'marginBottom': '50px'}),
    
    dcc.Interval(
        id='interval-component',
        interval=60*1000, # in milliseconds (1 minute)
        n_intervals=0
    )
], style={'backgroundColor': '#121212', 'minHeight': '100vh', 'padding': '20px'})

def get_latest_data_file():
    # Use absolute path or relative if consistent. Assuming ./data/ is where files are.
    base_file_path = "./data/"
    list_of_files = glob.glob(base_file_path + 'analyzed_market_data_*.json') 
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

    return latest_file

def apply_filters(df, min_buyer_count, name_filter, min_avg_vol, min_median_vol, min_median_price, min_tier, max_tier, rarity_filter, rarity_str_filter):
    if name_filter:
        df = df[df['name'].str.contains(name_filter, case=False, na=False)]
    
    if min_buyer_count is not None and min_buyer_count > 0:
        df = df[df['buyer_count'] >= min_buyer_count]
        
    if min_avg_vol is not None and min_avg_vol > 0:
        df = df[df['average_volume'] >= min_avg_vol]

    if min_median_vol is not None and min_median_vol > 0:
        df = df[df['median_volume'] >= min_median_vol]

    if min_median_price is not None and min_median_price > 0:
        df = df[df['median_price'] >= min_median_price]
        
    if min_tier is not None:
        df = df[df['tier'] >= min_tier]
        
    if max_tier is not None:
        df = df[df['tier'] <= max_tier]
        
    if rarity_filter is not None:
        df = df[df['rarity'] == rarity_filter]
        
    if rarity_str_filter:
        df = df[df['rarityStr'].str.contains(rarity_str_filter, case=False, na=False)]
        
    return df

@app.callback(
    [Output('market-table', 'data'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('apply-filter-btn', 'n_clicks')],
    [State('min-buyer-filter', 'value'),
     State('name-filter', 'value'),
     State('min-avg-vol-filter', 'value'),
     State('min-median-vol-filter', 'value'),
     State('min-median-price-filter', 'value'),
     State('min-tier-filter', 'value'),
     State('max-tier-filter', 'value'),
     State('rarity-filter', 'value'),
     State('rarity-str-filter', 'value')]
)
def update_metrics(n, n_clicks, min_buyer_count, name_filter, min_avg_vol, min_median_vol, min_median_price, min_tier, max_tier, rarity_filter, rarity_str_filter):
    latest_file = get_latest_data_file()
    
    if latest_file is None:
        return [], "No data found."
        
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return [], f"Error loading file: {str(e)}"
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return [], f"Error loading file: {str(e)}"
    
    # Process data for DataFrame
    df_data = []
    for item in data:
        prices = [float(p) for p in item.get('unit_prices', [])]
        
        row = {
            'name': item.get('name', 'Unknown'),
            'score': round(item.get('score', 0), 4),
            'total_volume': item.get('total_volume', 0),
            'average_volume': round(item.get('average_volume', 0), 2),
            'median_volume': round(item.get('median_volume', 0), 2),
            'buyer_count': len(set(item.get('claim_ids', []))),
            'median_price': item.get('median_price', 0),
            'tier': item.get('tier', 0),
            'rarity': item.get('rarity', 0),
            'rarityStr': item.get('rarityStr', '')
        }
        df_data.append(row)
        
    df = pd.DataFrame(df_data)
    
    if df.empty:
         return [], f"Data loaded from {os.path.basename(latest_file)} but it is empty."

    # Apply filters
    df = apply_filters(df, min_buyer_count, name_filter, min_avg_vol, min_median_vol, min_median_price, min_tier, max_tier, rarity_filter, rarity_str_filter)

    # Timestamp from filename or modification time
    timestamp = os.path.getmtime(latest_file)
    dt_object = datetime.fromtimestamp(timestamp)
    time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return df.to_dict('records'), f"Data loaded from: {os.path.basename(latest_file)} (Last modified: {time_str})"


@app.callback(
    [Output('details-table', 'data'),
     Output('details-title', 'children')],
    [Input('market-table', 'derived_virtual_selected_rows'),
     Input('market-table', 'derived_virtual_data')]
)
def update_details_table(selected_rows, rows):
    if not selected_rows or not rows:
        return [], ""
    
    # Get the selected item's name from the table view (rows)
    selected_index = selected_rows[0]
    if selected_index >= len(rows):
        return [], ""
        
    selected_item = rows[selected_index]
    item_name = selected_item.get('name')
    
    if not item_name:
        return [], ""

    # Load full data to get details
    latest_file = get_latest_data_file()
    if latest_file is None:
        return [], "Error: Data source not found"
        
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
    except Exception:
        return [], "Error loading data"

    # Find the specific item in the full dataset
    item_data = next((item for item in data if item.get('name') == item_name), None)
    
    if not item_data:
        return [], f"Details for {item_name} not found"
        
    # Extract details
    buyers = item_data.get('claim_names', [])
    prices = [float(p) for p in item_data.get('unit_prices', [])]
    quantities = item_data.get('quantities', [])
    order_volumes = item_data.get('order_volumes', [])
    
    # Create DataFrame for details
    # Ensure all lists are same length to avoid errors, though they should be from extraction
    min_len = min(len(buyers), len(prices), len(quantities), len(order_volumes))
    
    details_data = []
    for i in range(min_len):
        details_data.append({
            'buyer': buyers[i],
            'price': prices[i],
            'quantity': quantities[i],
            'total_value': order_volumes[i]
        })
        
    df_details = pd.DataFrame(details_data)
    
    return df_details.to_dict('records'), f"Buy Orders for: {item_name}"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8052)
