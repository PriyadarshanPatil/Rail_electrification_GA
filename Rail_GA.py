# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 15:31:00 2020

@author: priyadarshan
"""
import numpy as np
import copy
import subprocess
import random
from pyeasyga import pyeasyga




#This is the binary GA code for the rail electrification paper

#Input files:
#Network file original - Used in section 1
network_file_path = "network_file.txt"
#Electrification costs - Used in section 2
elec_costs = "Electrification_costs.csv"
#Electrification TSTT and capacity data - Used in section 3
elec_data = "Electrification_data.csv"
#Final generation population is written here - Used in section 5
results_file="results.txt"


#Constants defined here
random.seed(1)
Total_electrification_budget =  10000000
#Note that electrification costs are in 1000s for our dataset, so we divide the total budget accordingly.
#100 billion corresponds to 100 million written above


##################Section 1############################
#This block reads in the network file for editing in every GA iteration and saves it as list net
#NOTE: Network should not have separate information for AB and BA links. We create that later.
with open(network_file_path) as f:
    net = f.readlines()
f.close()
#This calculates the number of lines in the network file.
#It is assumed that there are 4 lines of metadata, one line end of metadata, 2 lines of space and a line of headings
num_lines_datafile = len(net)
num_links = num_lines_datafile-8






##################Section 2############################
#This block reads in the link electrification costs
with open(elec_costs) as f:
    electrification_costs_raw = f.readlines()
f.close()

cost_array = np.zeros(num_links)
for i in range(num_links):
    cost_array[i] = float(electrification_costs_raw[i])

#Initialize the y vector, or set of links to be electrified.
#1 means electrified, 0 means not electrified
binary_array = np.zeros(num_links)

#These following lines are debugging lines which electrify three links
# binary_array[1]=1
# binary_array[3]=1
# binary_array[4]=1

#This block defines the function for calculating electrification costs
#Note that both arguments must be numpy arrays
def calculate_electrification_costs(cost_array, binary_upgrade_array):
    return np.dot(cost_array,binary_upgrade_array)





##################Section 3############################
#This section defines a function to calculate the new network file from electrified binary array
#This section also saves it as net_new.txt in the AlgB sub-folder

#Function definition starts here

def write_electrified_network(binary_array):
    
    #Read the electrification data which is JA, JB, length, DGC_AB, DGC_BA, EGC_AB, EGC_BA, AB capacity, BA capacity, DFFTT_AB, DFFTT_BA, EFFTT_AB, EFFTT_BA
    with open(elec_data) as f:
        electrification_data_raw = f.readlines()
    f.close()
    
    electrification_data = np.zeros((num_links,13))
    
    for i in range(num_links):
        electrification_data[i] = [x.strip() for x in electrification_data_raw[i].split(',')]
    
    #Change metadata
    #The metadata header is created here and stored in a variable named new_header_temp
    new_num_links= int(2*(num_links + np.sum(binary_array)))
    
    line_4 = "<NUMBER OF LINKS> "+str(new_num_links)+"\n"
    
    new_header_temp = net[0]+net[1]+net[2]+line_4+net[4]+net[5]+net[6]+net[7]
    
    #Change network information
    
    ##this has the original network information
    net_temp_array = []
                               
    for i in range(len(net)):
        if i<8:
            continue
        else:
            net_temp_array.append(net[i].split())
            
    ##Add the BA links with appropriate capacity
    net_temp_array_BA = copy.deepcopy(net_temp_array)
    for i in range(len(net_temp_array_BA)):
        net_temp_array_BA[i][0] = net_temp_array[i][1]
        net_temp_array_BA[i][1] = net_temp_array[i][0]
        net_temp_array_BA[i][2] = electrification_data[i][8]
        net_temp_array_BA[i][4] = electrification_data[i][4]
        
    
    
    ##Add electrified link data (given binary_array)
    electrified_links = []
    for i in range(len(binary_array)):
        if binary_array[i] == 0:
            continue
        else:
            electrified_link_data = copy.deepcopy(net_temp_array[i])
            #change the FFTT
            electrified_link_data[4] = str(electrification_data[i][5])
            electrified_link_data[2] =str(float(electrified_link_data[2]) * 1.001) 
            electrified_link_data[3] =str(float(electrified_link_data[3]) * 1.001) 
            electrified_links.append(electrified_link_data)
            #Repeat for BA link
            electrified_link_data = copy.deepcopy(net_temp_array_BA[i])
            #change the FFTT
            electrified_link_data[4] = str(electrification_data[i][6])
            electrified_link_data[2] =str(float(electrified_link_data[2]) * 1.001)
            electrified_link_data[3] =str(float(electrified_link_data[3]) * 1.001) 
            electrified_links.append(electrified_link_data)
    
    
    #Save the metadata and network into a file names net_new.tntp
    #Step 1 compines the AB links, BA links and electrified links
    net_new = net_temp_array+net_temp_array_BA+electrified_links

    file1 = open("AlgB_data/net.txt","w")
    file1.write(new_header_temp)
    for i in range(len(net_new)):
        file1.write("\t" + str(net_new[i][0]) + "\t" + str(net_new[i][1]) + "\t" + str(net_new[i][2]) + "\t" + str(net_new[i][3]) + "\t" + str(net_new[i][4]) + "\t" + str(net_new[i][5]) + "\t" + str(net_new[i][6]) + "\t" + str(net_new[i][7]) + "\t" + str(net_new[i][8]) + "\t" + str(net_new[i][9]) + "\t" + ";" + "\n")    
    file1.close() 

    #print ("File written successfully")
    
    return

#write_electrified_network(binary_array)








##################Section 4############################
#This block is the candidate evaluation function.
#Takes a candidate solution as input, calls the electrified network writer to write new network, solves TAP for it, and then returns the total system cost
#Also, if the candidate solution violates total budget constraint, returns value of -9999999999999999

def fitness_evaluation(binary_arrays,data):
    fitness = -9999999999999999
    if calculate_electrification_costs(cost_array, binary_arrays)>Total_electrification_budget:
        print("overbudget")
        return fitness
    else:
        write_electrified_network(binary_arrays)
        TScost_out = subprocess.check_output(["java", "-jar", "AlgB_data/wrapPD.zip" , "AlgB_data/net.txt" , "AlgB_data/trips.txt", "AlgB_data/oneClass.txt"],universal_newlines = True)
        return (-1*float(TScost_out))
        # return random.randint(-50000000, 10000000)


# a_test=fitness_evaluation(binary_array,net)









#################Section 5############################
#This section runs the binary GA for rail electrification.

#Step1 - define data
data = net


#Step 2 -  create individual data 
def create_individual(data):
    individual = copy.deepcopy(binary_array)
    return individual


#Step 3 - initialize GA
ga = pyeasyga.GeneticAlgorithm(data, population_size=15, generations=100, crossover_probability=0.0, mutation_probability=0.3,  elitism=True, maximise_fitness=True)
ga.create_individual = create_individual

#Step 4  - assign fitness function
ga.fitness_function = fitness_evaluation


#Step 5 - run GA
ga.run()


#Step 6  - print out last generation
for individual in ga.last_generation():
    print (individual)

#Step 7 - Save individuals to a file named results_txt
file1 = open(results_file,"w")
np.set_printoptions(threshold=np.inf)
file1.write(str(ga.best_individual()[1]))
file1.close()



