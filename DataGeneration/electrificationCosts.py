# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 16:48:55 2020

@author: 09rwa
"""

import K

def electrification_cost(length, alpha, max_alpha, signalType):
    infrastructure_cost = K.lin((alpha-1)/max_alpha,K.inf[0],K.inf[1])
    signal_cost = K.signalCosts[signalType][-1]
    
    maintenance_cost = (K.lin((alpha-1)/max_alpha,
                              K.maintenance[0],
                              K.maintenance[1])*K.maintenanceFactor)
    
    return (infrastructure_cost + signal_cost + maintenance_cost)*length
