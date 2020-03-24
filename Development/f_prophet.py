# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 15:36:44 2020

@author: cmchico
"""

from fbprophet import Prophet
import numpy as np
import dask.bag as db
import pandas as pd

def train(series,val_dates,holidays,weekly=0,monthly=0,cpoint=0.05):
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
    val_dates['pred_day'] = ['day '+str(i) for i in range(val_dates.shape[0])]
    val_dates['error'] = val_dates.y - val_dates.yhat
    val_dates['se'] = val_dates.error**2
    
    return modelf,val_dates

def predict(atm,series,dev_length,val_length, HP, week,mon, horizon,cpoint = 0.05):

    #Predict for development dataset
    fitted_model,model1 = train(series[0:dev_length],series[0:dev_length], HP, week, mon, cpoint=cpoint)
    model1['pred_day'] = 'day 0'
    model1['tid'] = atm
    rmse1 = model1.groupby([model1.ds.dt.month,'pred_day']).se.mean().agg(np.sqrt).reset_index()
    
    dbseries = db.from_sequence([series[i:i+dev_length] for i in range(val_length)])
    dbforecast = db.from_sequence([series[i+dev_length:i+dev_length+horizon][['ds','y']] for i in range(val_length)])

    dbmaster = db.map(train,dbseries,dbforecast,HP,week,mon, cpoint=cpoint)

    modelf =dbmaster.compute()
    model = pd.concat([modelf[i][1] for i in range(len(model))])
    model['tid'] = atm
    rmse = model.groupby([model.ds.dt.month,'pred_day']).se.mean().agg(np.sqrt).reset_index()
    print(f'\nATM:{atm}  RMSE:{rmse.se.mean()}')
    return modelf[len(val_length)-1][0], pd.concat([model1,model]),pd.concat([rmse1,rmse])
