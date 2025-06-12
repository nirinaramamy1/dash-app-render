import pandas as pd
import psycopg2
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import os
from dotenv import load_dotenv
from unidecode import unidecode

# Dash app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Load environment variables
load_dotenv('/etc/secrets/env_file')
# load_dotenv('.env')

# PostgreSQL credentials
POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')

# Connexion to database
conn = psycopg2.connect(
    dbname=POSTGRES_DB_NAME,
    user=POSTGRES_DB_USER,
    password=POSTGRES_DB_PASSWORD,
    host=POSTGRES_DB_HOST,
    port=POSTGRES_PORT,
)
cursor = conn.cursor()

on_off_head = html.H1("OnOff Data visualisation", className="bg-secondary text-white p-2")
singer_head = html.H2("Singers visualisation", className="bg-secondary text-white p-2")
singer_project_head = html.H2("Singers interaction with projects visualisation", className="bg-secondary text-white p-2")


def fetch_data(query):
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(results, columns=columns)

def singer_gender_graph():
    df = fetch_data("""
        SELECT name, gender
        FROM singers
    """)
    df = df[df["name"] != "scraper"].drop(columns=["name"])
    df = df["gender"].value_counts().reset_index()
    df.columns = ['gender', 'count']

    fig = go.Figure(
        data=[go.Pie(
            labels=df['gender'],
            values=df['count'],
            hole=0.3,
            textinfo='label+value',
            textfont_size=12
        )]
    )

    fig.update_layout(
        width=500,
        height=400,
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1.2,
                y=0.5,
                showarrow=False,
                font=dict(size=18)
            ),
            dict(
                text='Gender',
                x=1.19,
                y=1.1,
                showarrow=False,
                font=dict(size=18)
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion de male et female"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def genres_preprocessing(genre):
    return unidecode(str(genre).strip().lower())

def singer_project_style():
    df = fetch_data("""
        SELECT genres, style
        FROM project_observations
    """)
    df = df[~df["genres"].isna()].reset_index(drop=True)
    df.loc[:,"genres"] = df["genres"].apply(genres_preprocessing)
    df = df["style"].value_counts().reset_index()
    df.columns = ['style', 'count']

    fig = go.Figure(
        data=[go.Pie(
            labels=df['style'],
            values=df['count'],
            hole=0.3,
            textinfo='label+value',
            textfont_size=12
        )]
    )

    fig.update_layout(
        width=500,
        height=400,
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1.2,
                y=0.5,
                showarrow=False,
                font=dict(size=18)
            ),
            dict(
                text='Genre',
                x=1.19,
                y=1.1,
                showarrow=False,
                font=dict(size=18)
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion des styles de projets"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

app.layout = dbc.Container(
    [
        on_off_head,
        singer_head,
        dbc.Row([
            dbc.Col(singer_gender_graph()),
        ]),
        singer_project_head,
        dbc.Row([
            dbc.Col(singer_project_style()),
        ]),
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)