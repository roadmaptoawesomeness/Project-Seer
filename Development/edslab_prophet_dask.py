# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 13:49:29 2020

@author: cmchico
"""

import edslab_prophet as ed

import dask.bag as db



def parallel_model_prophet(series, scenario,holi_set, dev_length = 729, period='1 days', horizon = '1 days'):          
    
#  If choosing among holiday lists, get only 1 best
    holi_set_no = range(len(holi_set))
    dbseries = db.from_sequence([series for i in holi_set_no])
    dbhol = db.from_sequence(holi_set)

    dbmaster = dbseries.map(ed.model_prophet,dbhol,weekly=0,monthly=0, 
                            dev_length=dev_length, period=period, horizon=horizon)

    model = dbmaster.compute()
    
    rmse_list = [model[i][2]['rmse'].mean() for i in holi_set_no]
    i = rmse_list.index(min(rmse_list))

    holiday = holi_set[i]
    select = (scenario.hol_num == i) & ~(scenario.week + scenario.mon == 0)
    
#     Run only for selected holiday
    scenario_filter = scenario[select].reset_index(drop=True)

    dbseries = db.from_sequence(series for i in range(scenario_filter.shape[0]))
    dbhol = db.from_sequence(holiday for i in scenario_filter.hol_num)
    dbweek = db.from_sequence(week for week in scenario_filter.week)
    dbmon = db.from_sequence(mon for mon in scenario_filter.mon)

    dbmaster = dbseries.map(ed.model_prophet,dbhol,dbweek,dbmon,dev_length=dev_length,period=period, horizon = horizon)
    
    model = dbmaster.compute()

    
    return  scenario_filter,model

def parallel_model_prophet_oneholi(series, scenario,holiday,dev_length = 729, period='1 days', horizon = '1 days'):          
    
#  If choosing among holiday lists, get only 1 best
    dbseries = db.from_sequence(series for i in range(scenario.shape[0]))
    dbhol = db.from_sequence(holiday for i in range(scenario.shape[0]))
    dbweek = db.from_sequence(week for week in scenario.week)
    dbmon = db.from_sequence(mon for mon in scenario.mon)

    dbmaster = dbseries.map(ed.model_prophet,dbhol,dbweek,dbmon,dev_length=dev_length,period=period, horizon = horizon)
    
    model = dbmaster.compute()

    
    return  model