import pandas as pd
pd.set_option('max_rows',20)
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"
import requests
import datetime as dt

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


url="https://covid19.who.int/WHO-COVID-19-global-data.csv"
who_dat=pd.read_csv(url)
# who_dat[['Date','Last']] = who_dat.Date_reported.str.split("T",expand=True)
# who_dat = who_dat.drop(['Last','Date_reported'], axis=1)
cols = ['Date_reported', 'Country_code', 'Country', 'WHO_region','New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']
who_dat.columns = cols
who_dat = who_dat[['Date_reported','Country_code','Country','WHO_region','New_cases','Cumulative_cases','New_deaths','Cumulative_deaths']]

pop_dat=pd.read_csv('Population by Country.csv',engine='python')
pop_dat = pop_dat[['Country (or dependency)', 'Population (2020)']]
cols = ['Country', 'Population_2020']
pop_dat.columns = cols
df_fin = pd.merge(who_dat,pop_dat, on = 'Country',how = 'inner')
df_fin['Date_reported'] = pd.to_datetime(df_fin['Date_reported'],format="%Y/%m/%d",errors='raise')
url = 'https://www.nationsonline.org/oneworld/country_code_list.htm'
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}
r = requests.get(url, headers=header)
dfs = pd.read_html(r.text,skiprows=1)[0]
cols = ['misc_1','misc_2','Country_code','iso_code','misc_3']
dfs.columns = cols
dfs = dfs[['Country_code','iso_code']]
df_fin = pd.merge(df_fin,dfs,on = 'Country_code',how='left')

# Worldwide Analysis

df_maxdate = df_fin.loc[df_fin.groupby('Country')['Date_reported'].idxmax()]
worldwide_total_cases = df_maxdate.Cumulative_cases.sum()
worldwide_total_deaths = df_maxdate.Cumulative_deaths.sum()
total_world_population = df_maxdate.Population_2020.sum()
worldwide_mortality_rate = (worldwide_total_deaths/worldwide_total_cases)*100
worldwide_mortality_rate = float("{:.3f}".format(worldwide_mortality_rate))
worldwide_cases_per_million = (worldwide_total_cases/total_world_population)*1000000
worldwide_deaths_per_million = (worldwide_total_deaths/total_world_population)*1000000

# Countrywise Analysis

def get_cntry_total_cases(df_maxdate,cntry='United States of America'):
    return df_maxdate[df_maxdate['Country']==cntry].iloc[0,5]
def get_cntry_total_deaths(df_maxdate,cntry='United States of America'):
    return df_maxdate[df_maxdate['Country']==cntry].iloc[0,7]
def get_cntry_total_population(df_maxdate,cntry='United States of America'):
    return df_maxdate[df_maxdate['Country']==cntry].iloc[0,8]
def get_firstdate(df_fin,cntry='United States of America'):
    df_fin_cntry = df_fin[df_fin['Country'] == cntry]
    df_fin_cntry.reset_index(drop=True, inplace=True)
    df_firstdate = df_fin_cntry.Date_reported.iloc[0].date()
    return df_firstdate


cntry='United States of America'
countrywise_total_cases = get_cntry_total_cases(df_maxdate,cntry)
countrywise_total_deaths = get_cntry_total_deaths(df_maxdate,cntry)
total_country_population = get_cntry_total_population(df_maxdate,cntry)
countrywise_mortality_rate = (countrywise_total_deaths/countrywise_total_cases)*100
countrywise_mortality_rate = float("{:.3f}".format(countrywise_mortality_rate))
countrywise_cases_per_million = (countrywise_total_cases/total_country_population)*1000000
countrywise_deaths_per_million = (countrywise_total_deaths/total_country_population)*1000000
firstdate = get_firstdate(df_fin,cntry)


def fig_world_trend(cntry='United States of America'):
    df = df_fin[df_fin['Country']==cntry]
    fig = px.line(df, y='New_cases', x='Date_reported', title='Daily confirmed cases trend for {}'.format(cntry),height=600,color_discrete_sequence =['Purple'])
    fig.update_layout(title_x=0.5,plot_bgcolor='#F2DFCE',paper_bgcolor='#F2DFCE',xaxis_title="Date",yaxis_title='Daily confirmed cases')
    return fig
                  
def world_map():
    df_maxdate = df_fin.loc[df_fin.groupby('Country')['Date_reported'].idxmax()]
    fig = px.choropleth(df_maxdate, locations="iso_code",
                    color="Cumulative_cases",
                    hover_name="Country",
                    color_continuous_scale=px.colors.sequential.Plasma,
                       title='Worldwide Covid-19 total cases Trend',height=600)
    fig.update_layout(title_x=0.5,plot_bgcolor='#F2DFCE',paper_bgcolor='#F2DFCE')
    return fig

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'COVID-19 Data Visuals'

colors = {
    'background': '#111111',
    'bodyColor':'#F2DFCE',
    'text': '#7FDBFF'
}
def get_page_heading_style():
    return {'backgroundColor': colors['background']}


def get_page_heading_title():
    return html.H1(children='COVID-19 Data Visuals',
                                        style={
                                        'textAlign': 'center',
                                        'color': colors['text']
                                    })

