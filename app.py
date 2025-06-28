import pandas as pd
import psycopg2
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import os
import re
from dotenv import load_dotenv
from unidecode import unidecode

# Dash app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server

# Load environment variables
load_dotenv('/etc/secrets/env_file')
load_dotenv('.env')

# PostgreSQL credentials
POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')

on_off_head = html.H1("OnOff Data visualisation", className="bg-secondary text-white p-2")

def fetch_data(query):
    with psycopg2.connect(
        dbname=POSTGRES_DB_NAME,
        user=POSTGRES_DB_USER,
        password=POSTGRES_DB_PASSWORD,
        host=POSTGRES_DB_HOST,
        port=POSTGRES_PORT,
    ) as conn:
        with conn.cursor() as cursor:
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
    # return unidecode(
    #     str(genre.replace(";", ",").replace("/", ",").replace("-", " ")
    #     ).strip().lower().replace("rnb", "r&b").split(",")[0]
    # )
    first_genre = re.sub(r'\s+', ' ', genre.replace(";", ",").replace("/", ",").replace("-", " ").lower().replace("rnb", "r&b")).strip().split(",")[0]
    return unidecode(first_genre)

def normalize_row(row):
    if '|' in row['genres']:
        genres = [g.strip() for g in row['genres'].split('|')]
        if row['file_category'] == 'DELIVERABLE':
            return pd.Series([genres[0], row['project_id'], 'DELIVERABLE'])
        elif row['file_category'] == 'REFERENCES':
            return pd.Series([genres[1], row['project_id'], 'REFERENCES'])
    else:
        return pd.Series([row['genres'], row['project_id'], row['file_category']])
    

def singer_project_style():
    df = fetch_data("""
        SELECT style
        FROM project_observations
    """)
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

