# code to find puncture mergers

import numpy as np
import os
import sys

from scipy.interpolate import CubicSpline

#scratch = os.environ["SCRATCH"] + "/" ## <---- put data location here
#scratch = "/data/yliang3/BH_N25/new_case/data"
scratch = sys.argv[1]


sim_name = "BH_N25"

def interpolate_puncture_data(puncture_data,dt):
  t = puncture_data[:,0]
  t_plot = np.arange(0.0,t[-1],2.4)
  N = len(t_plot)
  N_punc = int((len(puncture_data[0,:])-1)/3)
  out_data = np.zeros((N,1+3*N_punc))
  for ipunc in range(0,N_punc):
    x = puncture_data[:,1+ipunc*3]
    y = puncture_data[:,2+ipunc*3]
    z = puncture_data[:,3+ipunc*3]
    x_cs = CubicSpline(t,x)
    x_plot = x_cs(t_plot)
    y_cs = CubicSpline(t,y)
    y_plot = y_cs(t_plot)
    z_cs = CubicSpline(t,z)
    z_plot = z_cs(t_plot)
    #R = np.sqrt(x**2 + y**2 + z**2)
    #print(ipunc)
    #print("z = ", z[-1])
    #xyz_list.append((x_plot,y_plot,z_plot))
    out_data[:,1+3*ipunc] = x_plot
    out_data[:,1+3*ipunc+1] = y_plot
    out_data[:,1+3*ipunc+2] = z_plot
  out_data[:,0] = t_plot
  return out_data

def find_mergers(puncture_data,puncture_mass):
  N_BHs = int(len(puncture_data[0,1:])/3)
  merger_groups = []
  formation_times = [0]*N_BHs
  absorbed_times = [np.inf]*N_BHs
  BH_masses = [puncture_mass]*N_BHs
  out_puncture_data_list = []
  #
  n_times = len(puncture_data[:,0])
  for tt in range(0,n_times):
    t = puncture_data[tt,0]
    puncture_data_t = puncture_data[tt,1:]
    N_BHs_now = len(BH_masses)
    # get positions of BHs formed from mergers
    for igroup in range(0,len(merger_groups)):
      group = merger_groups[igroup]
      group_centre = np.zeros(3)
      for imember in group:
        group_centre += BH_masses[imember]*puncture_data_t[3*imember:3*imember+3]   
      group_centre /= BH_masses[N_BHs+igroup]
      puncture_data_t = np.append(puncture_data_t,group_centre)
    # find new mergers
    for i in range(0,N_BHs_now):
      if ((t > formation_times[i]) and (t < absorbed_times[i])):
        for j in range(i+1,N_BHs_now):
          if ((t > formation_times[j]) and (t < absorbed_times[j])):
            centeri = puncture_data_t[3*i:3*i+3]
            centerj = puncture_data_t[3*j:3*j+3]
            distance = np.linalg.norm(centeri - centerj)
            min_distance = (BH_masses[i] + BH_masses[j])
            if (distance < min_distance):
              absorbed_times[i] = t
              absorbed_times[j] = t
              merger_groups.append([i,j])
              BH_masses.append(BH_masses[i]+BH_masses[j])
              new_BH_num = len(BH_masses)-1
              formation_times.append(t)
              absorbed_times.append(np.inf)
              print("{:d} + {:d} --> {:d} at time {:.2f}".format(i+1,j+1,new_BH_num+1,t))
              with open("merger_events.txt", "a") as f:
                f.write(f"{i+1},{j+1},{t:.2f}\n")
              group_centre = np.zeros(3)
              group_centre = (BH_masses[i]*centeri + BH_masses[j]*centerj)/BH_masses[new_BH_num]
              puncture_data_t = np.append(puncture_data_t,group_centre)
            #
          #
        #
      #
    #
    out_puncture_data_list.append(puncture_data_t)
  N_BHs_final = len(BH_masses)
  out_BH_data = np.ones((n_times,1+3*N_BHs_final))*(-1)
  out_BH_data[:,0] = puncture_data[:,0]
  for tt in range(0,n_times):
    out_BH_data[tt,1:1+len(out_puncture_data_list[tt])] = out_puncture_data_list[tt]
  #
  headings = "      time"
  for iBH in range(0,N_BHs_final):
    headings += "x_{:d}".format(iBH+1).rjust(20," ") + "y_{:d}".format(iBH+1).rjust(20," ") + "z_{:d}".format(iBH+1).rjust(20," ")
  np.savetxt(sim_name + "_all_BHs_punctures.dat",out_BH_data,fmt=["%12.5f"]+["%20.10e"]*3*N_BHs_final,delimiter="",header=headings)
  print("saved locations as ", sim_name + "_all_BHs_punctures.dat")
  #
  formation_times = np.array(formation_times)
  absorbed_times = np.array(absorbed_times)
  BH_masses = np.array(BH_masses)
  BH_index = np.arange(1,N_BHs_final+1,1)
  BH_component_1 = np.ones(N_BHs_final)*(-1)
  BH_component_2 = np.ones(N_BHs_final)*(-1)
  for iBH in range(N_BHs,N_BHs_final):
    BH_component_1[iBH] = merger_groups[iBH-N_BHs][0]
    BH_component_2[iBH] = merger_groups[iBH-N_BHs][1]
  BH_data = np.column_stack((BH_index,BH_masses,formation_times,absorbed_times,BH_component_1,BH_component_2))
  headings = "BH".rjust(3," ") + "mass".rjust(6," ") + "t_formation".rjust(13," ") + "t_merge".rjust(13," ") + "parent_1".rjust(11," ") + "parent_2".rjust(11," ") 
  np.savetxt(sim_name + "_merger_info.dat",BH_data,fmt=["%5d","%5.2f","%12.5f","%12.2f","%10d","%10d"],delimiter=" ",header=headings)
  print("saved merger data as ", sim_name + "_merger_info.dat")

####

puncture_data = np.genfromtxt(scratch+"/punctures.dat")

interp_puncture_data = interpolate_puncture_data(puncture_data,2.4)

m_BH = 0.5

find_mergers(interp_puncture_data,m_BH)
