"""
Messages module.

@author Tomas Lazauskas, 2016
@web www.lazauskas.net
@email tomas.lazauskas[a]gmail.com
"""

import datetime
import Constants

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def error(caller, message, indent=0, verbose=1):
  """
  Prints an error message in a predefined format
  
  """
  
  if verbose == 0:
    return
        
  now = datetime.datetime.now().strftime("%d/%m/%y, %H:%M:%S")
  ind = ""
  for _ in range(indent):
      ind += "  "
  print ("[%s]: %s%s%s >> %s%s" % (now, bcolors.FAIL, ind, caller, message, bcolors.ENDC))

def log(caller, message, indent=0, verbose=1):
  """
  Prints a log message in a predefined format
  
  """
  
  if verbose == 0:
    return
   
  now = datetime.datetime.now().strftime("%d/%m/%y, %H:%M:%S")
  ind = ""
  for _ in range(indent):
      ind += "  "
  print ("[%s]: %s%s >> %s" % (now, ind, caller, message))

def warning(caller, message, indent=0, verbose=1):
  
  if verbose > Constants.verbosity:
    return
        
  now = datetime.datetime.now().strftime("%d/%m/%y, %H:%M:%S")
  ind = ""
  for _ in range(indent):
      ind += "  "
  print ("[%s]: %s%s%s >> %s%s" % (now, bcolors.WARNING, ind, caller, message, bcolors.ENDC))

def printAuthor(verbose=1):
  """
  Prints the authors name and the year
  
  """
  
  if verbose == 0:
    return
    
  print (bcolors.WARNING +"Written by" + bcolors.ENDC + " " + bcolors.OKGREEN + "Tomas Lazauskas" + 
         bcolors.ENDC + " " + bcolors.FAIL + "2016-2017" + bcolors.ENDC)
