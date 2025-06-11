from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import psycopg2
import boto3
from dotenv import load_dotenv
import os

# Loading env_file
load_dotenv('/etc/secrets/env_file')

# AWS S3 CREADENTIALS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# POSTGRES CREDENTIALS
POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
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

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash()
server = app.server

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
