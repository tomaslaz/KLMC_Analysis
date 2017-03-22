"""
Utilities module.

@author Tomas Lazauskas, 2017
@web www.lazauskas.net
@email tomas.lazauskas[a]gmail.com

"""

import copy
import os
import random
import string
import subprocess

_systems_stats_file = "Stats.csv"

def distanceSq(pos1x, pos1y, pos1z, pos2x, pos2y, pos2z):
  """
  Returns a squared distance between two positions in the Cartesian system 
  
  """
  
  return ((pos1x - pos2x)**2.0 + (pos1y - pos2y)**2.0 + (pos1z - pos2z)**2.0)

def atomicSeparation2(atomPos1, atomPos2, cellDims, PBC):
  """
  Return atomic separation squared with accounted periodic boundary conditions
  
  """
  
  rx = atomPos1[0] - atomPos2[0]
  ry = atomPos1[1] - atomPos2[1]
  rz = atomPos1[2] - atomPos2[2]
  
  if (PBC[0] == 1):
    rx = rx - round( rx / cellDims[0] ) * cellDims[0]

  if (PBC[1] == 1):
    ry = ry - round( ry / cellDims[1] ) * cellDims[1]

  if (PBC[2] == 1):
    rz = rz - round( rz / cellDims[2] ) * cellDims[2]

  sep2 = rx * rx + ry * ry + rz * rz;
      
  return sep2

def get_random_name(n=10):
  """
  Generates a n length random string
  
  """

  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def run_sub_process(command, verbose=0):
  """
  Run command using subprocess module.
  Return tuple containing STDOUT, STDERR, STATUS
  Caller can decide what to do if status is true
  
  """
  
  if verbose:
    print command
  
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, stderr = process.communicate()
  status = process.poll()
  
  return output, stderr, status

def sort_systems(systems_list):
  """
  Sorts systems according to their energy
  
  """
  
  systems_list_len = len(systems_list)

  for i in range(systems_list_len):
    for j in range(systems_list_len):
      if systems_list[i].totalEnergy < systems_list[j].totalEnergy:
        temp = copy.deepcopy(systems_list[i])
        
        systems_list[i] = copy.deepcopy(systems_list[j])
        systems_list[j] = copy.deepcopy(temp)
    
    if (i % 100 == 0): print "Sorting %d/%d" % (i+1, systems_list_len)

def systems_statistics(systems_list, dir_path=None):
  """
  Generates statistics about the FHI-aims simulations
    
  """
  
  if dir_path is None:
    f = open(_systems_stats_file, "w")
  else:
    f = open(os.path.join(dir_path, _systems_stats_file), "w")
  
  f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % ("System", "Energy", "Hashkey", "Cores", 
          "Time", "Tot.Time", "H-L", 
          "VBM", "VBMOcc", "VBMSpinChannel", 
          "CBM", "CBMOcc", "CBMSpinChannel", 
          "SpinN", "SpinS", "SpinJ","Size"))
  
  for system in systems_list:
    f.write("%s,%f,%s,%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % (system.name, system.totalEnergy, system.hashkey,
                                     system.noOfcores, system.runTime, system.noOfcores*system.runTime,
                                     system.homo_lumo_gap, system.vbm, system.vbm_occ_num, system.vbm_spin_chan, 
                                     system.cbm, system.cbm_occ_num, system.cbm_spin_chan, 
                                     system.spin_N, system.spin_S, system.spin_J, float(system.NAtoms)))
    
    
  f.close()