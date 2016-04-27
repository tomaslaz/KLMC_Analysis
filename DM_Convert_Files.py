#!/usr/bin/env python

"""
A script to convert files. Works with XYZ, CAR, and GIN formats.

@author Tomas Lazauskas, 2016
@web www.lazauskas.net
@email tomas.lazauskas[a]gmail.com
"""

import glob
import os
import sys
import numpy as np
from optparse import OptionParser

import source.Atoms as Atoms
import source.IO as IO

class Cluster(object):
  """
  A class to save the structure of a cluster.
  
  NAtoms: number of atoms in cluster (N)
  specie[N]: array of symbols of atoms
  pos[3N]: array of positions of atoms
  charge[N]: array of charges of atoms
  
  """
    
  def __init__(self, NAtoms):
      
    self.totalEnergy = 0.0
    self.NAtoms = NAtoms
    self.cellDims = np.zeros(3, np.float64)
    self.cellAngles = np.empty(3, np.float64)
    
    self.specie = np.empty(self.NAtoms, np.int32)
    self.pos = np.empty(3*self.NAtoms, np.float64)
    self.minPos = np.empty(3, np.float64)
    self.maxPos = np.empty(3, np.float64)
    
    self.charge = np.empty(self.NAtoms, np.float64)
    
    self.com = np.empty(3, np.float64)
    self.momentOfInertia = np.zeros([3, 3], np.float64)
    
    dt = np.dtype((str, 2))
    self.specieList = np.empty(0, dt)
    self.specieCount = np.empty(0, np.int32)
    
    self.PBC = np.zeros(3, np.int32)
    
    self.gulpSpecies = {}
        
  def addAtom(self, sym, pos, charge):
    """
    Add an atom to the cluster
    
    """
    
    if sym not in self.specieList:
        self.addSpecie(sym)
    
    specInd = self.specieIndex(sym)
    
    self.specieCount[specInd] += 1
    
    pos = np.asarray(pos, dtype=np.float64)
    
    self.specie = np.append(self.specie, np.int32(specInd))
    self.pos = np.append(self.pos, pos)
    self.charge = np.append(self.charge, charge)

    self.NAtoms += 1
    
  def calcCOM(self):
      
    """
    Calculates the centre of mass of a cluster
    
    """
    
    totMass = 0.0
    self.com[:] = 0.0
    
    for i in range(self.NAtoms):
      atomMass = Atoms.atomicMassAMU(self.specieList[self.specie[i]])
      totMass += atomMass
      
      for j in range(3):
        self.com[j] += atomMass * self.pos[3*i + j]

    self.com = self.com / totMass
  
  def calcMOI(self):
    """
    Calculates moment of inertia
    
    """
    
    moi = np.zeros(6, np.float64)

    
    self.momentOfInertia[:] = 0.0
    
    for i in range(self.NAtoms):
      atomMass = Atoms.atomicMassAMU(self.specieList[self.specie[i]])
        
      moi[0] += (self.pos[3*i+1]**2 + self.pos[3*i+2]**2) * atomMass
      moi[1] += (self.pos[3*i+0]**2 + self.pos[3*i+2]**2) * atomMass
      moi[2] += (self.pos[3*i+0]**2 + self.pos[3*i+1]**2) * atomMass
      moi[3] += -(self.pos[3*i+0] * self.pos[3*i+1]) * atomMass
      moi[4] += -(self.pos[3*i+0] * self.pos[3*i+2]) * atomMass
      moi[5] += -(self.pos[3*i+1] * self.pos[3*i+2]) * atomMass
    
    self.momentOfInertia[0][0] = moi[0]
    self.momentOfInertia[1][1] = moi[1]
    self.momentOfInertia[2][2] = moi[2]
    
    self.momentOfInertia[0][1] = moi[3]
    self.momentOfInertia[0][2] = moi[4]
    
    self.momentOfInertia[1][0] = moi[3]
    self.momentOfInertia[1][2] = moi[5]
    
    self.momentOfInertia[2][0] = moi[4]
    self.momentOfInertia[2][1] = moi[5]
  
  def rotateToMOI(self, basis):
    
    for i in range(self.NAtoms):
      for j in range(3):
        elSum = 0.0
        
        for k in range(3):
          elSum += self.pos[3*i+k] * basis[k][j]

        self.pos[3*i+j] = elSum
      
  def moveToCOM(self):
    """
    Centers the cluster on the centre of of mass.
    
    """
    
    for i in range(self.NAtoms):
      for j in range(3):
        self.pos[3*i + j] -= self.com[j]
      
  def removeAtom( self, index ):
    """
    Remove an atom from the structure
    
    """
    
    specInd = self.specie[index]
    self.specie = np.delete(self.specie, index)
    self.pos = np.delete(self.pos, [3*index,3*index+1,3*index+2])
    self.charge = np.delete(self.charge, index)

    self.NAtoms -= 1
    
    self.specieCount[specInd] -= 1
    if self.specieCount[specInd] == 0 and not self.specieListForced:
        self.removeSpecie(specInd)
  
  def removeSpecie(self, index):
    """
    Remove a specie from the specie list.
    
    """
    self.specieCount = np.delete(self.specieCount, index)
    self.specieList = np.delete(self.specieList, index)
    
    for i in xrange(self.NAtoms):
        if self.specie[i] > index:
            self.specie[i] -= 1

  def specieIndex(self, check):
    """
    Index of sym in specie list
    
    """
    
    count = 0
    index = -1
    for sym in self.specieList:
        if sym == check:
            index = count
            break
        
        count += 1
    
    return index 
  
  def addSpecie(self, sym, count=None):
    """
    Add specie to specie list
    
    """
            
    if sym in self.specieList:
        if count is not None:
            specInd = self.specieIndex(sym)
            self.specieCount[specInd] = count
        
        return
    
    if count is None:
        count = 0
    
    self.specieList = np.append(self.specieList, sym)
    self.specieCount = np.append(self.specieCount, np.int32(count))
    
  def minMaxPos(self, PBC):
      
    for i in xrange(3):
        if not PBC[i]:
            self.minPos[i] = self.pos[i::3].min()
            self.maxPos[i] = self.pos[i::3].max()

