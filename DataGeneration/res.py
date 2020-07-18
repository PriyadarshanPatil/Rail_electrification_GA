# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 13:20:11 2020

@author: 09rwa
"""

import K

from numpy import arcsin

def bearing(loco):
    if loco == 'diesel':
        return ((K.a*K.mg_c + K.b*(K.N_ax_c))*K.n_c 
                + (K.a*K.mg_c + K.b*(K.N_ax_l))*K.n_lD)
    else:
        return ((K.a*K.mg_c + K.b*(K.N_ax_c))*K.n_c 
                + (K.a*K.mg_c + K.b*(K.N_ax_l))*K.n_lE)

def flange(v,loco):
    if loco == 'diesel':
        return v*(K.B_c*K.n_c*K.mg_c + K.B_l*K.n_lD*K.m_l)
    else:
        return v*(K.B_c*K.n_c*K.mg_c + K.B_l*K.n_lE*K.m_l)

def air(v,loco):
    if loco == 'diesel':
        return K.airK*v**2*(K.n_c + K.n_lD)
    else:
        return K.airK*v**2*(K.n_c + K.n_lE)

def grade(gr,loco):
    if loco == 'diesel':
        return gr*K.m_trainD*K.g*1000
    else:
        return gr*K.m_trainE*K.g*1000

def curve(r,loco):
    if loco == 'diesel':
        return K.curve_const*K.m_trainD*K.g*arcsin(K.chord_const/r)*1000
    else:
        return K.curve_const*K.m_trainE*K.g*arcsin(K.chord_const/r)*1000

def train_power(throttle,loco):
    
    if loco == 'diesel':
        return (throttle**2/K.throttle_positions**2)*K.P_diesel  *K.n_lD*1000000
    else:
        return (throttle/100)*K.P_electric*K.n_lE*1000000

def brake(gr,r,link_speed,loco):
    if gr > 0:
        return grade(0.001,loco)
    else:
        if (bearing(loco) + flange(link_speed,loco) + air(link_speed,loco) 
            + grade(gr,loco) + curve(r,loco) > 0):
            return grade(0.001,loco)
        else:
            return ((train_power(1,loco)/link_speed) 
                    - (bearing(loco) + flange(link_speed,loco) 
                       + air(link_speed,loco) 
                       + grade(gr,loco) + curve(r,loco)
                       )
                    )

def regeneration(gr,r,link_speed,loco):
    brake_force = brake(gr,r,link_speed,loco)
    
    regenerative_braking = min(brake_force,K.current_limit*K.n_lE)
    return regenerative_braking

def tot_res(v,r,gr,link_speed,loco):
    return (bearing(loco) 
            + flange(v,loco) 
            + air(v,loco) 
            + grade(gr,loco) 
            + curve(r,loco) 
            + brake(gr,r,link_speed,loco))

def speed(throttle,r,gr,link_speed,loco):
    v = 0
    v_delta = 0.1
    
    power = train_power(throttle,loco)

    if gr >= 0:
        v_new = 10000
        while v_new > v:
            v += v_delta
            resistance = tot_res(v,r,gr,link_speed,loco)
            v_new = power/resistance
    else:
        v = 60
        v_new = 0
        while v_new < v:
            v -= v_delta
            resistance = tot_res(v,r,gr,link_speed,loco)
            v_new = power/resistance

#    if abs(v - v_new) > v_delta:
#        print(v,v_new)
    return (v+v_new)/2

def power(link_speed,r,gr,loco):
    throttle = 1
    
    if loco == 'diesel':
        for throttle in range(1,K.throttle_positions + 1):
            current_speed = speed(throttle,r,gr,link_speed,loco)
            if current_speed > link_speed or throttle == K.throttle_positions:
                return (throttle, current_speed)
                break
    else:
        for throttle in range(1,100 + 1):
            current_speed = speed(throttle,r,gr,link_speed,loco)
            if current_speed > link_speed or throttle == 100:
                return (throttle, current_speed)
                break

def FFTT(length,link_speed,r,gr,loco):
    return (length*1000)/power(link_speed,r,gr)[1]



