from dataclasses import dataclass
from numpy import ndarray, log
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import plotly.graph_objects as go

class TimeSeriesModel:
    
    def __init__(self, data : pd.DataFrame) -> None:
        self.data = data.dropna()
    
    def plot_feature(self, title : str =None) -> None:
        feature_name = self.data.columns[~self.data.columns.isin(['Date'])][0]
        
        x = self.data['Date'].astype(str)
        y = self.data[feature_name]
        if title is None:
            title = f'{feature_name} growth over years'
        fig = px.line(x=x, y=y, labels={'x': f"Date", 'y': f"{feature_name}"}, title=title)
        fig.show()

    def test_stationarity(self, to_print : bool =False) -> ndarray:
        
        feature_name = self.data.columns[~self.data.columns.isin(['Date'])][0]
        
        adf = adfuller(self.data[feature_name].values)

        if adf[0] > 0:
            adf = adfuller(log(self.data[feature_name].values))
        if to_print:
            print('ADF Statistic: %f' % adf[0])
            print('p-value: %f' % adf[1])
            print('Critical Values:')
            for key, value in adf[4].items():
                print(f"{key} {value}")
        return adf


    def plot_acf(self, nlags=50) -> None:
        feature_name = self.data.columns[~self.data.columns.isin(['Date'])][0]
        plot_acf(self.data[feature_name], lags=nlags, adjusted=True)

    def plot_pacf(self, method="ywa") -> None:
        feature_name = self.data.columns[~self.data.columns.isin(['Date'])][0]
        plot_pacf(self.data[feature_name], method=method)

    # Credit: https://community.plotly.com/t/plot-pacf-plot-acf-autocorrelation-plot-and-lag-plot/24108/3
    def create_corr_plot(self, lag=12, plot_pacf=False):
        
        feature = self.data.columns[~self.data.columns.isin(['Date'])][0]
        fig = go.Figure()

        series = self.data[feature]
        corr_array = pacf(series, alpha=0.05, nlags=lag) if plot_pacf else acf(series, alpha=0.05, nlags=lag)
        lower_y = corr_array[1][:, 0] - corr_array[0]
        upper_y = corr_array[1][:, 1] - corr_array[0]

        lines = [go.Scatter(x=(x, x), y=(0, corr_array[0][x]), mode='lines', line_color='#3f3f3f') for x in
                 range(len(corr_array[0]))]
        fig.add_traces(lines)

        fig.add_trace(
            go.Scatter(x=np.arange(len(corr_array[0])), y=corr_array[0], mode='markers', marker_color='#1f77b4',
                       marker_size=12))

        fig.add_trace(
            go.Scatter(x=np.arange(len(corr_array[0])), y=upper_y, mode='lines', line_color='rgba(255,255,255,0)'))

        fig.add_trace(
            go.Scatter(x=np.arange(len(corr_array[0])), y=lower_y, mode='lines', fillcolor='rgba(32, 146, 230,0.3)',
                       fill='tonexty', line_color='rgba(255,255,255,0)'))

        fig.update_traces(showlegend=False)
        fig.update_xaxes(range=[-1, lag])
        fig.update_yaxes(zerolinecolor='#000000')

        title = f'Partial Auto-correlation (PACF) for {feature}' if plot_pacf else f'Auto-correlation (ACF) for {feature}'
        fig.update_layout(title=title)
        return fig
