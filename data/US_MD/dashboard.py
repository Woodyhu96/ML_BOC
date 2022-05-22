
from tkinter.messagebox import NO
from dash import dcc, html, Dash, Input, Output, dash_table
from matplotlib.pyplot import title
import pandas as pd
import plotly.express as px
from DataModel import TimeSeriesModel
import plotly.graph_objects as go


# Load the dataset
datasets = {
    'US': pd.read_csv('./MicroML/data/US_MD/US_MD.csv')[1:]
}
datasets['US'].rename(columns={'sasdate': 'Date'}, inplace=True)

feature_options = ['Industrial Production',
                   'CPI Inflation', 'Unemployment Rate']
grouping_options = ['Output and income','labor market','housing','consumption, orders and inventories', 
                    'money and credit', 'bond and exchange rates', 'prices','stock market']
choice_options = ['Feature', 'Group']
AllinOne = ['Show all']
map_feature_options = {
    'US': {
        'Industrial Production': '^IP|INDPRO',
        'CPI Inflation': '^CPI',
        'Unemployment Rate': '^UEMP',
    }
}
map_grouping_options ={
    'US':{
        'Output and income':'RPI|W875RX1|INDPRO|^IP|NAPMPI|CUMFNS',
        'labor market': '^HW|CLF16OV|CE16OV|UNRATE|^UEMP|CLAIMSx|PAYEMS|USGOOD|^CES|^US|MANEMP|DMANEMP|NDMANEMP|SRVPRD|^AW|NAPMEI',
        'housing':'^HOUST|^PERM',
        'consumption, orders and inventories':'DPCERA3M086SBEA|CMRMTSPLx|RETAILx|^NAPM|ACOGNO|^AMD|BUSINVx|ISRATIOx|UMCSENTx', 
        'money and credit':'M1SL|M2SL|M2REAL|AMBSL|TOTRESNS|NONBORRES|BUSLOANS|REALLN|NONREVSL|CONSPI|MZMSL|^DTC|INVEST', 
        'bond and exchange rates':'FEDFUNDS|CP3Mx|^TB|^GS|^AAA|^BAA|COMPAPFFx|T1YFFM|T5YFFM|T10YFFM|TWEXMMTH|^EX', 
        'prices':'^PPI|OILPRICEx|NAPMPRI|^CPI|^CU|PCEPI|DDURRG3M086SBEA|DNDGRG3M086SBEA|DSERRG3M086SBEA',
        'stock market':'^S&P'
    }
}


# Create the Dash app
app = Dash(__name__)

# select a dataset
radio_btn_dataset = html.Div([
    html.Label("Select a dataset"),
    dcc.RadioItems(
        id="radio-dataset",
        options=[{'label': key, 'value': key} for key in datasets.keys()],
        value=next(iter(datasets.keys()))
    ),
    html.Br()
]
)

#show all button
showall_btn = html.Div([
    html.Label("Show all graph"),
    dcc.RadioItems(
        id="showall_button",
        options=AllinOne,
        value=AllinOne[0]
    ),
    html.Br()
]
)

#add mode choice button to switch between grouping view and feature view
mode_btn_choices = html.Div([
    html.Label("Mode"),
    dcc.RadioItems(
        id="feature-grouping-choices",
        options=choice_options,
        value=choice_options[0]
    ),
    html.Br()
]
)

#choose from different features
radio_btn_choices = html.Div([
    html.Label("Feature Category"),
    dcc.RadioItems(
        id="radio-category-feature-options",
        options=feature_options,
        value=feature_options[0]
    ),
    html.Br()
]
)

#choose from different groups
radio_btn_choices_group = html.Div([
    html.Label("Group Category"),
    dcc.RadioItems(
        id="radio-category-grouping-options",
        options=grouping_options,
        value=grouping_options[0]
    ),
    html.Br()
]
)

# select groups based on regex result
dropdown_group = html.Div([
    html.Label('Dropdown Group'),
    dcc.Dropdown(id="dropdown-group", multi=True),
    html.Br()
]
)

# select features based on regex result
dropdown_feature = html.Div([
    html.Label('Dropdown Feature'),
    dcc.Dropdown(id="dropdown-feature", multi=True),
    html.Br()
]
)

