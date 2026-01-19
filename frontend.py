import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import json
import os
import glob
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Bitcraft Market Analysis"

# Layout
app.layout = html.Div([
    html.H1("Bitcraft Market Analysis", style={'textAlign': 'center'}),
    
    html.Div(id='last-updated', style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='market-graph')
    ], style={'width': '100%', 'display': 'inline-block'}),
    
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
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
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
])

def get_latest_data_file():
    # Use absolute path or relative if consistent. Assuming ./data/ is where files are.
    base_file_path = "./data/"
    list_of_files = glob.glob(base_file_path + 'analyzed_market_data_*.json') 
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

@app.callback(
    [Output('market-graph', 'figure'),
     Output('market-table', 'data'),
     Output('last-updated', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    latest_file = get_latest_data_file()
    
    if latest_file is None:
        return {}, [], "No data found."
        
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return {}, [], f"Error loading file: {str(e)}"
    
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
         return {}, [], f"Data loaded from {os.path.basename(latest_file)} but it is empty."

    # Sort by score by default for the graph
    df_sorted = df.sort_values(by='score', ascending=False).head(50) # Top 50 for graph
    
    # Create Graph
    figure = {
        'data': [
            {'x': df_sorted['name'], 'y': df_sorted['score'], 'type': 'bar', 'name': 'Score'},
        ],
        'layout': {
            'title': 'Top 50 Items by Score',
            'xaxis': {'title': 'Item Name', 'tickangle': -45},
            'yaxis': {'title': 'Score'},
            'margin': {'b': 150} # Space for x-axis labels
        }
    }
    
    # Timestamp from filename or modification time
    timestamp = os.path.getmtime(latest_file)
    dt_object = datetime.fromtimestamp(timestamp)
    time_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return figure, df.to_dict('records'), f"Data loaded from: {os.path.basename(latest_file)} (Last modified: {time_str})"

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
