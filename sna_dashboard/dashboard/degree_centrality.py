from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import matplotlib.colors as mcolors

dash_app = None
dataset = None

def initialize_degree_centrality_app(dash_app_instance, dataset_instance):
    global dash_app, dataset
    dash_app = dash_app_instance
    dataset = dataset_instance

    dash_app.layout.children.append(html.Div([
        html.H1("Degree Centrality"),
        html.Div([
            dcc.Dropdown(
                id='degree-centrality-project-dropdown',
                options=[{'label': f'Project {i}', 'value': i} for i in dataset['project'].unique()],
                placeholder="Select projects",
                multi=True,
                style={'width': '200px'}
            ),
            dcc.Dropdown(
                id='degree-centrality-meeting-dropdown',
                placeholder="Select meetings",
                multi=True,
                style={'width': '200px'}
            ),
            dcc.Dropdown(
                id='degree-centrality-speaker-dropdown',
                placeholder="Select speakers",
                multi=True,
                style={'width': '200px'}
            ),
            html.Button('Reset', id='reset-degree-centrality-button', n_clicks=0)
        ], style={'display': 'flex', 'gap': '10px', 'flexWrap': 'wrap'}),
        dcc.Graph(id='degree-centrality-graph')
    ]))

    @dash_app.callback(
        [Output('degree-centrality-project-dropdown', 'value'),
         Output('degree-centrality-meeting-dropdown', 'value'),
         Output('degree-centrality-speaker-dropdown', 'value')],
        [Input('reset-degree-centrality-button', 'n_clicks')]
    )
    def reset_degree_centrality_filters(n_clicks):
        return [], [], []

    @dash_app.callback(
        Output('degree-centrality-meeting-dropdown', 'options'),
        [Input('degree-centrality-project-dropdown', 'value')]
    )
    def set_meeting_options(selected_projects):
        if not selected_projects:
            return []
        filtered_df = dataset[dataset['project'].isin(selected_projects)]
        meetings = filtered_df['meeting_number'].unique()
        return [{'label': f'Meeting {i}', 'value': i} for i in meetings]

    @dash_app.callback(
        Output('degree-centrality-speaker-dropdown', 'options'),
        [Input('degree-centrality-project-dropdown', 'value'),
         Input('degree-centrality-meeting-dropdown', 'value')]
    )
    def set_speaker_options(selected_projects, selected_meetings):
        if not selected_projects:
            return []
        filtered_df = dataset[dataset['project'].isin(selected_projects)]
        if selected_meetings:
            filtered_df = filtered_df[filtered_df['meeting_number'].isin(selected_meetings)]
        speakers = filtered_df['speaker_number'].unique()
        return [{'label': f'Speaker {i}', 'value': i} for i in speakers]

    @dash_app.callback(
        Output('degree-centrality-graph', 'figure'),
        [Input('degree-centrality-project-dropdown', 'value'),
         Input('degree-centrality-meeting-dropdown', 'value'),
         Input('degree-centrality-speaker-dropdown', 'value')]
    )
    def update_degree_centrality_graph(selected_projects, selected_meetings, selected_speakers):
        filtered_df = dataset

        if selected_projects:
            filtered_df = filtered_df[filtered_df['project'].isin(selected_projects)]

        if selected_meetings:
            filtered_df = filtered_df[filtered_df['meeting_number'].isin(selected_meetings)]

        if selected_speakers:
            filtered_df = filtered_df[filtered_df['speaker_number'].isin(selected_speakers)]

        if not selected_projects and not selected_meetings and not selected_speakers:
            fig = go.Figure()
            fig.update_layout(
                title='Degree Centrality by Meeting and Speaker',
                xaxis_title='Meeting Number',
                yaxis_title='Degree Centrality',
                showlegend=True
            )
            return fig

        if selected_meetings:
            bar_data = filtered_df.groupby(['meeting_number', 'speaker_number'])['degree_centrality'].sum().reset_index()
            colorscale = mcolors.LinearSegmentedColormap.from_list('blue_red', ['blue', 'red'])
            bar_colors = bar_data['degree_centrality'].apply(lambda x: mcolors.rgb2hex(colorscale(x / bar_data['degree_centrality'].max())))

            fig = go.Figure(data=[go.Bar(
                x=bar_data['speaker_number'],
                y=bar_data['degree_centrality'],
                marker_color=bar_colors
            )])
            fig.update_layout(
                title=f'Degree Centrality for Selected Meetings',
                xaxis_title='Speaker Number',
                yaxis_title='Degree Centrality',
                showlegend=False
            )

            color_bar = go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(
                    colorscale=[[0, 'blue'], [1, 'red']],
                    cmin=0,
                    cmax=bar_data['degree_centrality'].max(),
                    colorbar=dict(
                        title="Degree Centrality",
                        titleside="right"
                    )
                ),
                hoverinfo='none'
            )
            fig.add_trace(color_bar)
            return fig
        else:
            fig = go.Figure()
            for speaker in filtered_df['speaker_number'].unique():
                speaker_df = filtered_df[filtered_df['speaker_number'] == speaker]
                fig.add_trace(go.Scatter(x=speaker_df['meeting_number'],
                                         y=speaker_df['degree_centrality'],
                                         mode='lines+markers',
                                         name=f'Speaker {speaker}'))
            fig.update_layout(
                title='Degree Centrality by Meeting and Speaker',
                xaxis_title='Meeting Number',
                yaxis_title='Degree Centrality',
                showlegend=True
            )
            return fig