import os
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from supabase import create_client
import dash_bootstrap_components as dbc

# Supabase setup
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # For Render deployment

def get_data():
    # Hent data fra Supabase
    response = supabase.table('din_tabell').select('*').execute()
    return pd.DataFrame(response.data)

app.layout = dbc.Container([
    html.H1("Dashboard", className="text-center my-4"),
    
    # Grafvalg
    dcc.Dropdown(
        id='chart-type',
        options=[
            {'label': 'Linjediagram', 'value': 'line'},
            {'label': 'Søylediagram', 'value': 'bar'}
        ],
        value='line',
        className="mb-4"
    ),
    
    # Graf
    dcc.Graph(id='main-chart'),
    
    # Tabell
    html.Div(id='data-table', className="mt-4")
])

@app.callback(
    [Output('main-chart', 'figure'),
     Output('data-table', 'children')],
    [Input('chart-type', 'value')]
)
def update_charts(chart_type):
    df = get_data()
    
    # Graf
    if chart_type == 'line':
        fig = px.line(df, x='dato', y='verdi')
    else:
        fig = px.bar(df, x='dato', y='verdi')
    
    # Tabell
    table = dbc.Table.from_dataframe(
        df, 
        striped=True, 
        bordered=True, 
        hover=True,
        className="mt-4"
    )
    
    return fig, table

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
