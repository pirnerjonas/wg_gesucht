import os

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE_DIR = ''
DATA_DIR  = os.path.join(BASE_DIR, 'data/')

mapbox_access_token = "pk.eyJ1Ijoic2xhc2g0NDciLCJhIjoiY2tlOW1ueDZ1MHUyYzJ4cHh6bzJyc2VpcSJ9.wNKHxe2NEj7K7hxCIn2hjg"

# create app
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# load the data
apartment_df = pd.read_csv(os.path.join(DATA_DIR, 'apartment.csv'))
apartment_df['link'] = ['https://www.wg-gesucht.de/' + link for link in apartment_df['link']]
# define fields and  order for custom data
CUSTOM_LIST = ['title','price','squaremeter','wg_size','post_time','timespan','link']
# get one point to set figure (otherwise empty histograms when loading)
temp_hoverData = {'points': [{'curveNumber': 0,
                              'pointNumber': 6,
                              'pointIndex': 6,
                              'lon':apartment_df['lon'][0],
                              'lat': apartment_df['lat'][0],
                              'hovertext': apartment_df['title'][0],
                              'customdata':apartment_df.loc[0,CUSTOM_LIST].tolist()}]}
# compute additional fields to display
available_sizes = apartment_df['wg_size'].unique().tolist()
available_sizes.sort()
# timereference
available_times = apartment_df['_merge'].unique().tolist()
available_times.sort()
# price min and max for slider
price_min = apartment_df['price'].min()
price_max = apartment_df['price'].max()

# define layout of the app
app.layout = html.Div([
    html.Div(
        className="div-control",
        children=[
            html.H2('DASH - Shared Apartment App'),
            # filter wg size
            html.P('Select different sizes of the apartment'),
            html.Div(
                className="div-for-dropdown",
                children=[
                    dcc.Dropdown(id='filter-wg-size', 
                                 options=[{'label':i, 'value':i} for i in available_sizes],
                                 value=available_sizes,
                                 multi=True)
                ]),
            # filter time
            html.P('Select which timereference should be chosen'),
            html.Div(
                className="div-for-dropdown",
                children=[
                    dcc.Dropdown(id='filter-time', 
                                 options=[{'label':i, 'value':i} for i in available_times],
                                 value=available_times,
                                 multi=True)
                ]),
            # filter price
            html.P('Select price range'),
                    dcc.RangeSlider(id='price-slider',
                               min=price_min,
                               max=price_max,
                               step=25,
                               value=[price_min,price_max],
                               marks={int(price_min):str(price_min),
                                      int(price_max):str(price_max)}),
            html.P(id='slider-output'),
            # hover information
            html.H3('HOVER INFO'),
            html.P(id='title-hov'),
            html.P(id='timespan-hov'),
            html.P(id='price-hov'),
            html.P(id='squaremeter-hov'),
            html.P(id='wg-size-hov'),
            html.P(id='post-time-hov'),
            html.A(id='link-hov',children='Link to website')
        ]),
    # main graph, the map
    html.Div(
        className="main-content",
        children=[
            dcc.Graph(id='scatter-map',hoverData=temp_hoverData),
            html.P(),
            dcc.Graph(id='price-hist')
    ])
])

# updat mapdata regarding to dropdowns
@app.callback(
    Output('scatter-map', 'figure'),
    [Input('filter-wg-size', 'value'),
     Input('filter-time', 'value'),
     Input('price-slider', 'value')])
def upgrade_map(filter_wg_size_value, filter_time_value, slider_value):
    # filter the data
    filtered_df = apartment_df[apartment_df['wg_size'].isin(filter_wg_size_value)]
    filtered_df = filtered_df[filtered_df['_merge'].isin(filter_time_value)]
    filtered_df = filtered_df[filtered_df['price']>=slider_value[0]]
    filtered_df = filtered_df[filtered_df['price']<=slider_value[1]]
    # instanciate figure 
    fig = go.Figure()
    # add scatter map plot
    fig.add_trace(go.Scattermapbox(
        lat=filtered_df['lat'],
        lon=filtered_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
        ),
        hovertext=filtered_df['title'],
        hoverinfo='text',
        customdata=filtered_df[CUSTOM_LIST]
    ))
    # add layout
    fig.update_layout(
        autosize=True,
        showlegend=False,
        paper_bgcolor="#323130",
        margin=dict(
            l=40,
            b=40,
            t=10,
            r=0
        ),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=filtered_df['lat'].mean(),
                lon=filtered_df['lon'].mean()
            ),
            pitch=0,
            zoom=10,
            style='dark'
        )
    )
    return fig

