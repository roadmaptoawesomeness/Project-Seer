# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 00:21:38 2020

@author: cmchico
"""

from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics

import numpy as np

import warnings
warnings.filterwarnings('ignore')

def model_prophet(series,holidays, weekly=0,monthly=0, dev_length = 729, period='1 days', horizon = '1 days', cvf=True,perf=True,                              val_dates=None):
    
    #define model
    modelf = Prophet(interval_width = 0.95,
                    daily_seasonality = False,
                    weekly_seasonality = False,
                    yearly_seasonality = False,
                    holidays = holidays)
    if weekly != 0: modelf.add_seasonality(name='weeklyx', period = 7, fourier_order = weekly)
    if monthly != 0: modelf.add_seasonality(name='monthlyx', period = 30.5, fourier_order = monthly)
     
    return modelf

def model_prophet_predict(modelf,val_dates):
    
    val_perf = modelf.predict(val_dates)
    dev_perf = modelf.predict()