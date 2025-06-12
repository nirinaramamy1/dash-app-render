import pandas as pd
import psycopg2
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import os
from dotenv import load_dotenv

# Dash app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Load environment variables
load_dotenv('/etc/secrets/env_file')

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

heading = html.H1("OnOff Data Exploratory and Analysis", className="bg-secondary text-white p-2 mb-4")

def fetch_data(query):
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(results, columns=columns)

def singer_gender_graph():
    df = fetch_data("""
        SELECT gender
        FROM singers
    """)
    genre_counts = df["gender"].value_counts()
    genre_df = genre_counts.reset_index()
    genre_df.columns = ['gender', 'count']

    fig = go.Figure(
        data=[go.Pie(
            labels=genre_df['gender'],
            values=genre_df['count'],
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
                text=f"Total: {genre_df['count'].sum()}",
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
        dbc.CardHeader(html.H2("Proportion de male et female"), className="text-center"),
        dcc.Graph(figure=fig, style={"height":250}, config={'response': True})
    ])

app.layout = dbc.Container(
    [
        heading,
        dbc.Col(singer_gender_graph())
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)