# update histograms on dropdown and hover
@app.callback(
    Output('price-hist', 'figure'),
    [Input('scatter-map', 'hoverData'),
     Input('filter-wg-size', 'value'),
     Input('filter-time', 'value'),
     Input('price-slider', 'value')])
def update_price_hist(hoverData, filter_wg_size_value, filter_time_value, slider_value):
    # filter the data
    filtered_df = apartment_df[apartment_df['wg_size'].isin(filter_wg_size_value)]
    filtered_df = filtered_df[filtered_df['_merge'].isin(filter_time_value)]
    filtered_df = filtered_df[filtered_df['price']>=slider_value[0]]
    filtered_df = filtered_df[filtered_df['price']<=slider_value[1]]
    # create subplot figure
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Price","Squaremeter"))
    # price histogram
    fig.add_trace(
        go.Histogram(x=filtered_df['price'],
                     marker_color='#1E6CD9',
                     opacity=0.75),
        row=1, col=1
    )
    # squaremeter histogram
    fig.add_trace(
        go.Histogram(x=filtered_df['squaremeter'],
                     marker_color='#1E6CD9',
                     opacity=0.75),
 
        row=1, col=2
    )
    # configure layout
    fig.update_layout(height=300,
                      showlegend=False,
                      font_color="white",
                      plot_bgcolor="#323130",
                      paper_bgcolor="#323130")

    # horizontal line for price histogram
    fig.add_shape(
        dict(
            type="line",
            y0=0,
            x0=hoverData['points'][0]['customdata'][1],
            y1=len(filtered_df),
            x1=hoverData['points'][0]['customdata'][1],
            xref='x1',
            yref='y1',
            line=dict(color="#E83F38")

        )
    )
    # horizontal line for squaremeter histogram
    fig.add_shape(
        dict(
            type="line",
            y0=0,
            x0=hoverData['points'][0]['customdata'][2],
            y1=len(filtered_df),
            x1=hoverData['points'][0]['customdata'][2],
            xref='x2',
            yref='y2',
            line=dict(color="#E83F38")
        )
    )
    return fig

# update title on hover
@app.callback(
    Output('title-hov', 'children'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    if hoverData is None:
        raise PreventUpdate
    else:
        title=hoverData['points'][0]['customdata'][0]
        return f'Title: {title}'

# update price on hover
@app.callback(
    Output('price-hov', 'children'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    price=hoverData['points'][0]['customdata'][1]
    return f'Price: {price} €'

# update squaremeter on hover
@app.callback(
    Output('squaremeter-hov', 'children'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    squaremeter=hoverData['points'][0]['customdata'][2]
    return f'Squaremeter: {squaremeter} m²'

# update wg-size  on hover
@app.callback(
    Output('wg-size-hov', 'children'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    wg_size=hoverData['points'][0]['customdata'][3]
    return f'Size: {wg_size}'


# update post-time on hover
@app.callback(
    Output('post-time-hov', 'children'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    post_time=hoverData['points'][0]['customdata'][4]
    return f'{post_time}'

# update timespan on hover
@app.callback(
    Output('timespan-hov', 'children'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    timespan=hoverData['points'][0]['customdata'][5]
    return f'Timespan: {timespan}'

# update link 
@app.callback(
    Output('link-hov', 'href'),
    [Input('scatter-map', 'hoverData')])
def update_title(hoverData):
    url=hoverData['points'][0]['customdata'][6]
    return f'{url}'

@app.callback(
    Output('slider-output', 'children'),
    [Input('price-slider', 'value')])
def update_output(value):
    return f'Minimum: {value[0]}, Maximum: {value[1]}'

if __name__ == '__main__':
    app.run_server(debug=True)
