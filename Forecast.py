# -*- coding: utf-8 -*-

from fbprophet import Prophet
import numpy as np
import dask.bag as db
import pandas as pd

def forecast(series,val_dates,holidays,weekly=0,monthly=0,cpoint=0.05):
 
    """

    Parameters
    ----------
    series : dataframe
        DESCRIPTION.
    val_dates : dataframe 
         'ds' - dates for forecasting 
    holidays : dataframe, follows Propher requirements
        DESCRIPTION.
    weekly : integer, optional
        DESCRIPTION. The default is 0.
    monthly : integer, optional
        DESCRIPTION. The default is 0.
    cpoint : float, optional
        DESCRIPTION. The default is 0.05.

    Returns
    -------
    model : TYPE
        DESCRIPTION.

    """
    series = series.copy()
    val_dates = val_dates.copy()
    
    #define model
    modelf = Prophet(interval_width = 0.95,
                    daily_seasonality = False,
                    weekly_seasonality = False,
                    yearly_seasonality = False,
                    holidays = holidays,
                    changepoint_prior_scale = cpoint)
    if weekly != 0: modelf.add_seasonality(name='weeklyx', period = 7, fourier_order = weekly)
    if monthly != 0: modelf.add_seasonality(name='monthlyx', period = 30.5, fourier_order = monthly)
    
    modelf.fit(series)
    
    val_dates['yhat'] = modelf.predict(val_dates[['ds']]).yhat.values.clip(min=0)
    val_dates['pred_date'] = series.tail(1).ds.dt.date.values.tolist()[0]
    val_dates['pred_day'] = ['day '+ str(i) for i in range(val_dates.shape[0])]
    
    return model

