# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 13:07:06 2020

@author: cmchico
"""
import plotly.graph_objects as go
import plotly as plt

def get_bounds(all_):
    bounds = ((all_[['y','error']].agg(['max','min'])/1000000).round())*1000000
    bounds.y = bounds.y+1000000
    bounds.error = bounds.error-1000000
    return bounds

def flag_holi(holi):
    shape =  [
        dict(
            type="rect",
            # x-reference is assigned to the x-values
            xref="x",
            # y-reference is assigned to the plot paper [0,1]
            yref="paper",
            x0=holi.ds[i].date(),
            y0=0,
            x1=holi.ds_next[i].date(),
            y1=1,
            fillcolor="LightSalmon",
            opacity=0.5,
            layer="below",
            line_width=0)
     for i in holi[holi.event=='Payroll'].index] + \
    [
        dict(
            type="rect",
            # x-reference is assigned to the x-values
            xref="x",
            # y-reference is assigned to the plot paper [0,1]
            yref="paper",
            x0=holi.ds[i].date(),
            y0=0,
            x1=holi.ds_next[i].date(),
            y1=1,
            fillcolor="LightCoral",
            opacity=0.5,
            layer="below",
            line_width=0)
     for i in holi[holi.event=='Holiday'].index]
    return shape

def visual(all_,holi, path):
    atm =  all_.tid[0]
    atm_name = all_.tid_name[0]
    val_mape = "%{:.2f}".format(all_.val_mape[0]*100)
    val_rmse = "Php {:.2f} K".format(all_.val_rmse[0]/1000)
    pred = list(all_.yhat.values)
    pred_upper = list(all_.upper)
    pred_lower = list(all_.lower)
    error = list(all_.error)

    test_dates = list(all_.index)
    test = list(all_.y.values)

    # Layout
    layout = go.Layout(
        paper_bgcolor='rgb(255,255,255)',
        plot_bgcolor='rgb(255,255,255)',
        yaxis=dict(
            gridcolor='rgb(165,172,175)',
            showgrid=True,
            showline=False,
            showticklabels=True,
            tickcolor='rgb(127,127,127)',
            ticks='outside',
            zeroline=False
        ),
        xaxis=dict(
            gridcolor='rgb(165,172,175)',
            showgrid=True,
            gridwidth = 0.5,
            showline=False,
            showticklabels=True,
            tickcolor='rgb(127,127,127)',
            ticks='outside',
            zeroline=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                        label="1w",
                        step="day"),
                    dict(count=1,
                         label="1m",
                         step="month"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=False
            ),
            type = "date"
        ),
        xaxis_range=['2019-02-01','2019-04-30'],
        xaxis_tickmode = 'array',
        xaxis_tickvals = [15*k for k in range(len(test_dates))],
        xaxis_ticktext = [],
        showlegend=True
    )

    trace1 = go.Scatter(
        x =test_dates,
        y =test,
        line = dict(color='rgba(0,0,0,1)'),
        mode = 'lines+markers',
        showlegend = True,
        name = 'Actual Withdrawal')

    upper_bound = go.Scatter(
        name = 'Upper Bound',
        x =test_dates,
        y = pred_upper,
        mode = 'lines',
        marker = dict(color = 'rgba(44,160,44,0.2)'),
        line = dict(width = 0),
        fillcolor = 'rgba(44,160,44,0.2)',
        fill ='tonexty',
        showlegend = False)

    trace2 = go.Scatter(
        x =test_dates,
        y = pred,
        line=dict(color='green'),
        mode = 'lines+markers',
        showlegend=True,
        name='Forecasted Withdrawal',
        fillcolor = 'rgba(44,160,44,0.2)',
        fill = 'tonexty')

    lower_bound = go.Scatter(
        name='Lower Bound',
        x=test_dates,
        y=pred_lower,
        marker = dict(color = 'rgba(44,160,44,0.2)'),
        line = dict(width = 0),
        mode = 'lines',
        showlegend = False)

    trace3 = go.Bar(
        x = test_dates,
        y = error,
        marker_color = 'rgba(207,207,207,1)',
        showlegend = True,
        name = 'Forecast Error')
    forecasted = [lower_bound,trace2,upper_bound]

    # Create figure
    fig = go.Figure(data = forecasted,layout = layout)

    # Add Trace
    fig.add_trace(trace1)
    fig.add_trace(trace3)

    # Add range slider
    fig.layout.update(
        height = 600,
        width = 1200,
        xaxis_title = 'Date',
        yaxis_title = 'Daily Withdrawal',
        xaxis_tickformat = '%b %d <br>%Y <br>(%a)',
        title = 'Actual vs. Predicted Daily Withdrawals (ATM ' + atm + ': ' + atm_name + ')'+'<br>'+ \
                'Ave Daily Error: ' + val_rmse + ' (' + val_mape + ')',
        shapes=flag_holi(holi)
    )

    bounds = get_bounds(all_)
    fig.update_yaxes(range = [bounds.error['min'],bounds.y['max']],
                     showline = True,
                     linecolor = 'gray',
                     mirror = True,
                     tickprefix = '₱')

#     fig.update_xaxes(range = [pd.to_datetime('01-31-2019'),pd.to_datetime('05-01-2019')],
#                      showline = True,
#                      linecolor = 'gray',
#                      mirror = True,
#     )

    fig.show()
    # fig.write_image(validation+'ATM8739.png')
    plt.offline.plot(fig, filename=path + '_'+atm+'_.html', auto_open=False)
    return fig