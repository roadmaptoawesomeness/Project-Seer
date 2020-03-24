# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 06:29:57 2020

@author: cmchico
"""
import pandas as pd
import numpy as np
import f_optimize as ed

def sched_branch(actual_atm,reload_amt, tid,t,threshold,r=0.05/365, reload_charge=2000,days_no=7,hor=2,g4s=None):
    
    atm_no=len(tid)
    reload_list = ['c_'+tid[i] for i in range(atm_no)]
    aa = actual_atm.copy()
    aa['decision'] = ""
    aa['start_bal'] = 0
    aa['start_reload'] = 0
    aa['total_bal']=0
    aa['end_bal'] =0
    # aa['end_bal_temp'] =0
    aa['total_demand'] = aa['day 0']
    aa['threshold'] = threshold
    aa['excess'] = 0
    
    aa['cashout_flag'] = 0
    aa['reload_flag'] = 0
    
    start_bal_col = ['start_bal_' + str(i) for i in range(atm_no)]
    last_load_col = ['last_load_amt_' + str(i) for i in range(atm_no)]
    fload_col = ['fload_' + str(i) for i in range(atm_no)]
    total_bal_col = ['total_bal_' + str(i) for i in range(atm_no)]
    end_bal_col = ['end_bal_' + str(i) for i in range(atm_no)]
    end_bal_col_temp = ['end_bal_' + str(i) + '_temp' for i in range(atm_no)]
    start_load_col = ['start_reload_' + str(i) for i in range(atm_no)]
    avail_atm = ['avail_'+ str(i) for i in range(atm_no)]
    wdl_col = ['wdl_'+tid[i] for i in range(atm_no)]
    
    aa = aa.join(pd.DataFrame([[0 for i in range(atm_no*7)] for j in range(aa.shape[0])], 
                               columns= last_load_col + start_bal_col + start_load_col + total_bal_col + end_bal_col
                                  + end_bal_col_temp + fload_col, index = aa.index))
    
    if g4s is None:
        aa['reload_type'] = "No COG Reload"
    else:
        aa = aa.merge(g4s,how='left').sort_values('pred_date')
        aa.reload_type = aa.reload_type.fillna('No COG Non-Forecast Reload')
        aa[reload_list] = aa[reload_list].fillna(0)
        aa[start_load_col] = aa[reload_list]
        aa['reload_flag'] = (aa[start_load_col]>0).sum(axis=1)
    
    #set initial values
    aa.loc[0,total_bal_col] = reload_amt
    
    aa.loc[0,'start_bal'] = aa[start_bal_col].values[0].sum()
    aa.loc[0,'total_bal'] = aa[total_bal_col].values[0].sum()
    
    aa.loc[0,'reload_flag'] = sum(aa.loc[0,start_load_col] > 0)
    
    
    forecast = ['day ' + str(i) for i in range(hor,days_no+hor)]
    forecast_hor = ['day ' + str(i) for i in range(hor)]
    
    t=threshold/hor/atm_no

    
    for i in range(aa.shape[0] - hor):
        next_ = min(i+1,aa.shape[0]-1)
        next_hor = min(next_+hor,aa.shape[0]-1)
        
        
        #assign ending balances to temporary columns
        aa.loc[i,end_bal_col_temp] = aa[total_bal_col].values[i] - aa[wdl_col].values[i]
        aa.loc[i,end_bal_col] = aa.loc[i,end_bal_col_temp].values
        
         
        #distribute excess demand from one atm to another
        excess = abs(aa[end_bal_col_temp].values[i][aa[end_bal_col_temp].values[i] < 0].sum())
        
        if excess > 0:
            positive = (np.array(end_bal_col)[aa[end_bal_col_temp].values[i] > 0]).tolist()
            for col in positive:
                if excess > 0:
                    curr = aa.loc[i,col+'_temp']
                    aa.loc[i,col] = max(0,curr-excess)
                    excess = excess-curr
            aa.loc[i,end_bal_col] = aa.loc[i,end_bal_col].apply(lambda x: max(0,x)).values
    
        aa.loc[next_,start_bal_col] = aa.loc[i,end_bal_col].values
        aa.loc[i,'excess'] = excess
        
        #if there is excess demand, after distributing to other atms, then this is cashout
        #force the next day for reload
        if excess > 1000:
            print("cashout")
            aa.loc[i,'cashout_flag'] = 1
            aa.loc[next_,start_load_col] =  reload_amt
        
        #set-up next
        reloaded = aa[start_load_col].values[next_]>0
        aa.loc[next_,total_bal_col]   = aa[start_load_col].values[next_]  + 1*(~reloaded)*aa[start_bal_col].values[next_]
    
        #set-up parameters for optimization on t + hor
        d = aa.loc[next_,forecast].tolist()  
        
        #total remaining balance by start of reload time is 
        #sum of balances OR reloads during horizon less demands
        #distribute demands based on proportion of starting day balance for simulation
        
        #first day
        proportion = (aa[total_bal_col].values[next_]/aa[total_bal_col].values[next_].sum()*100).astype(int)/100
        d1 = aa[forecast_hor].values[next_][0]*proportion
        bal_ = aa[total_bal_col].values[next_] - d1
        
        #next days until t + hor
        for m in range(1,hor):
            bal_ = bal_*(aa.loc[next_+m,fload_col].values<=0) + aa.loc[next_+m,fload_col].values
            proportion = (bal_/bal_.sum()*100).astype(int)/100
            bal_ = bal_ - aa[forecast_hor].values[next_][m]*proportion
        
        #by start of optimization, balance should be at least 0. If this is negative, then it will force
        #the optimization to reload
        b = ((bal_>0)*bal_).tolist()
    
        prob, X_= ed.get_schedule(b,d,reload_amt,
                     atm_no,days_no,reload_charge=reload_charge, r=r,t=t, t_day0=threshold)
        
        
        #set-up reloads for t + hor
        if sum(sum(X_[:1,]))>0:
            aa.loc[next_,"decision"] = "REL AT T+" + str(hor)
            aa.loc[next_hor,fload_col] = X_[:1,].flatten()*reload_amt
            
            #add reloads to atms not yet "reloaded" by G4S pre-empt
            aa.loc[next_hor,start_load_col] = ((X_[:1,].flatten() + aa.loc[next_hor,reload_list].values)>0)*reload_amt
                
        aa.loc[next_hor,'reload_flag'] = sum(aa.loc[next_hor,start_load_col] > 0)
    
    #totals
    # aa.loc[i,'end_bal_temp'] = aa[end_bal_col_temp].sum(axis=1)   
    aa['end_bal'] = aa[end_bal_col].sum(axis=1)
    aa['total_bal'] = aa[total_bal_col].sum(axis=1)
    
    aa['civ_cost'] = aa.end_bal.apply(lambda x: max(0,x*r))
    aa['reload_cost'] = aa.reload_flag*reload_charge
    aa['total_cost'] = aa.civ_cost + aa.reload_cost
    aa[avail_atm] = (aa[total_bal_col] > 0)*1
    return aa