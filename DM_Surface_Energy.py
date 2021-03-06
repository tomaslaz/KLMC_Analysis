"""
A script to calculate surface energy for a cluster.

@author Tomas Lazauskas, 2017
@web www.lazauskas.net
@email tomas.lazauskas[a]gmail.com
"""

import os
import sys

from optparse import OptionParser

import source.IO as IO
from source.Messages import log

# verbose level: 0 - off, 1 - on
_verbose = 1

def cmd_line_args():
  """
  Handles command line arguments and options.
  
  """
  
  usage = "usage: %prog input_file radius energy"
  
  parser = OptionParser(usage=usage)
  
  parser.disable_interspersed_args()
  
  (options, args) = parser.parse_args()
    
  if (len(args) != 3):
    parser.error("incorrect number of arguments")

  return options, args

if __name__ == "__main__":
  
  # reading in input arguments
  options, args = cmd_line_args()
  
  file_name = args[0]
  radius = float(args[1])
  n1_bulk_energy = float(args[2])
  
  message = "reading file: %s" % (file_name)
  log(__name__, message, verbose=_verbose)
  
  system = IO.readSystemFromFileXYZ(file_name)
  
  # estimating the geometrical measurements
  system.calc_geo_measures(radius)
  
  message = "Volume: %f, Area: %f, Spheres: %d" % (system.arvo_volume, system.arvo_area, system.arvo_spheres)
  log(__name__, message, verbose=_verbose)
  
  # estimating the surface energy
  try:
    surface_energy = (system.totalEnergy - system.NAtoms * n1_bulk_energy) / system.arvo_area
  except:
    surface_energy = 0.0
  
  message = "Surface energy (E/A): %f" % (surface_energy)
  log(__name__, message, verbose=_verbose)
  