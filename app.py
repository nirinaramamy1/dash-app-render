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

try:
    conn = psycopg2.connect(
        dbname=POSTGRES_DB_NAME,
        user=POSTGRES_DB_USER,
        password=POSTGRES_DB_PASSWORD,
        host=POSTGRES_DB_HOST,
        port=POSTGRES_PORT,
    )
    cursor = conn.cursor()
    query = """
    SELECT po.title, po.style, po.song_type, po.genres, po.language, po.created_at,
           s.name AS singer, s.gender AS singer_gender, f.filename AS filename,
           f.file_path AS s3_path, f.file_category, f.mime_type AS mime_type, f.file_type AS type
    FROM project_observations po
    JOIN project_singer_association psa ON psa.project_observation_id = po.id
    JOIN singers s ON psa.singer_id = s.id
    JOIN files f ON f.project_id = po.id
    ORDER BY po.created_at DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(results, columns=columns)
except Exception as e:
    print("Erreur PostgreSQL:", e)
    df = pd.DataFrame()


heading = html.H1("OnOff Data exploratory and Analysis", className="bg-secondary text-white p-2 mb-4")

app.layout = dbc.Container(
    [
        dcc.Store(id="store-selected", data={}),
        heading,
        dbc.Row([
            # dbc.Col([control_panel, info], md=3),
            dbc.Col(
                [
                    dcc.Markdown(id="title"),
                    dbc.Row([dbc.Col(html.Div(id="paygap-card")), dbc.Col( html.Div(id="bonusgap-card"))]),
                    html.Div(id="bar-chart-card", className="mt-4"),
                ],  md=9
            ),
        ]),
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)