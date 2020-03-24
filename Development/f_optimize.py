import numpy as np
import cvxpy

def get_schedule(b,d,reload_amt,
                 atm_no,days_no,reload_charge=2000, r=0.05/365,t=0,t_day0=0):
    
    R = np.diag(reload_amt)
    B = np.array([b for i in range(days_no)])
    D = np.array([d])
    T = np.array([[t] for i in range(days_no)])
    if t_day0 >0: T[0] = t_day0
    rel_charge = np.array([[reload_charge] for i in range(atm_no)])

    C = np.tril(np.ones((days_no,days_no)))
    _1 = np.array([np.ones(atm_no)]).T
    
#by changing:
    X = cvxpy.Variable((days_no,atm_no),integer=True)


#minimize:
    #r*endbal:
    civ_cost = r*np.ones((1,days_no))@(B@_1 + C@X@R@_1 - C@D.T)
    

    #total no of reload:
    reload_cost = np.ones((1,days_no))@X@rel_charge

#subject to:
    # Each reload per atm per day should max 1, min 0
    X_ = X >= np.zeros((days_no,atm_no)) 
    reload = X<=np.ones((days_no,atm_no))

    #endbalance - threshold > 0
    nocashout = B@_1 + C@X@R@_1 - C@D.T - T >= np.zeros((days_no,1))
    
    problem = cvxpy.Problem(cvxpy.Minimize(reload_cost+civ_cost),[X_,reload,nocashout])
    problem.solve(solver=cvxpy.GLPK_MI)
    
    return problem,X.value