def project_per_language():
    df = fetch_data("""
        SELECT language
        FROM project_observations
    """)
    # Compute project counts by language
    df = df["language"].value_counts().reset_index()
    df.columns = ['lang', 'count']

    # Create the bar chart using Graph Objects
    fig = go.Figure(
        data=[
            go.Bar(
                x=df['lang'],
                y=df['count'],
                text=df['count'],
                # textposition='outside',
                # textfont=dict(size=8),
                marker=dict(
                    color=list(range(len(df['lang'].values))), # Assign colors based on language
                    # colorscale='Viridis'  # Use a colorscale for distinct colors
                )
            )
        ]
    )

    # Update layout to match the original styling
    fig.update_layout(
        # title='Projets répartis par langue',
        xaxis_title='Langues',
        yaxis_title='Nombre de projets',
        showlegend=False,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1,
                y=1.1,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18),
                align="left"
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion des projets par langue"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def project_per_song_type():
    df = fetch_data("""
        SELECT song_type
        FROM project_observations
    """)
    # Compute project counts by song_type
    df = df["song_type"].value_counts().reset_index()
    df.columns = ['type', 'count']

    # Create the bar chart using Graph Objects
    fig = go.Figure(
        data=[
            go.Bar(
                x=df['type'],
                y=df['count'],
                text=df['count'],
                # textposition='outside',
                # textfont=dict(size=8),
                marker=dict(
                    color=list(range(len(df['type'].values))), # Assign colors based on language
                )
            )
        ]
    )

    # Update layout to match the original styling
    fig.update_layout(
        # title='Projets répartis par langue',
        xaxis_title='Type de chant',
        yaxis_title='Nombre de projets',
        showlegend=False,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1,
                y=1.1,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18),
                align="left"
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion des projets par type de chants"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def project_genres_graph():
    df = fetch_data("""
        SELECT po.id AS project_id, po.genres, f.file_category
        FROM project_observations po
        JOIN project_singer_association psa ON psa.project_observation_id = po.id
        JOIN singers s ON psa.singer_id = s.id
        JOIN files f ON f.project_id = po.id
        ORDER BY po.created_at DESC
    """)
    df = df.dropna(subset=["genres"], ignore_index=True)
    df = df.apply(normalize_row, axis=1)
    df.columns = ['genres', 'project_id', 'file_category']
    df.genres = df.genres.values
    df = df.dropna(subset=["genres"], ignore_index=True)
    df = df["genres"].apply(genres_preprocessing).value_counts().reset_index()
    df.columns = ['genres', 'count']

    fig = go.Figure(go.Treemap(
        labels=df['genres'],
        parents=[""] * len(df),
        values=df['count'],
        marker=dict(
            colors=df['count'],
            colorscale='Viridis',
            colorbar=dict(title='Count')
        ),
        texttemplate='%{label}<br><br>%{value}',
        # textfont=dict(size=14),
    ))

    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0)
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Genres musicaux"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def project_file_category():
    df = fetch_data("""
        SELECT po.title, f.file_category
        FROM project_observations po
        JOIN project_singer_association psa ON psa.project_observation_id = po.id
        JOIN singers s ON psa.singer_id = s.id
        JOIN files f ON f.project_id = po.id
        ORDER BY po.created_at DESC
    """)
    # Compute project counts by file_category
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    df = df.groupby(["file_category"])["title"].count().reset_index()
    df.columns = ["category", "count"]

    # Create the bar chart using Graph Objects
    fig = go.Figure(
        data=[
            go.Bar(
                x=df['category'],
                y=df['count'],
                text=df['count'],
                # textposition='outside',
                # textfont=dict(size=8),
                marker=dict(
                    color=list(range(len(df['category'].values))), # Assign colors based on language
                )
            )
        ]
    )

    # Update layout to match the original styling
    fig.update_layout(
        # title='Projets répartis par langue',
        xaxis_title='Categorie de fichiers',
        yaxis_title='Nombre de projets',
        showlegend=False,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1,
                y=1.1,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18),
                align="left"
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion des projets à titre unique par categories"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def project_file_type():
    df = fetch_data("""
        SELECT po.title, f.file_type
        FROM project_observations po
        JOIN project_singer_association psa ON psa.project_observation_id = po.id
        JOIN singers s ON psa.singer_id = s.id
        JOIN files f ON f.project_id = po.id
        ORDER BY po.created_at DESC
    """)
    # Compute project counts by file_type
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    df = df.groupby(["file_type"])["title"].count().reset_index()
    df.columns = ["type", "count"]

    # Create the bar chart using Graph Objects
    fig = go.Figure(
        data=[
            go.Bar(
                x=df['type'],
                y=df['count'],
                text=df['count'],
                # textposition='outside',
                # textfont=dict(size=8),
                marker=dict(
                    color=list(range(len(df['type'].values))), # Assign colors based on language
                )
            )
        ]
    )

    # Update layout to match the original styling
    fig.update_layout(
        # title='Projets répartis par langue',
        xaxis_title='Type de fichiers',
        yaxis_title='Nombre de projets',
        showlegend=False,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1,
                y=1.1,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18),
                align="left"
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion des projets à titre unique par type"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def project_file_type_extension():
    df = fetch_data("""
        SELECT f.filename
        FROM project_observations po
        JOIN project_singer_association psa ON psa.project_observation_id = po.id
        JOIN singers s ON psa.singer_id = s.id
        JOIN files f ON f.project_id = po.id
        ORDER BY po.created_at DESC
    """)
    # Compute project counts by file_type extension
    df["filename_ext"] = df["filename"].apply(lambda x : x.split(".")[-1].lower())
    df = df.groupby(["filename_ext"])["filename"].count().reset_index()
    df.columns = ["extension", "count"]

    # Create the bar chart using Graph Objects
    fig = go.Figure(
        data=[
            go.Bar(
                x=df['extension'],
                y=df['count'],
                text=df['count'],
                # textposition='outside',
                # textfont=dict(size=8),
                marker=dict(
                    color=list(range(len(df['extension'].values))), # Assign colors based on language
                )
            )
        ]
    )

    # Update layout to match the original styling
    fig.update_layout(
        # title='Projets répartis par langue',
        xaxis_title='Type de fichiers',
        yaxis_title='Nombre de fichiers',
        showlegend=False,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        annotations=[
            dict(
                text=f"Total: {df['count'].sum()}",
                x=1,
                y=1.1,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18),
                align="left"
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Poportion des fichiers"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

def project_file_type_extension_per_file_category():
    df = fetch_data("""
        SELECT po.title, f.filename, f.file_category
        FROM project_observations po
        JOIN project_singer_association psa ON psa.project_observation_id = po.id
        JOIN singers s ON psa.singer_id = s.id
        JOIN files f ON f.project_id = po.id
        ORDER BY po.created_at DESC
    """)
    
    # Extraire l'extension
    df["filename_ext"] = df["filename"].apply(lambda x: x.split(".")[-1].lower())
    
    df = df.pivot_table(
        index='filename_ext',
        columns='file_category',
        values='title',
        aggfunc='count',
        fill_value=0
    )

    # Création de la heatmap avec go.Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns.tolist(),
        y=df.index.tolist(),
        text=df.values,
        texttemplate="%{text}",
        colorscale='Blues',
        colorbar=dict(title='Nb fichiers'),
        hovertemplate='Extension: %{y}<br>Catégorie: %{x}<br>Nb fichiers: %{z}<extra></extra>'
    ))


    # Mise en forme du layout
    fig.update_layout(
        # title='Carte de chaleur des fichiers par extension et catégorie',
        xaxis_title='Catégorie',
        yaxis_title='Extension',
        # template='plotly_white'
        annotations=[
            dict(
                text=f"Total: {df.sum().sum()}",
                x=1,
                y=1.1,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=18),
                align="left"
            )
        ]
    )

    return dbc.Card([
        dbc.CardHeader(html.H2("Proportion des fichiers par extension et catégorie"), className="text-center"),
        dbc.CardBody(
            [dcc.Graph(figure=fig, config={'responsive': True})],
            className="d-flex justify-content-center align-items-center"
        )
    ], className="mt-2 mb-2")

