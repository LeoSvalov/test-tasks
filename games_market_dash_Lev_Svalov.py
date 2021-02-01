import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

external_stylesheets = [dbc.themes.YETI]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



########################     DATA preprocessing    ########################

df = pd.read_csv('data/games.csv', index_col=0, parse_dates=True)

# drop rows where NaN exists
df = df.dropna()


'''
Remark about dataset:

I discover that a few rows in the column 'User_Score' (assumed to be numeric value) have the value 'tbd'( = To be determined, I suppose),
but majority has numeric score. Since this column is used as one of axis of the scatter plot, it will need to be sorted,
because it will not be fully correct graph if on the axis some smaller score will be on the right with respect to the bigger value.
So, I see 2 ways to deal with it
 1) either consider this 'tbd' as NaN and drop such rows as well 
 2) or assign some average user score to these rows and proceed with the scatter plot 

In my further solution, I've taken the first option and dropped the rows with 'tbd' User Score for having proper scatter plot.
'''

# search all rows with 'tbd' User Score and drop them too 
indexNames = df[df['User_Score'] == 'tbd' ].index
df.drop(indexNames , inplace=True)

# convert User Score column to numeric datatype
df["User_Score"] = pd.to_numeric(df["User_Score"])

# games should be released not earlier than in 2000
df_filtered = df[df['Year_of_Release'] >= 2000] 

###########################################################################

# data needed to setup dashboard components
genres = df_filtered['Genre'].unique()
ratings = df_filtered['Rating'].unique()
years = np.sort(df_filtered['Year_of_Release'].unique()).astype(int)


# components
hello_component = html.Div(
    [
        html.H1(children='Games market dashboard'),
        html.Div(children=['''The dashboard with a brief games market analysis.''',html.Br(),
                         '''Filter the games according to its genre, age rating and the year of release.''']),
    ],
    style={ 'border-bottom': '2px solid black',
            'margin': '50px',
            'marginBottom':50 }
)

filters_row = html.Div(
    dbc.Row(
        [
            dbc.Col(
                [
                dcc.Markdown('''**Filter 1**: Choose genre'''),  
                dcc.Dropdown(
                    id='genre-filter',
                    options=[{'label':genre, 'value':genre} for genre in genres],
                    searchable=True,
                    multi=True,
                    value=[]
                )
                ], 
                width=6, 
            ), 
            dbc.Col(
                [
                dcc.Markdown('''**Filter 2**: Choose age rating'''),  
                dcc.Dropdown(
                    id='rating-filter',
                    options=[{'label':rating, 'value':rating} for rating in ratings],
                    searchable=True,
                    multi=True,
                    value=[]

                )
                ], 
                width=6, 
            ), 
        ]
    ),
    style={ 'width': '90%',
            'margin': '50px' }
)

interval_row = html.Div(
    [
        html.Div(dcc.Markdown('''**Filter 3**: Choose time interval of release year'''),
                 style= {'marginLeft':50,'marginRight':50}
                ),  
        html.Div(
            dcc.RangeSlider(
            id='year-filter',
            min=years[0],
            max=years[-1],
            step=1,
            value=[years[0],years[-1]],
            marks={str(year.item()): str(year.item()) for year in years},
            ),
            style= {'marginLeft':100,'marginRight':100}
            )
    ]
)

output_row = html.Div(
    dbc.Row(
        [
        dbc.Col(dcc.Markdown('''**The number of filtered games:**'''),width="auto"),  
        dbc.Col(html.H5(id='number-output'),width="auto")
        ]
    ),
    style= {'marginLeft':50}
)

graph_row = html.Div(
    dbc.Row(
        [
        dcc.Graph(id='stack-graph'), 
        dcc.Graph(id='scatter-graph')
        ]
    ),
    style={ 'width': '100%',
            'marginLeft':50,'marginRight':50
          }
)

# combining components in layot of the dashboard
app.layout = html.Div(children=[hello_component,filters_row,output_row,graph_row,interval_row])


# Plots
'''
    Functions which define figures to plot. Used in callback
'''
def scatter_figure(games):
    games = games.sort_values(by=['User_Score'])
    fig = px.scatter(games, x="User_Score", y="Critic_Score", color="Genre", title='The correlation of the Critic & User scores and genres', 
                    labels={"User_Score": "User score",
                            "Critic_Score": "Critic score"})
    fig.update_layout(transition_duration=100)
    return fig

def stack_figure(games):
    chosen_genres = games['Genre'].unique()
    platforms = games['Platform'].unique()
    fig = go.Figure()
    for genre in chosen_genres:
        one_genre_games = games[games['Genre']==genre]
        y = [len(one_genre_games[one_genre_games['Platform']==platform]) for platform in platforms]
        fig.add_trace(go.Scatter( 
            name = genre, 
            x = platforms, 
            y = y, 
            stackgroup='one',
            groupnorm='percent'
        ))
    fig.update_layout(
        title="The interrelation between the platforms and genres",
        xaxis_title="Platform",
        yaxis_title="Percentage (%)",
        legend_title="Genre", 
    )
    return fig 

# Callback
'''
    The dashboard has 3 input filters that impact 3 output components: 
    2 plots and the frame with number of selected games.
    Filter the dataframe 'games' according to the given input and return the output
'''
@app.callback(
    [Output(component_id='number-output', component_property='children'),
     Output(component_id='stack-graph', component_property='figure'),
     Output(component_id='scatter-graph', component_property='figure')
    ],
    [Input(component_id='genre-filter', component_property='value'),
     Input(component_id='rating-filter', component_property='value'),
     Input(component_id='year-filter', component_property='value'),
    ]
)
def output(genre_list, rating_list, year_interval):
    if len(genre_list)==0 or len(rating_list)==0: return [0, px.scatter(title="Empty plot"), px.scatter(title="Empty plot")]
    games = df_filtered[df_filtered['Year_of_Release']>=year_interval[0]]
    games = games[games['Year_of_Release']<=year_interval[1]]
    games = games[games['Genre'].isin(genre_list)]
    games = games[games['Rating'].isin(rating_list)]

    if games.empty: return [0, px.scatter(title="Empty plot"), px.scatter(title="Empty plot")]
    else: return [len(games),stack_figure(games), scatter_figure(games)]


if __name__ == '__main__':
    app.run_server(debug=True)
