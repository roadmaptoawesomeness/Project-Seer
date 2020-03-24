# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 12:52:55 2020

@author: cmchico
"""
import pandas as pd
import f_optimize as ed
import numpy as np

def sched(actual,rel_amt,pred,r, reload_charge, threshold,hor=2,g4s=None):
    aa = actual[['date_str','y']+pred].copy()

    new_cols = ['start_bal','start_reload','total_bal','end_bal','last_load_amt','decision',
                'threshold','reload_flag'
                ,'cashout_flag','thresh_breach_flag','necessary_flag'
                ,'civ_cost','reload_cost','total_cost']

    mini_cols = ['start_bal','start_reload','total_bal','end_bal']
    aa[new_cols] = pd.DataFrame([[0 for i in range(len(new_cols))] for j in range(aa.shape[0])],
                                index=aa.index)
    aa.decision=""

    if g4s is None:
        aa['cog_preemptive'] = "No Pre-emptive"
    else:
        aa['cog_preemptive'] = aa.date_str.map(g4s['Pre-Emptive'].to_dict()).fillna("No Reload")
        aa['start_reload'] = aa.date_str.map(g4s['Current Load Amount'].to_dict()).fillna(0)
        aa['reload_flag'] = (aa.start_reload>0)*1

    aa.loc[0,'start_reload'] = rel_amt
    aa.loc[0,'reload_flag'] = 1


    for i in range(aa.shape[0]-1):     

            reloaded = aa.reload_flag[i] == 1
            next_ = min(i+1,aa.shape[0])
            next_hor = min(next_+hor,aa.shape[0])

            #start of day total balance is reloaded amount or start of day balance
            aa.loc[i,'total_bal']       = aa.start_reload[i]  + 1*(~reloaded)*aa.start_bal[i]

            #end of day balance is total balance - withdrawals for the day 
            aa.loc[i,'end_bal'] = aa.total_bal[i]- aa.y[i]

            #start day balance is balance from previous day or 0 if cashout
            aa.loc[next_,'start_bal'] = max(0,aa.end_bal[i])

            mini = aa[mini_cols][next_:next_+hor+1].reset_index(drop=True).copy()
            mini['yhat'] = 0
            for j in range(hor+1):
                mini.loc[j,'yhat'] = aa[pred[j]][next_]
                mini.loc[j,'total_bal'] = mini.start_reload[j]  + 1*(mini.start_reload[j]==0)*mini.start_bal[j]
                mini.loc[j,'end_bal'] = mini.total_bal[j] - mini.yhat[j]
                mini.loc[j+1,'start_bal'] = max(0,mini.end_bal[j])
            print(mini)

            if sum(mini.end_bal<threshold*rel_amt)>0:
                aa.loc[next_,"decision"] = "REL AT T+" + str(hor)
                aa.loc[next_hor,'start_reload'] = rel_amt
                aa.loc[next_hor,'reload_flag'] = 1
                aa.loc[next_hor,'total_bal'] = rel_amt

    aa['cashout_flag'] = (aa.end_bal < 0)*1

    #reloaded today because threshold breached end-of-day yesterday
    aa['thresh_breach_flag'] = (aa.end_bal < aa.threshold*rel_amt)*1

    aa['civ_cost'] = aa.end_bal.apply(lambda x: max(0,x*r))
    aa['reload_cost'] = aa.reload_flag*reload_charge

    aa['total_cost'] = aa.civ_cost + aa.reload_cost
    
    return aa

def sched_branch(actual,rel_amt,reload_charge=2000,r=0.05/365,t=0,atm_no=1,hor=2,window=7,
                 g4s=None):
    
    pred = ['day '+str(i) for i in range(window+hor)]
    reload_amt = [rel_amt*(i+1) for i in range(atm_no)]
    
    aa = actual[['date_str','y']+pred].copy()

    new_cols = ['start_bal','start_reload','total_bal','end_bal','last_load_amt','decision',
                'threshold','reload_flag'
                ,'cashout_flag','thresh_breach_flag','necessary_flag'
                ,'civ_cost','reload_cost','total_cost']

    mini_cols = ['start_bal','start_reload','total_bal','end_bal']
    aa[new_cols] = pd.DataFrame([[0 for i in range(len(new_cols))] for j in range(aa.shape[0])],
                                index=aa.index)
    aa.decision=""
    aa.threshold = t

    if g4s is None:
        aa['cog_preemptive'] = "No Pre-emptive"
    else:
        aa['cog_preemptive'] = aa.date_str.map(g4s['Pre-Emptive'].to_dict()).fillna("No Reload")
        aa['start_reload'] = aa.date_str.map(g4s['Current Load Amount'].to_dict()).fillna(0)
        aa['reload_flag'] = (aa.start_reload/rel_amt)

    aa.loc[0,'start_reload'] = rel_amt*atm_no
    aa.loc[0,'reload_flag'] = 1
    aa['bal'] = 0
    aa['Error'] = ""

    for i in range(aa.shape[0]-1):  
            reloaded = aa.reload_flag[i] >0
            
            next_ = min(i+1,aa.shape[0])
            next_hor = min(next_+hor,aa.shape[0])

            #start of day total balance is reloaded amount or start of day balance
            aa.loc[i,'total_bal']       = aa.start_reload[i]  + 1*(~reloaded)*aa.start_bal[i]

            #end of day balance is total balance - withdrawals for the day 
            aa.loc[i,'end_bal'] = aa.total_bal[i]- aa.y[i]

            #start day balance is balance from previous day or 0 if cashout
            aa.loc[next_,'start_bal'] = max(0,aa.end_bal[i])
            
            mini = aa[mini_cols][next_:next_+hor].reset_index(drop=True).copy()
            for j in range(hor):
                mini.loc[j,'yhat'] = aa[pred[j]][next_]
                mini.loc[j,'total_bal'] = mini.start_reload[j]  + 1*(mini.start_reload[j]==0)*mini.start_bal[j]
                mini.loc[j,'end_bal'] = mini.total_bal[j] - mini.yhat[j]
                mini.loc[j+1,'start_bal'] = max(0,mini.end_bal[j])
                
            bal_0 = max(0,mini.loc[hor-1,'end_bal'])
            
            aa.loc[next_,'bal']=bal_0
            
            demand_ = aa.loc[next_,pred[hor:]].to_list() 
        
            prob,X = ed.get_schedule([bal_0],demand_,reload_amt,
                             1, window,choice=atm_no, reload_charge=reload_charge, r=r,t=t)
            

            if (X is None):
                X = np.array([[0 for i in range(atm_no-1)] +[1]])
                aa.loc[next_hor,'Error'] = "Yes"
                aa.loc[next_,"decision"] = "REL AT T+" + str(hor)
                aa.loc[next_hor,'start_reload'] = X[0]@reload_amt
                aa.loc[next_hor,'reload_flag'] = X[0]@reload_amt/rel_amt
                aa.loc[next_hor,'total_bal'] = X[0]@reload_amt                
                
                
            else: 
                if X[0]@reload_amt > 0 :
                    aa.loc[next_,"decision"] = "REL AT T+" + str(hor)
                    aa.loc[next_hor,'start_reload'] = X[0]@reload_amt
                    aa.loc[next_hor,'reload_flag'] = X[0]@reload_amt/rel_amt
                    aa.loc[next_hor,'total_bal'] = X[0]@reload_amt                
                    
            

    aa['cashout_flag'] = (aa.end_bal < 0)*1

    #reloaded today because threshold breached end-of-day yesterday
    aa['thresh_breach_flag'] = (aa.end_bal < aa.threshold*rel_amt)*1

    aa['civ_cost'] = aa.end_bal.apply(lambda x: max(0,x*r))
    aa['reload_cost'] = aa.reload_flag*reload_charge

    aa['total_cost'] = aa.civ_cost + aa.reload_cost
    
    return aa



def validate_g4s(actual,g4s, r, reload_charge, threshold):
    """
    Args:
        actual: dataframe
            date_str (str)             : date in mm-dd-yyyy string format
            AMOUNT_SUM (float)         : total withdrawals by 10PM of date
        
        g4s: dataframe
            date_str (str)             : date in mm-dd-yyyy string format
            Current Load Amount (float): amount to be reloaded at start of date_str
        
        r: float                       : daily interest rate of Cash-in-Vault
        threshold: float               : %of reloaded amount to retain in CIV
        reload_charge: float           : cost of charge per reload
    
    
    Returns
        aa: dataframe          : daily simulation of balance, reload, and costs
        summ: dataframe                : total costs
    
    """

    aa = actual[['date_str','AMOUNT_SUM']].copy()
    
    new_cols = ['start_bal','start_reload','total_bal','end_bal','last_load_amt',
                'threshold','reload_flag'
                ,'cashout_flag','thresh_breach_flag','necessary_flag'
                ,'civ_cost','reload_cost','total_cost','preemptive_flag']
    
    aa[new_cols] = pd.DataFrame([[0 for i in range(len(new_cols))] for j in range(aa.shape[0])], index=aa.index)
    
    aa['cog_preemptive'] = aa.date_str.map(g4s['Pre-Emptive'].to_dict()).fillna("No Reload")
    aa['start_reload'] = aa.date_str.map(g4s['Current Load Amount'].to_dict()).fillna(0)
    aa['last_load_amt'] = aa.date_str.map(g4s['Current Load Amount'].to_dict()).ffill()
    aa['reload_flag'] = (aa.start_reload>0)*1
    aa['threshold'] = threshold*aa['last_load_amt']
    
    for i in range(aa.shape[0]-1):     
        
        reloaded = aa.reload_flag[i] == 1
        next_ = min(i+1,aa.shape[0])
        
        #start of day total balance is reloaded amount or start of day balance
        aa.loc[i,'total_bal']       = aa.start_reload[i]  + 1*(~reloaded)*aa.start_bal[i]
        
        #end of day balance is total balance - withdrawals for the day 
        aa.loc[i,'end_bal'] = aa.total_bal[i]- aa.AMOUNT_SUM[i]
        

        #start day balance is balance from previous day or 0 if cashout
        aa.loc[next_,'start_bal'] = max(0,aa.end_bal[i])
        


    aa['cashout_flag'] = (aa.end_bal < 0)*1
    
    #reloaded today because threshold breached end-of-day yesterday
    aa['thresh_breach_flag'] = (aa.end_bal < aa.threshold)*1
    
    #reloaded today even though threshold is not breached yesterday
    aa['preemptive_flag'] = (aa.thresh_breach_flag.shift(periods=1)!=1)*1
    
    aa['civ_cost'] = aa.end_bal.apply(lambda x: max(0,x*r))
    aa['reload_cost'] = aa.reload_flag*reload_charge
    
    aa['total_cost'] = aa.civ_cost + aa.reload_cost
    return aa