adf_result = html.Div([
    dash_table.DataTable(
        id='adf-result',
        columns=[
            {'name': 'Feature', 'id': 'Feature',
             'type': 'text', 'editable': False},
            {'name': 'ADF-Stat', 'id': 'ADF-Stat', 'type': 'numeric'},
            {'name': 'p-value', 'id': 'p-value', 'type': 'numeric'},
            {'name': '1%-Critical', 'id': '1%-Critical', 'type': 'numeric'},
            {'name': '5%-Critical', 'id': '5%-Critical', 'type': 'numeric'},
            {'name': '10%-Critical', 'id': '10%-Critical', 'type': 'numeric'},
        ],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{p-value} > 0.05',
                },
                'backgroundColor': 'tomato',
                'color': 'white'
            }
        ]
    ),
    html.Br()
])

plot_feature = html.Div([
    dcc.Graph(
        id='feature-line'
    ),
    html.Br(),
    adf_result
],  style={'width': '45%', 'display': 'inline-block'})

summary_plot = html.Div([
    dcc.Graph(
        id='summary-line'
    ),
    html.Br(),
],  style={'width': '45%', 'display': 'inline-block'})

plot_autocorrelation = html.Div([
    html.Div(id='container-acf', children=[
        dcc.RadioItems(
            id='radio-acf',
            inline=True
        ),
        dcc.Graph(id='acf'),
        dcc.Slider(0, 50, 5,
                   value=50,
                   id='acf-slider'
                   )
    ]),
    html.Div(id='container-pacf', children=[
        dcc.RadioItems(
            id='radio-pacf',
            inline=True
        ),
        dcc.Graph(id='pacf'),
        dcc.Slider(0, 50, 5,
                   value=50,
                   id='pacf-slider'
                   )
    ])
], style={'display': 'inline-block', 'width': '45%', 'padding-left': '5%'})


app.layout = html.Div(children=[
    radio_btn_dataset,
    mode_btn_choices,
    showall_btn,
    radio_btn_choices,
    radio_btn_choices_group,
    dropdown_feature,
    dropdown_group,
    plot_autocorrelation,
    plot_feature,
    summary_plot,
]
)

def get_filtered_data(dataset_key, selected_feature, time_col='Date') -> pd.DataFrame:
    dataset = datasets[dataset_key]
    date = pd.PeriodIndex(data=dataset[time_col], freq='M')
    dataset[time_col] = date
    data = pd.DataFrame(dataset, columns=[time_col, selected_feature])
    return data

###################################################################################################
# plot lines

@app.callback(
    Output('feature-line', 'figure'),
    Input('radio-dataset', 'value'),
    Input('dropdown-feature', 'value'),
    Input('dropdown-group', 'value'),
    Input('feature-grouping-choices','value')

)
def update_graph(dataset_key, selected_features,selected_group,mode):
    fig = go.Figure()
    if mode == 'Feature':
        for feature in selected_features:
            data = get_filtered_data(dataset_key, feature)
            model = TimeSeriesModel(data)
            fig.add_trace(go.Scatter(x=model.data['Date'].astype(str),
                                    y=model.data[feature], mode='lines', name=feature))
        fig.update_layout(
            title_text=f'Feature Index growth over years', title_x=0.5)
    else:
        for feature in selected_group:
            data = get_filtered_data(dataset_key, feature)
            model = TimeSeriesModel(data)
            fig.add_trace(go.Scatter(x=model.data['Date'].astype(str),
                                    y=model.data[feature], mode='lines', name=feature))
        fig.update_layout(
            title_text=f'Feature Index growth over years', title_x=0.5)
    return fig
###################################################################################################
# adding show all graph feature
@app.callback(
    Output('summary-line', 'figure'),
    Input('radio-dataset', 'value'),
    Input('radio-category-feature-options', 'value'),
    Input('radio-category-grouping-options','value'),
    Input('showall_button', 'value'),
    Input('feature-grouping-choices','value')
)
def update_summary_graph(dataset_key,category_feature,category_group,showall,mode):
    fig = go.Figure()
    dataset = datasets[dataset_key]
    if mode == 'Feature':
        regex = map_feature_options[dataset_key][category_feature]
        dataset = dataset.filter(regex=regex).columns    
    else:
        regex = map_grouping_options[dataset_key][category_group]
        dataset = dataset.filter(regex=regex).columns    
    if showall == 'Show all':
        for i in dataset:
            data = get_filtered_data(dataset_key, i)
            model = TimeSeriesModel(data)
            fig.add_trace(go.Scatter(x=model.data['Date'].astype(str),
                                    y=model.data[i], mode='lines', name=i))        

    return fig


