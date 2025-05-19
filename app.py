import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# Load your summarized time series data
df2 = pd.read_csv('data/tlc_data.csv')

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

# Vertical lines for important dates
vlines_fares = [
    {"date": "2011-05-04", "color": "black", "dash": "dash", "label": "Uber Intro'd<br>NYC"},
    {"date": "2020-03-13", "color": "#39FF14", "label": "COVID-19 Declared <br> Natl Emergency"}
]

vlines_mileage = [
    {"date": "2020-03-13", "color": "#39FF14", "label": "COVID-19 Declared <br> Natl Emergency"}
]

# Filter mileage data from 2017 onwards
startmile = '2017-01-01'
endmile = '2024-12-31'
dfmile = df2[(df2['dyear'] >= startmile) & (df2['dyear'] <= endmile)]

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server = app.server

app.layout = dbc.Container([
    # Header and controls
    html.Div([
        html.Div([
            html.H1("Daily Revenue & Mileage"),
            html.P(["Manhattan Yellow Cabs,", html.Br(), "2011-2024"], id='subhead-text')
        ], style={"verticalAlign": "top", "height": 155, "width": 500}),

        html.Div([
            dbc.RadioItems(
                id='data-select',
                className='btn-group',
                inputClassName='btn-check',
                labelClassName="btn btn-outline-light",
                labelCheckedClassName="btn btn-light",
                options=[
                    {"label": "Revenue", "value": "fares"},
                    {"label": "Mileage", "value": "mileage"}],
                value="fares",
                style={'width': 160}
            )
        ], style={'marginLeft': 15, 'marginRight': 15, 'display': 'flex'}),

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
                         className='customDropdown',
                         style={'width': 420, 'marginLeft': 15, 'marginTop': 15, 'marginBottom': 35}
            )
        ]),

        # Graph container (always visible)
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
                    style={'minWidth': '100%', 'display': 'block', 'opacity': 1},
                    config={'responsive': True}
                )
            ]
        ),
    ]),

    # Fixed bottom bar with About button and GitHub link + About modal
    html.Div([
        dbc.Button("About", id="open-about", color="secondary", outline=True, style={
            "backgroundColor": "#6c757d",
            "color": "white",
            "border": "none",
            "boxShadow": "none",
            "fontWeight": "600",
            "padding": "0.375rem 0.75rem"
        }),
        html.A(
            "GitHub Repo",
            href="https://github.com/laidleyt/tlc_trips",
            target="_blank",
            className="btn btn-darkgray",
            style={
                "backgroundColor": "#6c757d",
                "color": "white",
                "border": "none",
                "textDecoration": "none",
                "padding": "0.375rem 0.75rem",
                "fontWeight": "600"
            }
        ),

        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("About This Dashboard")),
                dbc.ModalBody([
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
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-about", className="ml-auto")
                )
            ],
            id="modal-about",
            is_open=False,
            size="lg",
            centered=True,
            scrollable=True,
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
        "gap": "1rem"
    })
], fluid=True)


@app.callback(
    Output("interactive-graph", "figure"),
    Input("data-select", "value"),
    Input("graph-type", "value"),
)
def update_graph(selected_data, selected_group):
    if selected_data == "fares":
        return create_area_chart(
            df2,
            "totalfares",
            selected_group,
            4,
            "Daily Yellow Cab Revenue by Group Category",
            "Revenue (Millions $)",
            vlines=vlines_fares
        )
    else:
        return create_area_chart(
            dfmile,
            "totalmileage",
            selected_group,
            3,
            "Daily Yellow Cab Mileage by Group Category",
            "Miles (Millions)",
            vlines=vlines_mileage
        )


@app.callback(
    Output("modal-about", "is_open"),
    [Input("open-about", "n_clicks"), Input("close-about", "n_clicks")],
    [State("modal-about", "is_open")]
)
def toggle_about_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)
