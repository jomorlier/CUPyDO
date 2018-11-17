#!/usr/bin/env python
# -*- coding: utf-8; -*-

"""
Copyright 2018 University of Liège
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. 

@file FlowInterface.py
@brief Python interface between Flow and CUPyDO.
@author A. Crovato
"""

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import os, os.path, sys, time, string

import math
import numpy as np
from cupydo.genericSolvers import FluidSolver

# ----------------------------------------------------------------------
#  FlowSolver class
# ----------------------------------------------------------------------

class Flow(FluidSolver):
    def __init__(self, _case):       
        # load the python module
        case = __import__(_case)
        
        # load the case (contains flow and some of its objects)
        # TODO: check what needs to be passed to getFlow
        self.flow = case.getFlow()

        # get the f/s boundary
        self.boundary = self.flow.boundary

        # number of nodes
        self.nNodes = self.boundary.nodes.size()
        self.nHaloNode = 0
        self.nPhysicalNodes = self.nNodes - self.nHaloNode

        # nodal load
        self.nodalLoad_X = np.zeros(self.nPhysicalNodes)
        self.nodalLoad_Y = np.zeros(self.nPhysicalNodes)
        self.nodalLoad_Z = np.zeros(self.nPhysicalNodes)

        # initialize
        self.exeOK = True
        FluidSolver.__init__(self)
        
    def run(self):
        """
        Run the solver for one steady (time) iteration.
        """

        self.exeOK = self.flow.solver.execute()
        self.__setCurrentState()
    
    def __setCurrentState(self):
        """
        Compute nodal forces from nodal Pressure coefficient
        """

        # integrate Cp at element
        cpiE = self.boundary.integrate(self.flow.solver.phi, self.flow.fCp)
        # interpolate integrated Cp from elements to nodes
        cfN = self.boundary.interpolate(cpiE)
        i = 0
        for n in self.boundary.nodes:
            self.nodalLoad_X[i] = self.flow.dynP * cfN[i][0]
            self.nodalLoad_Y[i] = self.flow.dynP * cfN[i][1]
            self.nodalLoad_Z[i] = self.flow.dynP * cfN[i][2]
            i += 1

    def getNodalInitialPositions(self):
        """
        Get the initial position of each node
        """
        
        x0 = np.zeros(self.nPhysicalNodes)
        y0 = np.zeros(self.nPhysicalNodes)
        z0 = np.zeros(self.nPhysicalNodes)
        for i in range(self.boundary.nodes.size()):
            n = self.boundary.nodes[i]               
            x0[i] = n.pos.x[0]
            y0[i] = n.pos.x[1]
            z0[i] = n.pos.x[2]

        return (x0, y0, z0)

    def getNodalIndex(self, iVertex):
        """
        Get index of each node
        """

        no = self.boundary.nodes[iVertex].no
        return no

    def applyNodalDisplacements(self, dx, dy, dz):
        """
        Apply displacements coming from solid solver to f/s interface
        """

        for i in range(self.boundary.nodes.size()):
            self.boundary.nodes[i].pos.x[0] += dx[i]
            self.boundary.nodes[i].pos.x[1] += dy[i]
            self.boundary.nodes[i].pos.x[2] += dz[i]

    def remeshing(self):
        """
        TODO Lagrangian remeshing
        """

    def fakeSolidSolver(self):
        """
        Dummy solid solver for testing
        Apply dummy displacement
        """

        dxD = np.zeros(self.nPhysicalNodes)
        dyD = np.zeros(self.nPhysicalNodes)
        dzD = np.zeros(self.nPhysicalNodes)
        self.applyNodalDisplacements(dxD, dyD, dzD)           
        
    def update(self):
        """
        TODO
        """
        
    def save(self):
        """
        Save data on disk at each converged fsi iteration
        """
        self.flow.solver.finalize()

    def initRealTimeData(self):
        """
        TODO
        """

    def saveRealTimeData(self, time, nFSIIter):
        """
        Save data on disk...
        """

    def printRealTimeData(self, time, nFSIIter):
        """
        Print data on screen...
        """
        
        #print toPrint
    
    def exit(self):
        """
        Exit the Flow solver.
        """
        
        print("***************************** Exit Flow *****************************")
