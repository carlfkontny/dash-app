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
server = app.server

def get_data():
    response = supabase.table('Zapier').select('*').execute()
    df = pd.DataFrame(response.data)
    df['start_date'] = pd.to_datetime(df['start_date'])
    return df

app.layout = dbc.Container([
    html.H1("Treningsdata Dashboard", className="text-center my-4"),
    
    # Filtrering
    dbc.Row([
        dbc.Col([
            html.Label("Velg aktivitetstype:"),
            dcc.Dropdown(
                id='type-filter',
                options=[{'label': x, 'value': x} for x in get_data()['type'].unique()],
                multi=True,
                placeholder="Alle typer"
            )
        ])
    ], className="mb-4"),
    
    # Oppsummering
    dbc.Row([
        dbc.Col([
            html.Div(id='summary-stats', className="mb-4")
        ])
    ]),
    
    # Grafer
    dbc.Row([
        dbc.Col([
            html.H3("Distanse over tid"),
            dcc.Graph(id='distance-chart')
        ]),
        dbc.Col([
            html.H3("Høydemeter"),
            dcc.Graph(id='elevation-chart')
        ])
    ]),
    
    # Detaljert tabell
    html.H3("Aktivitetslogg", className="mt-4"),
    html.Div(id='activity-table')
])

@app.callback(
    [Output('distance-chart', 'figure'),
     Output('elevation-chart', 'figure'),
     Output('activity-table', 'children'),
     Output('summary-stats', 'children')],
    [Input('type-filter', 'value')]
)
def update_dashboard(selected_types):
    df = get_data()
    
    if selected_types:
        df = df[df['type'].isin(selected_types)]
    
    # Distansegraf
    distance_fig = px.line(
        df.sort_values('start_date'), 
        x='start_date', 
        y='distance_in_k',
        color='type',
        title="Distanse per aktivitet"
    )
    
    # Høydemetergraf
    elevation_fig = px.bar(
        df.sort_values('start_date'),
        x='start_date',
        y='total_elevation_gain',
        color='type',
        title="Høydemeter per aktivitet"
    )
    
    # Oppsummeringsstatistikk
    stats = dbc.Card([
        dbc.CardBody([
            html.H4("Oppsummering"),
            html.P(f"Totalt antall aktiviteter: {len(df)}"),
            html.P(f"Total distanse: {df['distance_in_k'].sum():.1f} km"),
            html.P(f"Totale høydemeter: {df['total_elevation_gain'].sum():.0f} m"),
        ])
    ])
    
    # Aktivitetstabell
    table = dbc.Table.from_dataframe(
        df[['start_date', 'type', 'distance_in_k', 'moving_time', 'total_elevation_gain']]
        .sort_values('start_date', ascending=False)
        .assign(
            start_date=lambda x: x['start_date'].dt.strftime('%Y-%m-%d'),
            distance_in_k=lambda x: x['distance_in_k'].round(1),
            moving_time=lambda x: pd.to_timedelta(x['moving_time'], unit='s').astype(str).str.split().str[2],
            total_elevation_gain=lambda x: x['total_elevation_gain'].round(0)
        )
        .rename(columns={
            'start_date': 'Dato',
            'type': 'Type',
            'distance_in_k': 'Distanse (km)',
            'moving_time': 'Tid',
            'total_elevation_gain': 'Høydemeter'
        }),
        striped=True,
        bordered=True,
        hover=True
    )
    
    return distance_fig, elevation_fig, table, stats

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

application = app.server
app = application