###################################################################################################
# filter features under feature category(ie. Industrial production, unemployment rate)

@app.callback(
    Output('dropdown-feature', 'options'),
    Input('radio-dataset', 'value'),
    Input('radio-category-feature-options', 'value')
)
def update_feature_dropdown(dataset_key,category_option):

    dataset = datasets[dataset_key]
    regex = map_feature_options[dataset_key][category_option]
    return dataset.filter(regex=regex).columns
########################################################################################

# Filter features under group category(i.e. Output and income','labor market','housing')

@app.callback(
    Output('dropdown-group', 'options'),
    Input('radio-dataset', 'value'),
    Input('radio-category-grouping-options', 'value')
)
def update_group_dropdown(dataset_key,category_option):
    dataset = datasets[dataset_key]
    regex = map_grouping_options[dataset_key][category_option]
    return dataset.filter(regex=regex).columns
###################################################################################################

@app.callback(
    Output('radio-acf', 'options'),
    Input('dropdown-feature', 'value'),
    Input('dropdown-group','value'),
    Input('feature-grouping-choices','value')
)
def update_radio_acf_feature(selected_feature,selected_group,mode):
    if mode == 'Feature':
        selected = selected_feature
    else:
        selected = selected_group
    return [{'label': feature, 'value': feature} for feature in selected]

###################################################################################################

@app.callback(
    Output('acf', 'figure'),
    Input('radio-dataset', 'value'),
    Input('radio-acf', 'value'),
    Input('acf-slider', 'value')
)
def update_acf(dataset_key, selected_feature, lag):
    data = get_filtered_data(dataset_key, selected_feature)

    model = TimeSeriesModel(data)

    return model.create_corr_plot(lag)

###################################################################################################


@app.callback(
    Output('radio-pacf', 'options'),
    Input('dropdown-feature', 'value'),
    Input('dropdown-group', 'value'),
    Input('feature-grouping-choices','value')
)
def update_radio_pacf_feature(selected_feature,selected_group,mode):
    if mode == 'Feature':
        selected = selected_feature
    else:
        selected = selected_group
    return [{'label': feature, 'value': feature} for feature in selected]

###################################################################################################

@app.callback(
    Output('pacf', 'figure'),
    Input('radio-dataset', 'value'),
    Input('radio-pacf', 'value'),
    Input('pacf-slider', 'value')
)
def update_pacf(dataset_key, selected_feature, lag):
    data = get_filtered_data(dataset_key, selected_feature)

    model = TimeSeriesModel(data)

    return model.create_corr_plot(lag, True)

###################################################################################################

@app.callback(
    Output('adf-result', 'data'),
    Input('radio-dataset', 'value'),
    Input('dropdown-feature', 'value'),
    Input('dropdown-group', 'value'),
    Input('feature-grouping-choices','value')
)
def update_adf(dataset_key, selected_features,selected_group,mode):
    row = {'Feature': [], 'ADF-Stat': [], 'p-value': [],
           '1%-Critical': [], '5%-Critical': [], '10%-Critical': []}
    if mode == 'Feature':
        dataset = selected_features
    else:
        dataset = selected_group
        
    for feature in dataset:
        data = get_filtered_data(dataset_key, feature)
        model = TimeSeriesModel(data)
        res_tuple = model.test_stationarity()

        row['Feature'].append(feature)
        row['ADF-Stat'].append(res_tuple[0])
        row['p-value'].append(res_tuple[1])
        row['1%-Critical'].append(res_tuple[4]['1%'])
        row['5%-Critical'].append(res_tuple[4]['5%'])
        row['10%-Critical'].append(res_tuple[4]['10%'])

    data = pd.DataFrame(columns=row.keys())
    for key in row.keys():
        data[key] = row[key]
    return data.to_dict('records')

###################################################################################################


# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)
