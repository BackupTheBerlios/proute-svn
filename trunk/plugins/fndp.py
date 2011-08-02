#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import string
import sys

import vrpdata
import stylesheet

class FNDPInputData(vrpdata.VrpInputData):
    problemType = 'FNDP'
    # load a free newspaper delivery problem
    def loadData(self, fName):
        self.nodeAttributes += [ 'demand', 'capacity' ]
        self.nodes = []
        self.attributes = {'# periods': 0}
        # load a MCDARP instance
        for line in file.readlines(file(fName)):
            if line[0] == '#':
                continue
            else:
                tokens = line.split(';')
                if len(tokens) == 7:
                    self.attributes['nNodes'], self.attributes['# periods'], \
                        nVehicles, self.attributes['capacity'], \
                        self.attributes['service time'], \
                        self.attributes['depot ID'], \
                        self.attributes['period duration'] = [ string.atoi(x)
                                                               for x in tokens ]
                elif len(tokens) == self.attributes['# periods'] and \
                        not 'production schedule' in self.attributes:
                    self.attributes['production schedule'] = [ string.atoi(x)
                                                               for x in tokens ]
                elif len(tokens) == 5:
                    thisNode = {}
                    thisNode['index'] = string.atoi(tokens[0])
                    thisNode['label'] = string.atoi(tokens[0])
                    thisNode['demand'], thisNode['x'], thisNode['y'], \
                        thisNode['capacity'] = [ string.atof(x)
                                                 for x in tokens[1:] ]
                    thisNode['is depot'] = \
                        thisNode['index'] == self.attributes['depot ID']
                    self.nodes.append(thisNode)

class FNDPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'FNDP'
    # load a free newspaper solution by Archetti et al.
    def loadData(self, fName, vrpData):
        self.routeAttributes += [ 'starting time' ]
        self.routeNodeAttributes += [ 'quantity' ]
        self.routes = []
        for line in file.readlines(file(fName)):
            tokens = line.split()
            if tokens[0] == '***':
                continue
            elif tokens[1] != 'Trip':
                print 'incorrect file format'
                print line
                sys.exit(0)
            else:
                nodes = [ string.atoi(x.split('(')[0])
                          for x in tokens[6:-3] ]
                rest = [ x.split('(')[1][:-1].split(':') for x in tokens[6:-3] ]
                period = [ string.atoi(x[0]) for x in rest ]
                qty = [ string.atoi(x[1]) for x in rest ]
                startingTime = string.atoi(tokens[5][:-1])
                routeNodes = [ {'index': node, 'quantity': quantity,
                                'period': period}
                               for node, quantity, period in
                               zip(nodes, qty, period) ]
                thisRoute = {'index': len(self.routes),
                             'node sequence': nodes,
                             'node information': routeNodes,
                             'starting time': startingTime }
                self.routes.append(thisRoute)

class FNDPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'FNDP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display each route
        self.styles.append(basestyles.RouteColourDisplayer(\
                {'draw depot arcs':True,
                 'attribute': 'index',
                 'thickness': 1} ) )
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({'node size': 2}))
#         # display a label for each node
#         self.styles.append(basestyles.NodeLabelDisplayer())
