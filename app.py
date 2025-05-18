import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc

df2 = pd.read_csv('data/tlc_data.csv')  # read in summarized time series data

def create_area_chart(df, metric, var, facet_wrap, title, y_label, vlines=[]):
    filtered_df = df[df['var'] == var]

    fig = px.area(
        filtered_df,
        x='dyear',
        y=metric,
        color='group',
        facet_col='group',
        facet_col_wrap=facet_wrap
    )

    for line in vlines:
        fig.add_vline(
            x=datetime.strptime(line['date'], "%Y-%m-%d").timestamp() * 1000,
            line_color=line['color'],
            line_width=3,
            line_dash=line.get('dash', None),
            annotation_text=line['label']
        )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label
    )

    for axis in fig.layout:
        if axis.startswith('yaxis'):
            fig.layout[axis].title.text = y_label

    return fig

# Set up vertical lines
vlines_fares = [
    {"date": "2011-05-04", "color": "black", "dash": "dash", "label": "Uber Intro'd<br>NYC"},
    {"date": "2020-03-13", "color": "#39FF14", "label": "COVID-19 Declared <br> Natl Emergency"}
]

vlines_mileage = [
    {"date": "2020-03-13", "color": "#39FF14", "label": "COVID-19 Declared <br> Natl Emergency"}
]

# Filtered mileage DF
startmile = '2017-01-01'
endmile = '2024-12-31'
dfmile = df2[(df2['dyear'] >= startmile) & (df2['dyear'] <= endmile)]

# Pre-create figures for speed
fig_fares_paytype = create_area_chart(df2, 'daily_fare', 'paytype', facet_wrap=1,
    title="Daily Yellow Cab Fares, 2011-2024 <br> In 2025 US Dollars",
    y_label="Millions of USD",
    vlines=vlines_fares
)

fig_fares_ratecode = create_area_chart(df2, 'daily_fare', 'ratecode', facet_wrap=2,
    title="Daily Yellow Cab Fares, 2011-2024 <br> In 2025 US Dollars",
    y_label="Millions of USD",
    vlines=vlines_fares
)

fig_fares_vendorid = create_area_chart(df2, 'daily_fare', 'vendorid', facet_wrap=1,
    title="Daily Yellow Cab Fares, 2011-2024 <br> In 2025 US Dollars",
    y_label="Millions of USD",
    vlines=vlines_fares
)

fig_mileage_paytype = create_area_chart(dfmile, 'daily_miles', 'paytype', facet_wrap=1,
    title="Daily Yellow Cab Mileage, 2017-2024",
    y_label="Miles Traveled",
    vlines=vlines_mileage
)

fig_mileage_ratecode = create_area_chart(dfmile, 'daily_miles', 'ratecode', facet_wrap=2,
    title="Daily Yellow Cab Mileage, 2017-2024",
    y_label="Miles Traveled",
    vlines=vlines_mileage
)

fig_mileage_vendorid = create_area_chart(dfmile, 'daily_miles', 'vendorid', facet_wrap=1,
    title="Daily Yellow Cab Mileage, 2017-2024",
    y_label="Miles Traveled",
    vlines=vlines_mileage
)

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server = app.server

