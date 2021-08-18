import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
from front_end import navbar
from api_devolutivas.cache import Cache
from api_devolutivas.api_client import ClientDevolutivas
from geo_utils import Regionalizador

SHP_PATH = 'map_data/mapa_subprefeituras/SIRGAS_SHP_subprefeitura_polygon.shp'
CACHE = Cache()
API_CLIENT = ClientDevolutivas(cache=CACHE)
REGIONALIZAR = Regionalizador(SHP_PATH)

def gerar_geodf(cathegory_name):

    DADOS = API_CLIENT.get_all_contribs_by_type('categorias')
    geodf = REGIONALIZAR(DADOS, cathegory_name)

    return geodf

def gerar_mapa(geodf):

    fig = px.choropleth(
        geodf,
        geojson=geodf.geometry,
        locations=geodf.index,
        color = 'Percentual',
        color_continuous_scale = 'Blues'
        )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=1000, height=400)

    return fig

external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Regionalização Devolutivas PDM 21-24'
server = app.server

app.layout = html.Div([
    navbar,
    html.P("Tema:"),
    dcc.Dropdown(
        id='tema', 
        options=[{'value': x['nome'], 'label': x['nome']} 
                 for x in API_CLIENT.categorias],
        value=API_CLIENT.categorias[0]['nome'],
    ),
    dcc.Graph(id="choropleth"),
])

@app.callback(
    Output("choropleth", "figure"), 
    [Input("tema", "value")])
def display_choropleth(tema):

    geodf = gerar_geodf(tema)
    fig = gerar_mapa(geodf)

    return fig

if __name__ == "__main__":

    app.run_server(debug=True)