def cmdLineArgs():
  """
  Handles command line arguments and options.
  
  """
  
  usage = "usage: %prog inputFile outputFile"
  
  parser = OptionParser(usage=usage)

  parser.disable_interspersed_args()
      
  (options, args) = parser.parse_args()

  if (len(args) < 2 and len(args) > 3):
    parser.error("incorrect number of arguments")

  return options, args

def convertFile(cluster, outFile, controlFile=None):
  """
  Saves a cluster in to a file according to the file format
  
  """
  error = ""
  success = True
  
  if outFile.endswith(".xyz"):
    success, error = IO.writeXYZ(cluster, outFile)
    
  elif outFile.endswith(".car"):
    success, error = IO.writeCAR(cluster, outFile)
    
  elif outFile.endswith(".gin"):
    success, error = IO.writeGIN(cluster, outFile, controlFile=controlFile)
    
  else:
    error = "Undefined output format"
    success = False
    
  return success, error
    
if __name__ == "__main__":
  
  ok = 1
  error = ""
  
  _, args = cmdLineArgs()
  
  inFileName = args[0]
  outFileName = args[1]
  
  if (len(args) > 2):
    controlFile = args[2]
  else:
    controlFile = None
    
  if inFileName[-3:] == outFileName[-3:]:
    sys.exit("Formats must differ!")
  
  if inFileName == ".gin":
    fileList = glob.glob("*.gin")
      
    for fileName in fileList:
      cluster, error = IO.readClusterFromFileGIN(fileName)
        
      outputFile = fileName[:-3] + outFileName[-3:]
      
      ok, error = convertFile(cluster, outputFile, controlFile)
  
  elif inFileName == ".car":
    fileList = glob.glob("*.car")
    
    for fileName in fileList:
      
      cluster = IO.readClusterFromFileCAR(fileName)
       
      outputFile = fileName[:-3] + outFileName[-3:]
      
      ok, error = convertFile(cluster, outputFile, controlFile)
  
  elif inFileName == ".xyz":
    fileList = glob.glob("*.xyz")
    
    for fileName in fileList:
      cluster = IO.readClusterFromFileXYZ(fileName)
        
      outputFile = fileName[:-3] + outFileName[-3:]
      
      ok, error = convertFile(cluster, outputFile, controlFile)
    
  else:
    
    if inFileName.endswith(".xyz"):
      cluster = IO.readClusterFromFileXYZ(inFileName)
      
    elif inFileName.endswith(".car"):
      cluster = IO.readClusterFromFileCAR(inFileName)
    
    elif inFileName.endswith(".gin"):
      cluster, error = IO.readClusterFromFileGIN(inFileName)
    
    else:
      print "Unrecognised input file ", inFileName, " format"
      sys.exit()
      
    ok, error = convertFile(cluster, outFileName, controlFile)
    
    if ok:
      print "Finished!"
    
    else:
      print "Error: ", error
      