app.layout = dbc.Container([
    html.Div([
        html.Div([
            html.H1(["Daily Revenue & Mileage"]),
            html.P(["Manhattan Yellow Cabs,", html.Br(), "2011-2024"],
                   id='subhead-text')
        ], style={
            "verticalAlign": "top",
            "height": 155,
            "width": 500
        }),

        html.Div([
            html.Div(dbc.RadioItems(
                id='data-select',
                className='btn-group',
                inputClassName='btn-check',
                labelClassName="btn btn-outline-light",
                labelCheckedClassName="btn btn-light",
                options=[
                    {"label": "Revenue", "value": "fares"},
                    {"label": "Mileage", "value": "mileage"}],
                value="fares"
            ), style={'width': 160}),
            html.Div(style={'width': 160})
        ], style={
            'margin-left': 15,
            'margin-right': 15,
            'display': 'flex'
        }),

        html.Div([
            html.H2('Group Category:'),
            dcc.Dropdown(id='graph-type',
                         options=[
                             {'label': 'Form of Payment: Cash/Credit', 'value': 'paytype'},
                             {'label': 'Vendor: Creative Mobile Tech (CMT)/Curb', 'value': 'vendorid'},
                             {'label': 'Destination: In-City/Suburb/JFK/EWR', 'value': 'ratecode'}
                         ],
                         value='paytype',
                         clearable=False,
                         optionHeight=40,
                         className='customDropdown')
        ], style={
            'width': 420,
            'margin-left': 15,
            'margin-top': 15,
            'margin-bottom': 35
        }),

        html.Div(
            id='graph-wrapper',
            style={
                'overflowX': 'auto',
                'width': '80vw',
                'padding': '1rem',
                'boxSizing': 'border-box',
                'marginTop': '7rem'
            },
            children=[
                dcc.Graph(
                    id='interactive-graph',
                    style={
                        'minWidth': '600px',
                        'height': '400px',
                        'display': 'block'  # initially visible
                    },
                    config={'responsive': True}
                ),
                html.Div(
                    id='about-text',
                    style={
                        'display': 'none',
                        'marginTop': '2rem',
                        'fontSize': '15px',
                        'maxWidth': '750px',
                        'lineHeight': '1.2',
                        'textAlign': 'left',
                        'color': 'white',
                        'backgroundColor': '#6c757d',
                        'padding': '1.5rem',
                        'borderRadius':'10px',
                        'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.1)'
                    },
                    children=[
                        html.P("Thanks for visiting. To create this dashboard, I began by downloading the full time series "
                               "of individual yellow cab trips from 2011–2025 in parquet file format.", style={'marginBottom':'0.5rem'}),
                        html.P([
                            "You can access these files on the TLC’s official site here: ",
                            html.A("TLC Trip Data", href="https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page", target="_blank")
                        ], style={'marginBottom':'0.5rem'}),
                        html.P("From there, I used DuckDB in Python (also available for R) to query the parquet files, pull relevant variables, "
                               "and summarize the daily totals in revenue and mileage.", style={'marginBottom':'0.5rem'}),
                        html.P("Because the total dataset contains over a billion rows and ~30GB even in Parquet, conventional tools like pandas are "
                               "inefficient or even unusable. DuckDB uses SQL syntax and avoids reading full datasets into memory.", style={'marginBottom':'0.5rem'}),
                        html.P("I highly recommend DuckDB — it functions as a kind of 'mini data warehouse', even for small business use.", style={'marginBottom':'0.5rem'}),
                        html.P("The visualizations were created with Plotly and embedded here using Plotly Dash.", style={'marginBottom':'0.5rem'}),
                        html.P([
                            "GitHub code is available here: ",
                            html.A("GitHub Repo", href="https://github.com/laidleyt/tlc_trips", target="_blank")
                        ], style={'marginBottom':'0.5rem'}),
                        html.P([
                            "Feel free to connect on LinkedIn: ",
                            html.A("Tom Laidley", href="https://linkedin.com/in/tomlaidley", target="_blank")
                        ], style={'marginBottom':'0.5rem'}),
                        html.P("Thanks!", style={'marginBottom':'0'})
                    ]
                )
            ]
        ),

        # Fixed position About and GitHub buttons
        html.Div([
            dbc.Button(
                "About",
                id="toggle-about-btn",
                color="secondary",
                outline=True
            ),
            html.A(
                "GitHub Repo",
                href="https://github.com/laidleyt/tlc_trips",
                target="_blank",
                className="btn btn-outline-secondary"
            )
        ], style={
            "position": "fixed",
            "bottom": "10px",
            "left": "50%",
            "transform": "translateX(-50%)",
            "zIndex": "1000",
            "display": "flex",
            "justifyContent": "center",
            "width": "auto",
            "minWidth": "200px",
            "gap": "10px"
        })

    ])
], fluid=True)


# Callback to update figure, but skip update if About text visible
@app.callback(
    Output('interactive-graph', 'figure'),
    Input('data-select', 'value'),
    Input('graph-type', 'value'),
    Input('about-text', 'style')
)
def update_graph(data_type, group_var, about_style):
    if about_style.get('display') == 'block':
        # About visible, skip updating figure to prevent empty or flicker
        return dash.no_update

    if data_type == "fares":
        if group_var == "paytype":
            return fig_fares_paytype
        elif group_var == "ratecode":
            return fig_fares_ratecode
        else:
            return fig_fares_vendorid
    else:
        if group_var == "paytype":
            return fig_mileage_paytype
        elif group_var == "ratecode":
            return fig_mileage_ratecode
        else:
            return fig_mileage_vendorid

# Callback to toggle About text and graph visibility + button label
@app.callback(
    Output('interactive-graph', 'style'),
    Output('about-text', 'style'),
    Output('toggle-about-btn', 'children'),
    Input('toggle-about-btn', 'n_clicks'),
    State('toggle-about-btn', 'children'),
    prevent_initial_call=True
)
def toggle_about(n_clicks, current_text):
    if current_text.strip().lower() == "about":
        return {'visibility': 'hidden', 'height': '0', 'overflow': 'hidden'}, {'display': 'block'}, "Back"
    else:
        return {'visibility': 'visible', 'height': 'auto', 'overflow': 'visible'}, {'display': 'none'}, "About"

if __name__ == '__main__':
    app.run_server(debug=True)

