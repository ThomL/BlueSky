""" 
Datalog class definition : Data logging class

Methods:
    Datalog(filename)  : constructor

    write(txt)         : add a line to the datalogging buffer
    save()             : save data to file
   
Created by  : Jacco M. Hoekstra (TU Delft)
Date        : October 2013

Modifation  :   - added start method including command processing
                - added CSV-style saving
By          : P. Danneels
Date        : April 2016

"""
import os
import numpy as np
from misc import tim2txt
from time import strftime, gmtime

#-----------------------------------------------------------------


class Datalog():
    def __init__(self, sim):
        self.sim = sim
        # Create a buffer and save filename
        self.fname = os.path.dirname(__file__) + "/../../data/output/" \
            + strftime("%Y-%m-%d-%H-%M-%S-BlueSky.txt", gmtime())
        self.buffer = ["time;acid;gs;vs;track;lat;long\n"]  # Log data
        self.aclist = np.zeros(1)                                 # AC list to log
        self.dt = 1.                                              # Default logging interval
        self.t0 = -9999                                           # Timer
        self.swlog = False                                        # Logging started
        return

    def start(self, acbatch, dt):
        if len(self.sim.traf.id) == 0:
            return False, "LOG: No traffic present, log not started."
        self.id2idx = np.vectorize(self.sim.traf.id2idx)  # vectorize function
        if acbatch is None:  # No batch defined, log all
            self.aclist = self.id2idx(self.sim.traf.id)
        elif acbatch == 'AREA':
            if self.sim.traf.swarea:
                self.aclist = self.id2idx(self.sim.traf.id)
            else:
                return False, "LOG: AREA DISABLED, LOG NOT STARTED"
        else:
            idx = self.id2idx(acbatch)
            if idx < 0:  # not an acid or ac does not exist
                return False, "LOG: ACID " + acbatch + " NOT FOUND"
            else:
                self.aclist = idx
        self.dt = dt
        if self.aclist.any():
            self.swlog = True
        return True, "LOG started."

    def update(self, sim):
        if not self.swlog:                     # Only update when logging started an traffic is selected
            return
        if abs(sim.simt - self.t0) < self.dt:  # Only do something when time is there
            return
        self.t0 = sim.simt                     # Update time for scheduler

        t = tim2txt(sim.simt)                  # Nicely formated time

        if self.aclist.ndim < 1:               # Write to buffer for one AC
            self.writebuffer(sim, t, self.aclist)
        else:                                  # Write to buffer for multiple AC
            for i in self.aclist:
                self.writebuffer(sim, t, self.aclist[i])
        return

    def writebuffer(self, sim, t, idx):
        self.buffer.append(t + ";" +
                           str(sim.traf.id[idx]) + ";" +
                           str(sim.traf.gs[idx]) + ";" +
                           str(sim.traf.vs[idx]) + ";" +
                           str(sim.traf.trk[idx]) + ";" +
                           str(sim.traf.lat[idx]) + ";" +
                           str(sim.traf.lon[idx]) + "\n")
        return

    def save(self):  # Write buffer to file
        f = open(self.fname, "w")
        f.writelines(self.buffer)
        f.close()
        return
