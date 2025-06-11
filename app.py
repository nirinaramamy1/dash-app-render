import dash
from dash import html

app = dash.Dash(__name__)
server = app.server  # Important for Render

app.layout = html.Div("Hello from Dash on Render!")

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=10000)
