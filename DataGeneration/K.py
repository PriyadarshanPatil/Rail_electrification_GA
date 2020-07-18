# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 11:09:27 2020

@author: 09rwa
"""

#constants

#network parameters
trim_old_links = True

#based on speeds by FRA track classes
mph_m_s = 0.44704
speeds = {
        'A':    80*mph_m_s,
        'B':    60*mph_m_s,
        'C':    40*mph_m_s,
        'G':    25*mph_m_s,
        'H':    10*mph_m_s,
        'X':    5 *mph_m_s, #the last three are guesses...
        '0':    5 *mph_m_s,
        '_':    5 *mph_m_s
        }

'''bearing resistance'''
a = 2.9 #N/tonne
b = 97.3 #N

'''flange resistance'''
B_l = 0.329 #N-s/m-tonne for locomotives
B_c = 0.494 #N-s/m-tonne for railcars

'''air resistance'''
airK = 1.56 #N-s^2/m^2 for conventional equipment
#K = 2.06 #N-s^2/m^2 for conventional equipment

'''grade resistance'''
g = 9.80665 #m/s^2

'''curve resistance'''
curve_const = 0.45836 #unitless
chord_const = 30.48/2 #m
min_curve = 500 #m
max_curve = 10000 #m

'''brake resistance'''

'''inertial resistance'''

'''regenerative braking'''
current_limit = 240000 #N
return_efficiency = 0.8

'''parameters for unit train'''
mg_c = 100 #gross mass for a railcar in tonnes
m_c = 30 #tare weight for a railcar in tonnes
N_ax_c = 4 #number of axles per railcar
N_ax_l = 6 #number of axles per locomotive

n_lD = 3.1 #number of diesel-electric locomotives per train unit
n_lE = n_lD*0.75 #number of electric locomotives per train unit
n_c = 47.44 #number of railcars per train unit

m_l = 192 #mass of locomotive, tonnes
P_diesel = 2.29925 #MW
P_electric = 3.0 #MW
throttle_positions = 8

m_trainD = n_lD*m_l + n_c*mg_c
m_trainE = n_lE*m_l + n_c*mg_c

'''parameters for link capacity'''
tonnes_per_train = n_c*(mg_c - m_c)
capacity_per_track = 40 #trains per day
single_track_main_direction = 0.5
single_track_opposing_direction = 0.4

def lin(x,minimum,maximum):
    return x*maximum + (1-x)*minimum

'''paramaters for electrification costs'''
OCS = [232,947]
sub = [27, 200]
trn = [10, 69 ]
pub = [0,  200]
sig = [92, 1423]
inf = [OCS[0] + sub[0] + trn[0] + pub[0],
       OCS[1] + sub[1] + trn[1] + pub[1]]
maintenance = [7.3,7.4]

discountRate = 0.07
timeHorizon = 50
maintenanceFactor = sum([1/(1+discountRate)**k for k in range(timeHorizon)])

signalCosts = {
        "S":    ['automatic control system',        1.0],
        "T":    ['automatic train control',         0.9],
        "U":    ['automatic train stop',            0.8],
        "I":    ['AMTK incremental train control',  0.6],
        "C":    ['centralised traffic control',     0.1],
        "B":    ['automatic block signals',         0.8],
        "M":    ['manual',                          0.0],
        "O":    ['timetable and train order',       0.0],
        "_":    ['unknown',                         0.5],
        "G":    ['unknown',                         0.5]
        }
for k in signalCosts:
    signalCosts[k].append(lin(signalCosts[k][1],sig[0],sig[1]))

'''paramaters for generalised costs'''
logistics = 0.584225/3600 #$/tonne/s
crew = 42.55/3600 #$/s/crew
crew_per_train = 2
time_costs = (logistics + crew*crew_per_train/(mg_c - m_c)*n_c)*1.25

DE_internal_efficiency = 0.8
DE_generator_efficiency = 0.4

E_internal_efficiency = 0.9
E_transmission_efficiency = 0.9

diesel_volume_cost = 0.592 #$/L
diesel_energy = 38.6 #MJ/L
diesel_cost = diesel_volume_cost/diesel_energy #$/MJ

electricity_cost = 0.01856 #$/MJ
