#
# File created October 3rd 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: October 4th 2011 by Fabien Tricoire
#
from style import *

import colours

dateInputAttributes = [ 'release time', 'due date' ]
dateSolutionAttributes = [ 'start of service' ]

def computeNodeIndices(inputData,
                       solutionData,
                       nodePredicate,
                       routePredicate):
    nodeIndices = []
    indicesAsSet = set()
    for route in solutionData.routes:
        # add nodes from routes that are to be displayed
        if routePredicate is None or routePredicate(route):
            for nodeIndex in route['node sequence']:
                if nodePredicate is None or \
                        nodePredicate(inputData.nodes[nodeIndex]):
                    if not nodeIndex in indicesAsSet:
                        nodeIndices.append(nodeIndex)
                        indicesAsSet.add(nodeIndex)
    return nodeIndices

def computeHorizon(inputData,
                   solutionData,
                   nodeIndices,
                   reducedHorizon):
    dates = []
    indices = nodeIndices if reducedHorizon else range(len(inputData.nodes))
    for index in indices:
        for attr in dateInputAttributes:
            if attr in inputData.nodes[index]:
                dates.append(inputData.nodes[index][attr])
        for attr in dateSolutionAttributes:
            if attr in solutionData.nodes[index]:
                dates.append(solutionData.nodes[index][attr])
    dMin, dMax = min(dates), max(dates)
    return dMin, dMax
    
class SchedulingNodes( Style ):
    description = 'scheduling'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'alpha blending': IntParameterInfo(0, 255),
        'node guide': BoolParameterInfo(),
        'font colour': colourInfo,
        'font size': IntParameterInfo(6, 40),
        'max. height': IntParameterInfo(6, 40),
        'time window': BoolParameterInfo(),
        'time window colour': colourInfo,
        'waiting time': BoolParameterInfo(),
        'waiting time colour': colourInfo,
        'service time': BoolParameterInfo(),
        'service time colour': colourInfo,
        'lunch break': BoolParameterInfo(),
        'lunch break colour': colourInfo,
        'vehicle line': BoolParameterInfo(),
        'vehicle line colour': colourInfo,
        'vehicle line thickness': IntParameterInfo(0, 10),
        'time scale': BoolParameterInfo(),
        'time scale precision': IntParameterInfo(2, 20),
        'reduced horizon': BoolParameterInfo(),
        }
    defaultValue = {
        'alpha blending': 170,
        'node guide': True,
        'font colour': colours.black,
        'font size': 9,
        'max. height': 12,
        'time window': True,
        'time window colour': colours.dimcyan,
        'waiting time': True,
        'waiting time colour': colours.darkorange,
        'service time': True,
        'service time colour': colours.red,
        'lunch break': False,
        'lunch break colour': colours.transparent,
        'vehicle line': True,
        'vehicle line colour': colours.black,
        'vehicle line thickness': 1,
        'time scale': True,
        'time scale precision': 5,
        'font family': 'Verdana',
        'font style': 'normal',
        'reduced horizon': False,
        }
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # box where we'll draw
        xmin, ymin, xmax, ymax = boundingBox
        x0, y0, x1, y1 = \
            convertX(xmin), convertY(ymin), convertX(xmax), convertY(ymax)
        y0 += self.parameterValue['font size']
        x0 += 2 * self.parameterValue['font size']
