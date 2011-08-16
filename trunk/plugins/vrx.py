#
# File created July 30th 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 17th 2011 by Fabien Tricoire
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
                    self.nodes[self.locationIDToIndex[tokens[1]]]['is depot'] =\
                        False
                elif section == 'request times':
                    pass

# load a solution file produced by indigo
class VRXSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    solutionType = 'indigo'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # route attributes in a solution file produced by indigo
        self.routeAttributes += [ 'vehicle', 'vehicle type', 'ID' ]
        # it is possible to visit several times the same node for different
        # requests
        self.routeNodeAttributes += [ 'request' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        thisRoute = None
        stage = None
        # process each line
        for rawLine in file(fName):
            # remove the comments
            line = rawLine[:rawLine.find('#')].rstrip()
            tokens = line.split()
            if len(tokens) < 2:
                continue
#             print tokens
            # case of a new vehicle
            if tokens[0] == 'Vehicle':
                currentVehicle = tokens[1]
            # case of a new route for this vehicle
            elif tokens[0] == 'Route':
                currentRoute = tokens[1]
            elif tokens[0] == 'Cost':
                currentCost = string.atoi(tokens[1])
            elif tokens[0] == 'Start:':
                currentStartTime = string.atoi(tokens[1])
            elif tokens[0] == 'Finish:':
                currentFinishTime = string.atoi(tokens[1])
            elif tokens[0] == 'Duration:':
                currentDuration = string.atoi(tokens[1])
            elif tokens[0] == 'Capacity:':
                currentCapacity = string.atoi(tokens[1])
            elif tokens[0] == 'Max' and tokens[1] == 'Load:':
                currentMaxLoad = string.atoi(tokens[2])
            # we already read the last route -> add it and exit
            elif tokens[0] == 'Unassigned' and tokens[1] != 'cost':
                self.routes.append(thisRoute)
                return
            # case of a new route
            elif tokens[0] == 'Count':
                stage = 'route'
                # append previous route if any
                if not thisRoute is None:
                    self.routes.apped(thisRoute)
                # create new route
                thisRoute = { 'index': len(self.routes),
                              'ID': currentRoute,
                              'vehicle': currentVehicle,
                              'vehicle type': currentVehicle,
                              'cost': currentCost,
                              'starting time': currentStartTime,
                              'finishing time': currentFinishTime,
                              'duration': currentDuration,
                              'capacity': currentCapacity,
                              'max. load': currentMaxLoad,
                              'node information': [],
                              }
#                 # add fields to route node attributes if they're not there yet
#                 for field in tokens[3:]:
#                     if not field in self.routeNodeAttributes:
#                         self.routeNodeAttributes.append(field)
                # use these fields for reading the route
                currentFields = tokens
            # case where we read information for one node
            elif stage == 'route':
                # special case: end of the route
                if tokens[0] == '(End)':
                    tokens = [ None ]  + tokens
                thisNode = { 'index': vrpData.locationIDToIndex[tokens[2]],
                             'request': tokens[1] }
                if tokens[1] != '(Start)':
                    for field, value in zip (currentFields[3:], tokens[3:]):
                        prevField = field
                        if field == 'Arrive':
                            thisNode['arrival time'] = string.atoi(value)
                        elif field == 'LateArr':
                            thisNode['latest arrival time'] = string.atoi(value)
                        elif field == 'Wait':
                            thisNode['waiting time'] = string.atoi(value)
                        elif field == 'Start':
                            thisNode['service start'] = string.atoi(value)
                        elif field == 'Depart':
                            thisNode['departure time'] = string.atoi(value)
                        elif field == 'Cumm' and prevField == 'load':
                            thisNode['load'] = string.atoi(value)
                # finally add the node to current route
                thisRoute['node information'].append(thisNode)

# load a solution file produced by indigo
class VRX_CSVSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    solutionType = 'csv'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # route attributes in a solution file produced by indigo
        self.routeAttributes += [ 'vehicle', 'ID' ]
        # it is possible to visit several times the same node for different
        # requests
        self.routeNodeAttributes += [ 'request' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        thisRoute = None
        stage = None
        # process each line
        for rawLine in file(fName):
            tokens = rawLine.split(',')
            if len(tokens) < 2:
                continue
#             print tokens
            # case of a new route
            if tokens[0] == 'Route':
                thisRoute = { 'index': len(self.routes),
                              'ID': tokens[1],
                              'node information': [],
                              }
            # vehicle for this route
            elif tokens[0] == 'Vehicle':
                thisRoute['vehicle'] = tokens[1]
            elif tokens[0] == 'Total' and tokens[1] == 'cost':
                thisRoute['cost'] = string.atoi(tokens[2])
            # case of a new route
            elif len(tokens) > 2 and tokens[2] == 'Customer':
                stage = 'route'
                # use these fields for reading the route
                currentFields = tokens
            # case where we read information for one node
            elif stage == 'route':
                if tokens[2] == '':
                    continue
                thisNode = { 'index': vrpData.locationIDToIndex[tokens[3]],
                             'request': tokens[2] }
                for field, value in zip (currentFields[4:], tokens[4:]):
                    if tokens[2] != '(Start)' and tokens[2] != '(End)':
                        if field == 'Arrive':
                            thisNode['arrival time'] = value
                        elif field == 'Wait':
                            thisNode['waiting time'] = value
                        elif field == 'Start':
                            thisNode['service start'] = value
                        elif field == 'Leave':
                            thisNode['departure time'] = value
                        elif field == 'Late-Start':
                            thisNode['latest arrival time'] = value
                # finally add the node to current route
                thisRoute['node information'].append(thisNode)
                # special case: end of the route
                if tokens[2] == '(End)':
                    self.routes.append(thisRoute)
                    stage = None

# load a .rt file
class VRXRouteSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    solutionType = '.rt'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # route attributes for a .rt file
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
        self.styles.append(basestyles.NodeDisplayer({'node size': 3,
                                                     'hide unused nodes': True,
                                                     }))
        # display a label for each node
        self.styles.append(basestyles.NodeLabelDisplayer({'hide unused nodes':
                                                              True,
                                                          }))
        # display each node's demand
        self.styles.append(basestyles.NodeDemandDisplayer({'hide unused nodes':
                                                              True,
                                                          }))
