from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics

import numpy as np

import warnings
warnings.filterwarnings('ignore')

def compute_rmse(cvf,agg='mean'):

    a = cvf.copy()
    a['se'] = ((a.y - a.yhat)**2)
    a = a[['cutoff', 'se']]
    if agg == 'mean': 
        return a.groupby(['cutoff']).se.mean().apply(np.sqrt).mean()
    if agg == 'median':
        return a.groupby('cutoff').se.mean().apply(np.sqrt).median()
   
def model_prophet(series,holidays, weekly=0,monthly=0, dev_length = 729, period='1 days', horizon = '1 days', cvf=True,perf=True,                              val_dates=None):
    
    #define model
    modelf = Prophet(interval_width = 0.95,
                    daily_seasonality = False,
                    weekly_seasonality = False,
                    yearly_seasonality = False,
                    holidays = holidays)
    if weekly != 0: modelf.add_seasonality(name='weeklyx', period = 7, fourier_order = weekly)
    if monthly != 0: modelf.add_seasonality(name='monthlyx', period = 30.5, fourier_order = monthly)
    
    modelf.fit(series)
    
    #test for horizon
    if cvf:     cvf = cross_validation(modelf, initial = str(dev_length) + ' days', period = period, horizon = horizon)
    if perf:    perf = performance_metrics(cvf)
 
    return modelf, cvf, perf

def model_prophet_predict(series,val_dates, holidays, weekly=0,monthly=0):
    
    #define model
    modelf = Prophet(interval_width = 0.95,
                    daily_seasonality = False,
                    weekly_seasonality = False,
                    yearly_seasonality = False,
                    holidays = holidays)
    if weekly != 0: modelf.add_seasonality(name='weeklyx', period = 7, fourier_order = weekly)
    if monthly != 0: modelf.add_seasonality(name='monthlyx', period = 30.5, fourier_order = monthly)
    
    modelf.fit(series)
 
    return modelf, modelf.predict(val_dates)
