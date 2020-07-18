# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 16:46:35 2020

@author: 09rwa
"""

import K

def diesel_GC(FFTT, throttle):
    
    efficiency = (K.DE_internal_efficiency
                  *K.DE_generator_efficiency) #unitless
    power_consumption = ((throttle**2/K.throttle_positions**2)
                         *(K.P_diesel*K.n_lD)/efficiency) #MW
    
    return ((K.time_costs*FFTT) 
            + power_consumption*FFTT*K.diesel_cost/K.tonnes_per_train)

def electric_GC(FFTT, throttle, returnedPower):
    efficiency = (K.E_internal_efficiency
                  *K.E_transmission_efficiency) #unitless
    power_consumption = (throttle*K.P_electric*K.n_lE)/efficiency
    
    return ((K.time_costs*FFTT) 
            + (power_consumption*FFTT 
               - returnedPower)*K.electricity_cost/K.tonnes_per_train)
