#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 18th 2011 by Fabien Tricoire
#
from style import *

import colours
import shapes

# This module contains flexible, general-purpose styles: they can be reused for
# different purposes and are not restrictive when it comes to required
# attributes.

# Display an interval within a bigger interval. The bigger interval is set by
# taking extreme values over the whole instance for both attributes setting the
# bounds of the subinterval to display.
# The default values for these two attributes allow to use this style directly
# for time window representation.
class FlexibleSubInterval(Style):
    description = 'interval as a rectangle'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'x offset': IntParameterInfo(-40, 20),
        'y offset': IntParameterInfo(-20, 40),
        'thickness': IntParameterInfo(0, 20),
        'width': IntParameterInfo(6, 200),
        'height': IntParameterInfo(3, 60),
        'contour colour': colourInfo,
        'background colour': colourInfo,
        'time window colour': colourInfo,
        }
    defaultValue = {
        'x offset': 4,
        'y offset': 4,
        'thickness': 1,
        'width': 20,
        'height': 7,
        'contour colour': colours.black,
        'background colour': colours.white,
        'time window colour': colours.dimcyan,
        'left bound attribute': 'release time',
        'right bound attribute': 'due date',
        }
    def initialise(self):
        # parameter info for these needs to be computed later when the data
        # format is known
        self.timeToX = None

    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'width':
            self.timeToX = util.intervalMapping(self.earliest,
                                                self.latest,
                                                0.0,
                                                self.parameterValue['width'])
        
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only block
        if not 'left bound attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['right bound attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
            self.parameterInfo['left bound attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
        # only perform painting if the selected attributes are available
        if not (self.parameterValue['right bound attribute'] in \
                    inputData.nodeAttributes and \
                    self.parameterValue['left bound attribute'] in \
                    inputData.nodeAttributes):
            return
        if self.timeToX is None:
            self.earliest = \
                min( [ x[self.parameterValue['left bound attribute']]
                       for x in inputData.nodes ], 0 )
            self.latest = max( [ x[self.parameterValue['right bound attribute']]
                                 for x in inputData.nodes ] )
            self.timeToX = util.intervalMapping(self.earliest, self.latest,
                                                0.0,
                                                self.parameterValue['width'])
        # now we can display everything we want
        # for each node display its background
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['background colour'],
                             self.parameterValue['background colour'],
                             lineThickness=self.parameterValue['thickness'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'])
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')
        # then display the TWs
        rtParam = self.parameterValue['left bound attribute']
        ddParam = self.parameterValue['right bound attribute']
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['time window colour'],
                             self.parameterValue['time window colour'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'] +
                        self.timeToX(node[rtParam]))
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            
            allW.append(max(1,
                            self.timeToX(node[ddParam]) -
                            self.timeToX(node[rtParam])))
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')
        # then the border around
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['contour colour'],
                             lineThickness=self.parameterValue['thickness'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'])
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')

# Display a rectangle proportional to the demand for each node
class NodeAttributeAsRectangleDisplayer( Style ):
    description = 'small bar for attribute'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = {
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'width': IntParameterInfo(2, 20),
        'max. height': IntParameterInfo(5, 200),
        'colour': ColourParameterInfo(),
        }
    defaultValue = {
        'x offset': -5,
        'y offset': 4,
        'width': 4,
        'min. height': 1,
        'max. height': 20,
        'colour': colours.darkorange,
        'attribute': 'demand',
        }
    def initialise(self):
        self.minValue = None
    #
    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'max. height' or parameterName == 'attribute':
            self.minValue = None
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
        # only perform painting if the selected attributes are available
        if not self.parameterValue['attribute'] in inputData.nodeAttributes:
            return
        # first compute min and max demand if it's the first time we're here
        if self.minValue is None:
            values = [ node[self.parameterValue['attribute']]
                        for node in inputData.nodes ]
            self.minValue, self.maxValue = min(values), max(values)
            self.computeHeight =\
                util.intervalMapping(self.minValue, self.maxValue,
                                     self.parameterValue['min. height'],
                                     self.parameterValue['max. height'])
        # second only continue if an attribute is specified
        allX, allY, allW, allH = [], [], [], []
        for node in inputData.nodes:
            if (nodePredicate and not nodePredicate(node)) or node['is depot']:
                continue
            else:
                allX.append(convertX(node['x']) +
                            self.parameterValue['x offset'])
                allY.append(convertY(node['y']) +
                            self.parameterValue['y offset'])
                allW.append(self.parameterValue['width'])
                allH.append(self.computeHeight(\
                        node[self.parameterValue['attribute']]))
        style = DrawingStyle(self.parameterValue['colour'],
                             self.parameterValue['colour'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southeast')

# Display a list of rectangles proportional to cell value of given list
# attribute for each node
class NodeListAttributeAsRectanglesDisplayer(NodeAttributeAsRectangleDisplayer):
    description = 'small bars for list attribute'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = {
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'padding': IntParameterInfo(0, 60),
        'width': IntParameterInfo(2, 20),
        'max. height': IntParameterInfo(5, 200),
        'colours': ColourMapParameterInfo(),
        }
    defaultValue = {
        'x offset': -5,
        'y offset': 5,
        'padding': 2,
        'width': 4,
        'min. height': 1,
        'max. height': 20,
        'colours': generateRandomColours(100),
        'attribute': '',
        }
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'attribute' in self.parameterInfo:
            def acceptable(x):
                return isinstance(x, list) and \
                    (isinstance(x[0], int) or isinstance(x[0], float))
            self.parameterInfo['attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
        # only perform painting if the selected attributes are available
        if not self.parameterValue['attribute'] in inputData.nodeAttributes:
            return
        # first compute min and max demand if it's the first time we're here
        if not self.minValue:
            values = [ max(node[self.parameterValue['attribute']])
                       for node in inputData.nodes ]
            self.minValue, self.maxValue = min(values), max(values)
            self.computeHeight =\
                util.intervalMapping(self.minValue, self.maxValue,
                                     self.parameterValue['min. height'],
                                     self.parameterValue['max. height'])
        # second only continue if an attribute is specified
        # we use a different colour (hence style) for each item
        nElements = len(inputData.nodes[0][self.parameterValue['attribute']])
        for i in range(nElements):
            allX, allY, allW, allH = [], [], [], []
            for node in inputData.nodes:
                if (nodePredicate and not nodePredicate(node)) or \
                        node['is depot']:
                    continue
                else:
                    allX.append(convertX(node['x']) +
                                self.parameterValue['x offset'] +
                                i * (self.parameterValue['width'] +
                                     self.parameterValue['padding']))
                    allY.append(convertY(node['y']) +
                                self.parameterValue['y offset'])
                    allW.append(self.parameterValue['width'])
                    allH.append(self.computeHeight(\
                            node[self.parameterValue['attribute']][i]))
            style = DrawingStyle(self.parameterValue['colours'][i],
                                 self.parameterValue['colours'][i])
            canvas.drawRectangles(allX, allY, allW, allH, style,
                                  referencePoint='southeast')

# Display a rectangle proportional to the demand for each node
class FlexibleNodeDisplayer( Style ):
    description = 'customizable nodes'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = {
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'min. radius': IntParameterInfo(2, 20),
        'max. radius': IntParameterInfo(5, 200),
        'fill colour': ColourParameterInfo(),
        'contour colour': ColourParameterInfo(),
        'shape type': EnumerationParameterInfo( [ 'polygon',
                                                  'regular star',
                                                  'sharp star',
                                                  'fat star',
                                                  'very fat star',
                                                  ] ),
        'number of edges': IntParameterInfo(3, 100),
        'angle': FloatParameterInfo(-180.0, 180.0),
        'radius by attribute': BoolParameterInfo(),
        'filter active': BoolParameterInfo(),
        }
    defaultValue = {
        'x offset': 0,
        'y offset': 0,
        'min. radius': 3,
        'max. radius': 10,
        'fill colour': colours.darkpurple,
        'contour colour': colours.black,
        'shape type': 'polygon',
        'number of edges': 3,
        'angle': 0,
        'radius by attribute': False,
        'radius attribute': 'index',
        'filter active': False,
        'filter attribute': 'is depot',
        'filter value': 'True',
        }
    def initialise(self):
        self.minValue = None
    #
    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'max. radius' and \
                parameterValue < self.parameterValue['min. radius']:
            Style.setParameter(self, 'min. radius', parameterValue)
        if parameterName == 'min. radius' and \
                parameterValue > self.parameterValue['max. radius']:
            Style.setParameter(self, 'max. radius', parameterValue)
        if parameterName == 'radius attribute' \
                or parameterName == 'min. radius' \
                or parameterName == 'max. radius':
            self.minValue = None
        # in case we change the attribute on which the filter is based,
        # we must compute the list of possible values for this attribute
        if parameterName == 'filter attribute':
            del self.parameterInfo['filter value']
            del self.parameterValue['filter value']
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'radius attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['radius attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData,
                                                 solutionData,
                                                 acceptable)
#         # only perform painting if the selected attributes are available
#         if not self.parameterValue['attribute'] in inputData.nodeAttributes:
#             return
        if not 'filter attribute' in self.parameterInfo:
            acceptable = \
                lambda x: isinstance(x, int) or \
                isinstance(x, str) or isinstance(x, float)
            self.parameterInfo['filter attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData,
                                                 solutionData,
                                                 acceptable)
        if not 'filter value' in self.parameterInfo:
            self.fValues = globalNodeAttributeValues(\
                self.parameterValue['filter attribute'],
                inputData,
                solutionData)
            rawValues = set ( self.fValues )
#             rawValues = set ( [ node[self.parameterValue['filter attribute']]
#                                 for node in inputData.nodes ] )
            finalValues = [ x if isinstance(x, str) else str(x)
                            for x in rawValues ]
            self.parameterInfo['filter value'] = \
                EnumerationParameterInfo(finalValues)
            # case where 
            if not 'filter value' in self.parameterValue or \
                    not self.parameterValue['filter value'] in finalValues:
                self.parameterValue['filter value'] = finalValues[0]
        # compute min and max demand if required
        if self.minValue is None:
            self.rValues = globalNodeAttributeValues(\
                self.parameterValue['radius attribute'],
                inputData,
                solutionData)
            self.minValue, self.maxValue = min(self.rValues), max(self.rValues)
            self.computeRadius =\
                util.intervalMapping(self.minValue, self.maxValue,
                                     self.parameterValue['min. radius'],
                                     self.parameterValue['max. radius'])
        # second only continue if an attribute is specified
        allR = [ self.computeRadius(x) for x in self.rValues ]
        allX, allY = [], []
        for node, value in zip(inputData.nodes, self.fValues):
            if nodePredicate and not nodePredicate(node):
                continue
            # only display nodes matching the filter
            elif self.parameterValue['filter active'] and \
                    'filter value' in self.parameterValue and \
                    str(value) != self.parameterValue['filter value']:
#                     str(node[self.parameterValue['filter attribute']]) != \
#                     self.parameterValue['filter value']:
                continue
            else:
                allX.append(convertX(node['x']) +
                            self.parameterValue['x offset'])
                allY.append(convertY(node['y']) +
                            self.parameterValue['y offset'])
        # determine shape to use
        if self.parameterValue['shape type'] == 'polygon':
            shape = shapes.makeRegularPolygon(\
                self.parameterValue['number of edges'] )
        elif self.parameterValue['shape type'] == 'regular star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'] )
        elif self.parameterValue['shape type'] == 'sharp star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'], 3 )
        elif self.parameterValue['shape type'] == 'fat star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'], 2 )
        elif self.parameterValue['shape type'] == 'very fat star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'], 1.5 )
        else:
            return
        # Now we can draw the polygons
        style = DrawingStyle(self.parameterValue['contour colour'],
                             self.parameterValue['fill colour'])
        # In case they all have the same radius, we can use the faster method
        if not self.parameterValue['radius by attribute']:
            canvas.drawCentredPolygons(shape, allX, allY,
                                       self.parameterValue['max. radius'],
                                       style,
                                       self.parameterValue['angle'])
        # otherwise we have to display each polygon separately
        else:
            for x, y, r in zip(allX, allY, allR):
                canvas.drawCentredPolygon(shape, x, y, r, style,
                                          self.parameterValue['angle'])
