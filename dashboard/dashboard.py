import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

data_path = 'immo_data_202208_v2.csv'
data = pd.read_csv(data_path)

data = data.dropna(subset=['price_cleaned', 'space_cleaned', 'lat', 'lon', 'gde_area_forest_percentage', 'type_unified'])
print(data.columns)
print(data.shape)

data['price_cleaned'] = pd.to_numeric(data['price_cleaned'], errors='coerce')
data['space_cleaned'] = pd.to_numeric(data['space_cleaned'], errors='coerce')

app = dash.Dash(__name__)
app.title = "Swiss Real Estate Dashboard"

app.layout = html.Div([
    html.H1("Swiss Real Estate Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Price Range (in CHF):"),
        dcc.RangeSlider(
            id='price-slider',
            min=data['price_cleaned'].min(),
            max=data['price_cleaned'].max(),
            step=50000,
            value=[data['price_cleaned'].min(), data['price_cleaned'].max()],
            marks={
                data['price_cleaned'].min(): f"{data['price_cleaned'].min()/1e6}M",
                data['price_cleaned'].max(): f"{data['price_cleaned'].max()/1e6}M"
            },
        )
    ], style={'margin': '20px'}),

    html.Div([
        html.Label("Select Property Type:"),
        dcc.Dropdown(
            id='type-dropdown',
            options=[{'label': t, 'value': t} for t in data['type_unified'].unique()],
            value=None,
            clearable=True
        )
    ], style={'margin': '20px'}),

    html.Div([
        dcc.Graph(id='price-vs-surface')
    ]),


    html.Div([
        dcc.Graph(id='map', style={'height': '800px'})
    ]),

    html.Div([
        dcc.Graph(id='forest-vs-price'),
        dcc.Graph(id='type-vs-price')
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-around'})
])

@app.callback(
    [
        Output('price-vs-surface', 'figure'),
        Output('map', 'figure'),
        Output('forest-vs-price', 'figure'),
        Output('type-vs-price', 'figure')
    ],
    [
        Input('price-slider', 'value'),
        Input('type-dropdown', 'value')
    ]
)
def update_graphs(price_range, property_type):
    if property_type is None:
        filtered_data = data[(data['price_cleaned'] >= price_range[0]) &
                             (data['price_cleaned'] <= price_range[1])]
    else:
        filtered_data = data[(data['price_cleaned'] >= price_range[0]) &
                             (data['price_cleaned'] <= price_range[1]) &
                             (data['type_unified'] == property_type)]

    fig1 = px.scatter(
        filtered_data,
        x='space_cleaned',
        y='price_cleaned',
        title='Price vs. Living Space',
        labels={'space_cleaned': 'Living Space (m²)', 'price_cleaned': 'Price (CHF)'},
        color='price_cleaned',
        color_continuous_scale='Viridis'
    )


    fig3 = px.scatter_mapbox(
        filtered_data,
        lat='lat',
        lon='lon',
        color='price_cleaned',
        size='space_cleaned',
        title='Property Locations',
        labels={'price_cleaned': 'Price (CHF)', 'space_cleaned': 'Living Space (m²)'},
        center={"lat": 46.8182, "lon": 8.2275},
        zoom=7,
        mapbox_style="open-street-map"
    )

    fig4 = px.scatter(
        filtered_data,
        x='gde_area_forest_percentage',
        y='price_cleaned',
        title='Forest Area vs. Price',
        labels={'gde_area_forest_percentage': 'Forest Area (%)', 'price_cleaned': 'Price (CHF)'}
    )

    fig5 = px.box(
        filtered_data,
        x='type_unified',
        y='price_cleaned',
        title='Type vs. Price',
        labels={'type_unified': 'Type', 'price_cleaned': 'Price (CHF)'}
    )

    return fig1, fig3, fig4, fig5

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