#         # useless border
#         style = DrawingStyle(colours.red,
#                              None,
#                              1)
#         canvas.drawRectangle(x0, y0, x1 - x0, y1 - y0,
#                              style,
#                              referencePoint='southwest'
#                              )
        # compute useful nodes in the correct order
        nodeIndices = computeNodeIndices(inputData,
                                         solutionData,
                                         nodePredicate,
                                         routePredicate)
        rowHeight = (y1 - y0) / len(nodeIndices)
        halfRowHeight = rowHeight / 2.0
        halfRectHeight = self.parameterValue['max. height'] / 2.0
        indexToRow = {}
        for index in nodeIndices:
            indexToRow[index] = len(indexToRow)
        # time horizon
        dMin, dMax = computeHorizon(inputData,
                                    solutionData,
                                    nodeIndices,
                                    self.parameterValue['reduced horizon'])
        # convert time to x coordinate
        timeToX = util.intervalMapping(dMin, dMax, x0, x1)
        # global font for this style
        font = Font(self.parameterValue['font size'],
                    self.parameterValue['font family'],
                    self.parameterValue['font style'])
        fontColour = self.parameterValue['font colour']
        # display time scale if needed
        if self.parameterValue['time scale']:
            style=DrawingStyle(lineColour=colours.black,
                               lineThickness=1)
            canvas.drawLine(x0, y0, x1, y0, style)
            for i in range(self.parameterValue['time scale precision']):
                value = i * (dMax - dMin) \
                    / self.parameterValue['time scale precision']
                canvas.drawText(str(value), timeToX(value), y0,
                                font, fontColour, fontColour)
        # list of dicts of rectangle parameters
        rectangleInfo = {}
        for attr in [ 'time window', 'waiting time', 'service time' ]:
            if self.parameterValue[attr]:
                colour = self.parameterValue[attr + ' colour']
                colour.alpha = self.parameterValue['alpha blending']
                rectangleInfo[attr] =  { 'xs': [],
                                         'ys': [],
                                         'ws': [],
                                         'hs': [],
                                         'colour': colour }
        # for each node, display various stuff
        for nodeIndex in indexToRow:
            index = nodeIndex
            row = indexToRow[index]
            yBase = y0 + row * rowHeight + halfRowHeight
            # node guide
            if self.parameterValue['node guide']:
                y = yBase + self.parameterValue['font size'] / 2.0
                canvas.drawText(str(index),
                                x0 - 2 * self.parameterValue['font size'], y,
                                font, fontColour, fontColour)
            # line for each node
                canvas.drawLine(x0, yBase, x1, yBase,
                                DrawingStyle(colours.funkygreen,
                                             colours.funkygreen,
                                             .1))
            # time window
            if self.parameterValue['time window']:
                e = timeToX(inputData.nodes[index]['release time'])
                l = timeToX(inputData.nodes[index]['due date'])
                rectangleInfo['time window']['xs'].append(e)
                rectangleInfo['time window']['ys'].append(yBase +halfRectHeight)
                rectangleInfo['time window']['ws'].append(l - e)
                rectangleInfo['time window']['hs'].append(\
                    self.parameterValue['max. height'])
            # waiting time
            if self.parameterValue['waiting time']:
                arrival = timeToX(solutionData.nodes[index]['arrival time'])
                start = timeToX(solutionData.nodes[index]['start of service'])
                rectangleInfo['waiting time']['xs'].append(arrival)
                rectangleInfo['waiting time']['ys'].append(\
                    yBase + halfRectHeight)
                rectangleInfo['waiting time']['ws'].append(start - arrival)
                rectangleInfo['waiting time']['hs'].append(\
                    self.parameterValue['max. height'])
            # service time
            if self.parameterValue['service time']:
                start = timeToX(solutionData.nodes[index]['start of service'])
                end = timeToX(solutionData.nodes[index]['end of service'])
                rectangleInfo['service time']['xs'].append(start)
                rectangleInfo['service time']['ys'].append(\
                    yBase + halfRectHeight)
                rectangleInfo['service time']['ws'].append(end - start)
                rectangleInfo['service time']['hs'].append(\
                    self.parameterValue['max. height'])
        # now we can display all the rectangle
        for attr in [ 'time window', 'waiting time', 'service time' ]:
            if self.parameterValue[attr]:
                info = rectangleInfo[attr]
                canvas.drawRectangles(info['xs'], info['ys'],
                                      info['ws'], info['hs'],
                                      DrawingStyle(info['colour'],
                                                   info['colour'],
                                                   0),
                                      'northwest')
        # display routes
        if self.parameterValue['vehicle line']:
            colour = self.parameterValue['vehicle line colour']
            colour.alpha = self.parameterValue['alpha blending']
            style = DrawingStyle(colour, colour,
                                 self.parameterValue['vehicle line thickness'])
            for route in solutionData.routes:
                if routePredicate is None or routePredicate(route):
                    for nextNodeIndexIndex, nodeIndex in \
                            enumerate(route['node sequence'][:-1]):
                        nextNodeIndex = \
                            route['node sequence'][nextNodeIndexIndex+1]
                        row1 = indexToRow[nodeIndex]
                        row2 = indexToRow[nextNodeIndex]
                        y1 = y0 + row1 * rowHeight + halfRowHeight
                        y2 = y0 + row2 * rowHeight + halfRowHeight
                        xArrival = timeToX(solutionData.nodes[nodeIndex]\
                                               ['arrival time'])
                        xDeparture = timeToX(solutionData.nodes[nodeIndex]\
                                                 ['end of service'])
                        xNextArrival = timeToX(\
                            solutionData.nodes[nextNodeIndex]['arrival time'])
                        # horizontal line from arrival at this node
                        # until departure
                        canvas.drawLine(xArrival, y1, xDeparture, y1, style)
                        # travel line to the next node
                        canvas.drawLine(xDeparture, y1, xNextArrival, y2, style)
                    # service at the last node
                    lastNodeIndex = route['node sequence'][-1]
                    row = indexToRow[lastNodeIndex]
                    y = y0 + row * rowHeight + halfRowHeight
                    xArrival = timeToX(solutionData.nodes[lastNodeIndex]\
                                           ['arrival time'])
                    xDeparture = timeToX(solutionData.nodes[lastNodeIndex]\
                                             ['end of service'])
                    canvas.drawLine(xArrival, y, xDeparture, y, style)
