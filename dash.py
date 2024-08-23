import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df = pd.read_csv('games.csv')
df = df[(df['Year_of_Release'] >= 2000) & (df['Year_of_Release'] <= 2022)]
df = df.dropna()
df = df[pd.to_numeric(df['User_Score'], errors='coerce').notnull()]
df = df[pd.to_numeric(df['Critic_Score'], errors='coerce').notnull()]
df['User_Score'] = df['User_Score'].astype(float)
df['Critic_Score'] = df['Critic_Score'].astype(float)

app.layout = html.Div([
    html.H1("Дашборд игровой индустрии"),

    dcc.Dropdown(
        id='platform-filter',
        options=[{'label': platform, 'value': platform} for platform in df['Platform'].unique()],
        multi=True,
        placeholder="Выберите платформы"
    ),
    dcc.Dropdown(
        id='genre-filter',
        options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
        multi=True,
        placeholder="Выберите жанры"
    ),
    dcc.RangeSlider(
        id='year-filter',
        min=2000,
        max=2022,
        marks={i: str(i) for i in range(2000, 2023)},
        value=[2000, 2022]
    ),

    html.Div([
        html.Div([
            dcc.Graph(id='total-games-bar-chart'),
            html.P(id='total-games-label')
        ], style={'flex': 1, 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='avg-user-score-bar-chart'),
            html.P(id='avg-user-score-label')
        ], style={'flex': 1, 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='avg-critic-score-bar-chart'),
            html.P(id='avg-critic-score-label')
        ], style={'flex': 1, 'padding': '10px'})
    ], style={'display': 'flex'}),

    dcc.Graph(id='area-plot'),

    dcc.Graph(id='scatter-plot'),
    dcc.Graph(id='bar-line-chart')
])


@app.callback(
    [Output('total-games-bar-chart', 'figure'),
     Output('avg-user-score-bar-chart', 'figure'),
     Output('avg-critic-score-bar-chart', 'figure'),
     Output('total-games-label', 'children'),
     Output('avg-user-score-label', 'children'),
     Output('avg-critic-score-label', 'children'),
     Output('area-plot', 'figure'),
     Output('scatter-plot', 'figure'),
     Output('bar-line-chart', 'figure')],
    [Input('platform-filter', 'value'),
     Input('genre-filter', 'value'),
     Input('year-filter', 'value')]
)
def update_dashboard(platforms, genres, years):
    filtered_df = df[(df['Year_of_Release'] >= years[0]) & (df['Year_of_Release'] <= years[1])]

    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]

    total_games = len(filtered_df)
    avg_user_score = round(filtered_df['User_Score'].mean(), 2)
    avg_critic_score = round(filtered_df['Critic_Score'].mean(), 2)

    total_games_bar_chart = px.bar(x=['Общее число игр'], y=[total_games], title="Общее число игр")

    avg_user_score_bar_chart = px.bar(x=['Средняя оценка игроков'], y=[avg_user_score], title="Средняя оценка игроков")

    avg_critic_score_bar_chart = px.bar(x=['Средняя оценка критиков'], y=[avg_critic_score],
                                        title="Средняя оценка критиков")

    total_games_label = f"Всего игр: {total_games}"
    avg_user_score_label = f"Средняя оценка игроков: {avg_user_score}"
    avg_critic_score_label = f"Средняя оценка критиков: {avg_critic_score}"

    games_per_year_platform = filtered_df.groupby(['Year_of_Release', 'Platform']).size().reset_index(name='Game_Count')

    area_plot = px.area(games_per_year_platform, x='Year_of_Release', y='Game_Count', color='Platform',
                        title="Выпуск игр по годам и платформам")
    area_plot = area_plot.data

    scatter_plot = px.scatter(filtered_df, x='User_Score', y='Critic_Score', color='Genre',
                              title="Соотношение оценок игроков и критиков по жанрам",
                              color_discrete_sequence=px.colors.qualitative.Set3)

    bar_line_chart = px.bar(filtered_df.groupby('Genre')['User_Score'].mean().reset_index(),
                            x='Genre', y='User_Score', title="Средняя оценка игроков по жанрам",
                            color='Genre', color_discrete_sequence=px.colors.qualitative.Set3)

    return (
        total_games_bar_chart,
        avg_user_score_bar_chart,
        avg_critic_score_bar_chart,
        total_games_label,
        avg_user_score_label,
        avg_critic_score_label,
        {'data': area_plot},
        scatter_plot,
        bar_line_chart
    )


if __name__ == '__main__':
    app.run_server(debug=True)