def get_page_heading_subtitle():
    return html.Div(children='Visualize Covid-19 data countrywise.',
                                         style={
                                             'textAlign':'center',
                                             'color':colors['text']
                                         })

def generate_page_header():
    main_header =  dbc.Row(
                            [
                                dbc.Col(get_page_heading_title(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    subtitle_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_subtitle(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    header = (main_header,subtitle_header)
    return header


def get_country_list():
    return df_fin['Country'].unique()

def create_dropdown_list(cntry_list):
    dropdown_list = []
    for cntry in sorted(cntry_list):
        tmp_dict = {'label':cntry,'value':cntry}
        dropdown_list.append(tmp_dict)
    return dropdown_list

def get_country_dropdown(id):
    return html.Div([
                        html.Label('Select Country'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=create_dropdown_list(get_country_list()),
                            value='United States of America'
                        ),
                        html.Div(id='my-div'+str(id))
                    ])


def graph1():
    return dcc.Graph(id='graph1',figure=fig_world_trend('United States of America'))

def graph2():
    return dcc.Graph(id='graph2',figure=world_map())

def generate_card_content(card_header,card_value,overall_value):
    card_head_style = {'textAlign':'center','fontSize':'100%'}
    card_body_style = {'textAlign':'center','fontSize':'150%'}
    card_header = dbc.CardHeader(card_header,style=card_head_style)
    card_body = dbc.CardBody(
        [
            html.H5(f"{int(card_value):,}", className="card-title",style=card_body_style),
            html.P(
                "Worlwide: {:,}".format(overall_value),
                className="card-text",style={'textAlign':'center'}
            ),
        ]
    )
    card = [card_header,card_body]
    return card

def generate_cards(cntry='United States of America'):
    countrywise_total_cases = get_cntry_total_cases(df_maxdate,cntry)
    countrywise_total_deaths = get_cntry_total_deaths(df_maxdate,cntry)
    countrywise_mortality_rate = (countrywise_total_deaths/countrywise_total_cases)*100
    countrywise_mortality_rate = float("{:.3f}".format(countrywise_mortality_rate))
    cards = html.Div(
        [
            dbc.Row(children=
                [ 
                    dbc.Col(dbc.Card(generate_card_content("Total Cases",countrywise_total_cases,worldwide_total_cases), 
                                     color="warning", inverse=True),md=dict(size=2,offset=3),style={'display': 'inline-block'}),
                    dbc.Col(dbc.Card(generate_card_content("Fatalities",countrywise_total_deaths,worldwide_total_deaths), 
                                     color="dark", inverse=True),md=dict(size=2),style={'display': 'inline-block'}),
                    dbc.Col(dbc.Card(generate_card_content("Mortality Rate (%)",countrywise_mortality_rate,worldwide_mortality_rate),
                                     color="success", inverse=True),md=dict(size=2),style={'display': 'inline-block'}),
                ],
                className="mb-4",
            ),
        ],id='card1'
    )
    return cards

def generate_layout():
    page_header = generate_page_header()
    layout = dbc.Container(
        [
            page_header[0],
            page_header[1],
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(get_country_dropdown(id=1),md=dict(size=4,offset=2))                    
                ]
            
            ),
            html.Hr(),
            html.Div(children= [html.P(id = 'text-1', children = 'Coronaviruses (CoV) are a large family of viruses that cause illness ranging from the common cold to more severe diseases such as Middle East Respiratory Syndrome (MERS-CoV) and Severe Acute Respiratory Syndrome (SARS-CoV). A novel coronavirus (nCoV) is a new strain that has not been previously identified in humans.'),
                     html.P(id = 'text-2', children = 'Coronaviruses are zoonotic, meaning they are transmitted between animals and people. Detailed investigations found that SARS-CoV was transmitted from civet cats to humans and MERS-CoV from dromedary camels to humans. Several known coronaviruses are circulating in animals that have not yet infected humans. Common signs of infection include respiratory symptoms, fever, cough, shortness of breath and breathing difficulties. In more severe cases, infection can cause pneumonia, severe acute respiratory syndrome, kidney failure and even death.'),
                     html.P(id = 'text-3', children = 'Standard recommendations to prevent infection spread include regular hand washing, covering mouth and nose when coughing and sneezing, thoroughly cooking meat and eggs. Avoid close contact with anyone showing symptoms of respiratory illness such as coughing and sneezing.')]
            ),
            html.Hr(),
            generate_cards(),
            html.Hr(),
            dbc.Row(
                [                
                    
                    dbc.Col(graph2(),md=dict(size=6,offset=3))
        
                ],
                align="center",

            ),
            html.Hr(),
            dbc.Row(
                [                
                    
                    dbc.Col(graph1(),md=dict(size=6,offset=3))
        
                ],
                align="center",

            )
            
        ],fluid=True,style={'backgroundColor': colors['bodyColor']}
    )
    return layout

app.layout = generate_layout()

@app.callback(
    [Output(component_id='graph1',component_property='figure'), #line chart
    Output(component_id='card1',component_property='children')], #overall card numbers
    [Input(component_id='my-id1',component_property='value')] #dropdown
)
def update_output_div(input_value1):
    return fig_world_trend(input_value1),generate_cards(input_value1)
     
app.run_server(debug=True)


