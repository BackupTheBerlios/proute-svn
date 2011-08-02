#
# File created July 30th 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 31st 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-

import string

import vrpdata
import stylesheet

class VRXInputData(vrpdata.VrpInputData):    
    problemType = 'VRX'
    # load a VRX instance
    def loadData(self, fName):
        self.nodeAttributes += [ 'demand', 'release time', 'due date',
                                 'service time', 'request type' ]
        self.globalAttributes += [ 'capacity', 'maximum duration' ]
        self.nodes = []
        self.attributes = {}
        section = None
        self.locationIDToIndex = {}
        # read a section at a time
        for rawLine in file(fName):
            # remove the comments
            line = rawLine[:rawLine.find('#')].rstrip()
            # empty lines
            if len(line) == 0: continue
            # end of a section
            elif line == '*END*':
                section = None
            # beginning of a section
            elif section is None:
                keyword = line.split()[0]
                if keyword == 'VRX':
                    section = 'header'
                # one-line header-type information
                elif keyword[4:] == '_METRIC':
                    pass
                # location section
                elif keyword == 'LOCATIONS':
                    section = 'locations'
                elif keyword == 'VEHICLES':
                    section = 'vehicles'
                elif keyword == 'VEHICLE_COST':
                    section = 'ignored'
                elif keyword == 'ROUTES':
                    section = 'vehicle availabilities'
                elif keyword == 'REQUESTS':
                    section = 'requests'
                elif keyword == 'REQUEST_TIMES':
                    section = 'request times'
            # case where we read a normal line in the file
            elif section != 'ignored':
                tokens = line.split()
                # section-dependent actions
                if section == 'header':
                    if tokens[0] == 'NAME':
                        self.name = tokens[1]
                elif section == 'locations':
                    thisNode = { 'label': tokens[0],
                                 'index': len(self.nodes),
                                 'x': string.atof(tokens[1]),
                                 'y': string.atof(tokens[2]),
                                 'is depot': True }
                    self.locationIDToIndex[tokens[0]] = len(self.nodes)
                    self.nodes.append(thisNode)
                elif section == 'vehicles':
                    pass
                elif section == 'routes':
                    pass
                elif section == 'requests':
                    self.nodes[self.locationIDToIndex[tokens[0]]]['is depot'] =\
                        False
                elif section == 'request times':
                    pass
            
class VRXSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence',
                                  'vehicle', 'vehicle type', 'ID' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        # process each line
        for rawLine in file(fName):
            # remove the comments
            line = rawLine[:rawLine.find('#')].rstrip()
            if line[:9] == 'Route-Veh':
                tokens = line.split()
                thisRoute = { 'index': len(self.routes),
                              'ID': tokens[1],
                              'vehicle': tokens[2],
                              'vehicle type': tokens[2][tokens[2].find('-'):],
                              }
                
                sequence = tokens[3:]
                thisRoute['node sequence'] =  [ vrpData.locationIDToIndex[i]
                                                for i in sequence ]
                self.routes.append(thisRoute)
            
# style for displaying VRX data
class VRXStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'VRX' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display each route
        self.styles.append(\
            basestyles.RouteDisplayer({'draw depot arcs': True}))
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({'node size': 3}))
        # display a label for each node
        self.styles.append(basestyles.NodeLabelDisplayer())
        # display each node's demand
        self.styles.append(basestyles.NodeDemandDisplayer())
