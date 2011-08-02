#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
from style import *
import util
import colours

class TimeWindowDisplayer(Style):
    description = 'time windows'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'contour colour': colourInfo,
        'height': IntParameterInfo(3, 60),
        'background colour': colourInfo,
        'width': IntParameterInfo(6, 200),
        'time window colour': colourInfo,
        'y offset': IntParameterInfo(-20, 40),
        'thickness': IntParameterInfo(0, 20),
        'x offset': IntParameterInfo(-40, 20),
        }
    defaultValue = {
        'x offset': 4,
        'y offset': 4,
        'thickness': 1,
        'width': 20,
        'height': 7,
        'time window colour': colours.dimcyan,
        'background colour': colours.white,
        'contour colour': colours.black,
        }
    def __init__(self, parameterValue={}):
        Style.__init__(self, parameterValue)
        self.requiredNodeAttributes += [ 'release time', 'due date' ]
        # this can only be computed once data is known
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
        if self.timeToX is None:
            self.earliest = \
                min( [ x['release time']
                       for x in inputData.nodes ], 0 )
            self.latest = max( [ x['due date']
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
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['time window colour'],
                             self.parameterValue['time window colour'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'] +
                        self.timeToX(node['release time']))
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            
            allW.append(max(1,
                            self.timeToX(node['due date']) -
                            self.timeToX(node['release time'])))
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
