from dash import Dash, dcc, html, callback, Output, Input
import plotly.express as px
import pandas as pd
from backend import *

app = Dash(external_stylesheets=['assets/css/styles.css'])

set_porduct_sale_list.delay()
set_dates_list.delay()
set_products_list.delay()

names = ProductsList()
names_list = names.get_all_products()

dates = DatesList('dates')
dates_list = dates.get_all_dates()

fig = {}

app.layout = html.Div(children=[

    html.Div([
        html.Div(children='select product:', style={'font-size': 'medium', 'color': 'white', 'padding-right': '8px'}),
        dcc.Dropdown(names_list, placeholder='type to search...', id='dropdown', style={'width': '75vw'})
    ], style={'display': 'flex', 'width': '100%', 'align-items': 'center', 'padding': '8px', 'background-color': '#272121'}),

    html.Div([
        
        html.Div([

            html.H3(
                children='',
                id="head",
                style={
                    'textAlign': 'left',
                    'padding': '8px',
                    'color': 'white',
                }
            ),

            dcc.Graph(
                id='graph',
                figure=fig)
        ], style={'width': '70%', 'background-color': '#4A3F35'}),
        
        html.Div([

            html.Div([
                html.Div(id='main-cat', children='Appliances'),
                html.Div(children='>', style={'padding-right': '8px', 'padding-left': '8px'}),
                html.Div(id='sub-cat', children='All appliances'),
            ], style={'display': 'flex', 'padding-top': '16px', 'font-size': 'small', 'color': 'white'}),

            html.Img(id='image', src='', style={'width': '100%', 'max-hight': '50vh', 'border-radius': '8px', 'margin-top': '16px'}),

            html.Div([
                html.Div(id='actual-price', children='', style={'text-decoration': 'line-through'}),
                html.Div(id='discount-price', children='', style={'font-weight': 'bold', 'font-size': 'large'}),
            ], style={'padding-top': '16px', 'color': 'white'}),

            html.Div([
                html.Img(src='assets/static/star.jpg', style={'width': '20px'}),
                html.Div(id='ratings', children="", style={'padding-left': '4px'}),
                html.Div(id='no_of_ratings', children="", style={'padding-left': '4px'}),
            ], style={'padding-top': '16px', 'display': 'flex', 'color': 'white'}),

            html.A(id='amazon-link', children='view on Amazon', href='', 
                style={'text-decoration': 'none', 'padding': '8px', 'width': 'fit-content', 'color': '#FA7D09', 'font-weight': 'bold', 'border': 'solid', 'border-radius': '8px', 'border-color': '#FA7D09', 'border-width': '2px', 'margin-top': '16px'}),
            
        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '30%', 'background-color': '#4A3F35', 'padding': '8px'}),

    ], id='container', style={'width': '100%', 'display': 'none'}),

    html.Div([
        html.H1(children="select a product from navbar")
    ], id='placeholder', style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': '#4A3F35', 'color': 'white', 'height': '100vh'}),
], style={'margin': '0', 'padding': '0'})

@callback(
    Output('head', 'children'),
    Output('graph', 'figure'),
    Output('main-cat', 'children'),
    Output('sub-cat', 'children'),
    Output('image', 'src'),
    Output('actual-price', 'children'),
    Output('discount-price', 'children'),
    Output('ratings', 'children'),
    Output('no_of_ratings', 'children'),
    Output('amazon-link', 'href'),
    Output('container', 'style'),
    Output('placeholder', 'style'),
    Input('dropdown', 'value'),
    prevent_initial_call=True,
)
def update(value):
    ps = ProductSale.load(value)

    # upadte graph data with selected product's sale stats
    df = pd.DataFrame({
        "Date": dates_list,
        "Sales Count": ps.sale_dates.values(),
    })
    fig = px.bar(df, x="Date", y="Sales Count")
    fig.update_layout(
        plot_bgcolor='#4A3F35',
        paper_bgcolor='#4A3F35',
        font_color='white',
        barcornerradius=15,
    )

    # upon the first product selection, hide the placeholder and show the contents of the page 
    container_style = {'width': '100%', 'display': 'flex'}
    placeholder_style = {'display': 'none'}

    # stringify the value of ps.no_of_ratings to handle data type inconsistency
    no_of_ratings = "(" + str(ps.no_of_ratings) + " rates)"

    return value, fig, ps.main_category, ps.sub_category, ps.image, ps.actual_price, ps.discount_price, ps.ratings, no_of_ratings, ps.link, container_style, placeholder_style

if __name__ == '__main__':
    app.run(debug=True)
    worker_process = multiprocessing.Process(target=start_celery_worker)
    worker_process.start()
    worker_process.join()