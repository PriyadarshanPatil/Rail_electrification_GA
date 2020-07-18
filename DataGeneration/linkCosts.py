# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 10:30:07 2020

@author: walthall
"""

import csv
import K #constants
import res
import GC
import electrificationCosts
from time import time
import os

directory = os.getcwd()

#name of the case to be generated, will generate a folder if none exists
case = "hiTC"

startTime = time()

#set file to the name of the links dataset
file = "linkData.csv"

#read in the links in the linkData file
links = []
linkDict = {}
with open(file) as csvfile:
    f = csv.reader(csvfile)

    max_alpha = 0

    index = 0
    for row in f:
        if index == 0:
            #record the headers from the file
            header = row
        else:
            #check whether the outdated links from the set should be left out
            if K.trim_old_links:
                #row[13] should be "STATUS"
                if row[13] not in ["A","M","P"]:
                    links.append(row)
                    linkDict[int(row[0])] = row
                    if float(row[45]) > max_alpha:
                        max_alpha = float(row[45])
        index += 1

header[0] = "FID"

startTime = time()

link_translator = {}
from_nodes = []
to_nodes = []
for link in links:
    JA = int(link[22])
    JB = int(link[23])
    linkID = int(link[0])
    
    if JA not in from_nodes:
        from_nodes.append(JA)
        link_translator[JA] = {}
        link_translator[JA][JB] = [linkID]
    else:
        if JB in link_translator[JA]:
            link_translator[JA][JB].append(linkID)
        else:
            link_translator[JA][JB] = [linkID]
    if JB not in to_nodes:
        to_nodes.append(JB)

from_nodes.sort()
to_nodes.sort()

link_order = []
for JA in from_nodes:
    JBs = [k for k in link_translator[JA]]
    if len(JBs) > 1:
        JBs.sort()
    for JB in JBs:
        for k in link_translator[JA][JB]:
            link_order.append(k)

links = []
for link in link_order:
    links.append(linkDict[link])

header.append('r')
header.append('link_speed')
for link in links:
    #alpha is at index 45
    
    alpha = float(link[45])
    lambda_ = (alpha - 1)/(max_alpha - 1)
    
    link.append(K.min_curve*lambda_ + K.max_curve*(1-lambda_))
    link.append(K.speeds[link[9]])

for element in ['DthrottleAB', #index 55
                'DthrottleBA', #index 56
                'Dv_AB', #index 57
                'Dv_BA', #index 58
                'DFFTT_AB', #index 59
                'DFFTT_BA', #index 60
                'EthrottleAB', #index 61
                'EthrottleBA', #index 62
                'Ev_AB', #index 63
                'Ev_BA', #inedx 64
                'EFFTT_AB', #index 65
                'EFFTT_BA', #index 66
                'returnedPowerMJ_AB', #index 67
                'returnedPowerMJ_BA']:
    header.append(element)

index = 0
print('--calculating diesel-electric travel times--')
for link in links:
    AB = res.power(link[54],link[53],float(link[41].strip('%')),'diesel')
    BA = res.power(link[54],link[53],float(link[42].strip('%')),'diesel')
    
    throttleAB = AB[0]
    v_AB = AB[1]
    throttleBA = BA[0]
    v_BA = BA[1]
    FFTT_AB = float(link[5])*1000/v_AB
    FFTT_BA = float(link[5])*1000/v_BA
    
    for element in [throttleAB,
                    throttleBA,
                    v_AB,
                    v_BA,
                    FFTT_AB,
                    FFTT_BA]:
        link.append(element)
    
    if index % 1000 == 0:
        print('\r'+str(round(index/35425*100,2))+'%   ',end='\r')
    index += 1
print('\r','100%')
print()

print('--calculating electric travel times--')
index = 0
for link in links:
    AB = res.power(link[54],link[53],float(link[41].strip('%')),'electric')
    BA = res.power(link[54],link[53],float(link[42].strip('%')),'electric')
    
    throttleAB = AB[0]/100
    v_AB = AB[1]
    throttleBA = BA[0]/100
    v_BA = BA[1]
    FFTT_AB = float(link[5])*1000/v_AB
    FFTT_BA = float(link[5])*1000/v_BA
    regenerationAB = (res.regeneration(float(link[41].strip('%')),
                                       link[53],
                                       link[54],
                                       'electric')
                      *v_AB*K.return_efficiency/10e6)
    regenerationBA = (res.regeneration(float(link[42].strip('%')),
                                       link[53],
                                       link[54],
                                       'electric')
                      *v_BA*K.return_efficiency/10e6)
    
    for element in [throttleAB,
                    throttleBA,
                    v_AB,
                    v_BA,
                    FFTT_AB,
                    FFTT_BA,
                    regenerationAB,
                    regenerationBA]:
        link.append(element)
    
    if index % 1000 == 0:
        print('\r'+str(round(index/len(links)*100,2))+'%   ',end='\r')
    index += 1
print('\r','100%')
print()

print('calculating capacities')
index = 0
for link in links:
    #link[7] is ENTRK, the equivalent number of tracks for the link
    ABcap = K.tonnes_per_train*K.capacity_per_track*float(link[7])
    BAcap = K.tonnes_per_train*K.capacity_per_track*float(link[7])
    
    #correct for single tracks:
    #link[10] is TRKTYP
    if link[10] == '1':
        ABcap*=K.single_track_main_direction
        BAcap*=K.single_track_opposing_direction
    
    link.append(ABcap)
    link.append(BAcap)
    
    if index % 1000 == 0:
        print('\r'+str(round(index/len(links)*100,2))+'%',end='\r')
    index += 1
print('\r','100%')
print()
header.append('ABcap') #index 69
header.append('BAcap') #index 70

print('calculating generalised costs & electrification costs')
index = 0
for k in ['DGC_AB', #index 71
          'DGC_BA', #index 72
          'EGC_AB', #index 73
          'EGC_BA', #index 74
          'electrificationCosts' #index 75
          ]:
    header.append(k)
for link in links:
    
    DFFTT_AB        = float(link[59])
    DFFTT_BA        = float(link[60])
    Dthrottle_AB    = int(  link[55])
    Dthrottle_BA    = int(  link[56])
    
    EFFTT_AB        = float(link[65])
    EFFTT_BA        = float(link[66])
    Ethrottle_AB    = float(link[61])
    Ethrottle_BA    = float(link[62])
    return_AB       = float(link[67])
    return_BA       = float(link[68])
    
    DGC_AB = GC.diesel_GC(DFFTT_AB, Dthrottle_AB)
    DGC_BA = GC.diesel_GC(DFFTT_BA, Dthrottle_BA)
    EGC_AB = GC.electric_GC(EFFTT_AB,Ethrottle_AB,return_AB)
    EGC_BA = GC.electric_GC(EFFTT_BA,Ethrottle_BA,return_BA)
    
    length      = float(link[5])
    alpha       = float(link[45])
    signalType  =       link[16]
    
    constCost = electrificationCosts.electrification_cost(length,
                                                          alpha,
                                                          max_alpha,
                                                          signalType)

    for element in [DGC_AB,DGC_BA,EGC_AB,EGC_BA,constCost]:
        link.append(element)
    if index % 1000 == 0:
        print('\r'+str(round(index/len(links)*100,2))+'%',end='\r')
    index += 1
print('\r','100%')
print()

os.chdir(directory + "/cases/" + case)

#write overall dataset
filename = "link_TTs_" + case + ".csv"
with open(filename, 'w', newline = '') as csvfile:
    f = csv.writer(csvfile)
    f.writerow(header)
    for link in links:
        f.writerow(link)
        
#write network file
filename = 'network.txt'
with open(filename, 'w', newline = '') as csvfile:
    f = csv.writer(csvfile, delimiter = '\t')
    f.writerow(["<NUMBER OF ZONES> 132"])
    f.writerow(["<NUMBER OF NODES> 28290"])
    f.writerow(["<FIRST THRU NODE> 1"])
    f.writerow(["<NUMBER OF LINKS> 28064"])
    f.writerow(["<END OF METADATA>"])
    f.writerow([""])
    f.writerow([""])
    f.writerow(["""~\tInit Node\tTerm Node\tcapacity\tlength\tfree flow time\tB
               \tpower\tSpeedLimit\tToll\t;"""])
    for link in links:
        JA = str(link[22])
        JB = str(link[23])
        capAB = str(link[69])
        length = str(link[5])
        DGC_AB = str(link[71])
        B = "1"
        Power = "4"
        SpdLmt = "0"
        Toll = "0"
        Type = "0"
        
        f.writerow(["\t" + JA + '\t' + JB + '\t' + capAB + '\t' + length + '\t' 
                   + DGC_AB + '\t' + B + '\t' + Power + '\t' + SpdLmt + '\t'
                   + Toll + '\t' + Type + '\t;'])

#write electrification costs file
filename = "Electrification_costs.csv"
with open(filename, 'w', newline = '') as csvfile:
    f = csv.writer(csvfile)
    for link in links:
        electrificationCost = str(link)
        f.writerow(electrificationCost)

filename = "Electrification_data.csv"
with open(filename, 'w', newline = '') as csvfile:
    f = csv.writer(csvfile)
    for link in links:
        JA = str(link[22])
        JB = str(link[23])
        length = str(link[ 5])
        DGC_AB = str(link[71])
        DGC_BA = str(link[72])
        EGC_AB = str(link[73])
        EGC_BA = str(link[74])
        ABcap = str(link[69])
        BAcap = str(link[70])
        DFFTT_AB = str(link[59])
        DFFTT_BA = str(link[60])
        EFFTT_AB = str(link[65])
        EFFTT_BA = str(link[66])
        
        line = [JA,JB,length,DGC_AB,DGC_BA,EGC_AB,EGC_BA,ABcap,BAcap,
                DFFTT_AB,DFFTT_BA,EFFTT_AB,EFFTT_BA]
        f.writerow(line)
        
filename = "Electrification_data_w_headers.csv"
with open(filename, 'w', newline = '') as csvfile:
    f = csv.writer(csvfile)
    
    f.writerow(["JA","JB","length","DGC_AB","DGC_BA","EGC_AB","EGC_BA",
               "ABcap","BAcap","DFFTT_AB","DFFTT_BA","EFFTT_AB","EFFTT_BA"])
    
    for link in links:
        JA          = str(link[22])
        JB          = str(link[23])
        length      = str(link[ 5])
        DGC_AB      = str(link[71])
        DGC_BA      = str(link[72])
        EGC_AB      = str(link[73])
        EGC_BA      = str(link[74])
        ABcap       = str(link[69])
        BAcap       = str(link[70])
        DFFTT_AB    = str(link[59])
        DFFTT_BA    = str(link[60])
        EFFTT_AB    = str(link[65])
        EFFTT_BA    = str(link[66])
        
        f.writerow([JA,JB,length,DGC_AB,DGC_BA,EGC_AB,EGC_BA,ABcap,BAcap,DFFTT_AB,DFFTT_BA,EFFTT_AB,EFFTT_BA])

        
os.chdir(directory)
        
print('took {}s'.format(time()-startTime))
