import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import json
import os
import glob
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

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
        dash_table.DataTable(
            id='market-table',
            columns=[
                {"name": "Item Name", "id": "name"},
                {"name": "Score", "id": "score"},
                {"name": "Total Volume", "id": "total_volume"},
                {"name": "Avg Volume", "id": "average_volume"},
                {"name": "Median Volume", "id": "median_volume"},
                {"name": "Buyer Count", "id": "buyer_count"},
                {"name": "Min Price", "id": "min_price"},
                {"name": "Max Price", "id": "max_price"},
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
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_current=0,
            page_size=20,
        )
    ], style={'marginTop': '20px'}),
    
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

@app.callback(
    [Output('market-table', 'data'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    latest_file = get_latest_data_file()
    
    if latest_file is None:
        return [], "No data found."
        
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return [], f"Error loading file: {str(e)}"
    
    # Process data for DataFrame
    df_data = []
    for item in data:
        prices = item.get('unit_prices', [])
        
        row = {
            'name': item.get('name', 'Unknown'),
            'score': round(item.get('score', 0), 4),
            'total_volume': item.get('total_volume', 0),
            'average_volume': round(item.get('average_volume', 0), 2),
            'median_volume': round(item.get('median_volume', 0), 2),
            'buyer_count': len(set(item.get('claim_ids', []))),
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0
        }
        df_data.append(row)
        
    df = pd.DataFrame(df_data)
    
    if df.empty:
         return [], f"Data loaded from {os.path.basename(latest_file)} but it is empty."

    # Timestamp from filename or modification time
    timestamp = os.path.getmtime(latest_file)
    dt_object = datetime.fromtimestamp(timestamp)
    time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return df.to_dict('records'), f"Data loaded from: {os.path.basename(latest_file)} (Last modified: {time_str})"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8052)