singers = fetch_data("""
    SELECT name
    FROM singers
    WHERE name <> 'scraper'
""")["name"]

app.layout = dbc.Container(
    [
        on_off_head,
        dbc.Row([
            dbc.Col(singer_gender_graph()),
            dbc.Col(singer_project_style()),
        ]),
        dbc.Row([
            dbc.Col(project_per_language()),
            dbc.Col(project_per_song_type()),
        ]),
        dbc.Row([
            dbc.Col(project_genres_graph()),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("Projets par langue pour le chanteur", className="text-center"),
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                                dcc.Dropdown(
                                id='singer-dropdown',
                                options=[{'label': singer, 'value': singer} for singer in singers],
                                value=singers[0],
                            ),
                        ]),
                        dbc.Row(id='singer-projects-graph')
                    ])
                ], className="mt-2 mb-2")
            )
        ]),
        dbc.Row([
            dbc.Col(project_file_category()),
            dbc.Col(project_file_type())
        ]),
        dbc.Row([
            dbc.Col(project_file_type_extension()),
            dbc.Col(project_file_type_extension_per_file_category())
        ])
    ],
    fluid=True,
)

@app.callback(
    Output('singer-projects-graph', 'children'),
    Input('singer-dropdown', 'value')
)
def singer_projects_by_language_graph(selected_singer):
    df = fetch_data("""
        SELECT
            s.name,
            po.title,
            po.language
        FROM
            singers s
        JOIN
            project_singer_association psa ON s.id = psa.singer_id
        JOIN
            project_observations po ON psa.project_observation_id = po.id
        WHERE s.is_active = po.is_active AND s.name <> 'scraper'
    """)
    df = df.groupby(['name', 'language'])['title'].count().reset_index()
    df.columns = ['name', 'language', 'project_count']
    # df['language_label'] = df['language'].apply(
    #     lambda lang: f"{lang} ({df.groupby('language')['project_count'].sum().to_dict()[lang]})"
    # )
    df = df[df['name'] == selected_singer]

    fig = go.Figure(
        data=[
            go.Bar(
                x=df['language'],
                # x=df['language_label'],
                y=df['project_count'],
                text=df['project_count'],
                marker=dict(
                    color=list(range(len(df['language'].values))),
                )
            )
        ]
    )

    fig.update_layout(
        title=f"Projets interprétés par {selected_singer  if selected_singer else 'No One'}",
        xaxis_title='Langue',
        # xaxis_title='Langue (total global)',
        yaxis_title='Nombre de projets',
        annotations=[
            dict(
                text=f"Total: {df['project_count'].sum()}",
                x=1,
                y=1.1,
                xref='paper',
                yref='paper',
                showarrow=False,
                font=dict(size=14),
                align='right'
            )
        ]
    )
    return dcc.Graph(figure=fig, config={'responsive': False})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
    # app.run(debug=True, host="localhost", port=3000)