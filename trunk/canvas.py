#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 1st 2011 by Fabien Tricoire
#
import util

class Canvas:
    """
    Abstract class: should be derived by backend classes.
    Most methods here should be overloaded by the backend version.

    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

    # return the width and height of this canvas
    def getSize(self):
        return self.width, self.height

    # clear the canvas and set a white background
    def blank(self):
        print 'Error: method clear not implemented in backend'

    # draw a simple border...
    def drawBorder(self):
        print 'Error: method drawBorder not implemented in backend'
        
    # draw a rectangle centered at coordinates x, y
    # if a reference point is specified, it is used, otherwise the coordinates
    # are assumed to be those of the center of the rectangle
    # possible values for the reference point are 'center', 'northwest',
    # 'northeast', 'southeast', 'southwest'
    def drawRectangle(self, x, y, w, h, style, referencePoint='center'):
        print 'Error: method drawRectangle not implemented in backend'

    # draw a list of rectangles with the same style
    # if a reference point is specified, it is used, otherwise the coordinates
    # are assumed to be those of the center of the rectangles
    # possible values for the reference point are 'center', 'northwest',
    # 'northeast', 'southeast', 'southwest'
    # xs, ys, ws, hs are lists
    def drawRectangles(self, xs, ys, ws, hs, style, referencePoint='center'):
        print 'Error: method drawRectangles not implemented in backend'

    # draw a circle centered at coordinates x, y
    def drawCircle(self, x, y, r, style):
        print 'Error: method drawCircle not implemented in backend'

    # draw a list of circles with the same colour style
    # parameters xs, ys, rs should be lists
    def drawCircles(self, xs, ys, rs, style):
        print 'Error: method drawCircles not implemented in backend'

    # draw a line
    def drawLine(self, x1, y1, x2, y2, style):
        print 'Error: method drawLine not implemented in backend'

    # draw a polyline
    # x and y are lists
    def drawPolyline(self, x, y, style):
        print 'Error: method drawPolyline not implemented in backend'

    # draw a spline; each element in points is a 2-uple with x,y coordinates
    def drawSpline(self, points, style):
        print 'Error: method drawSpline not implemented in backend'
        
    # draw a polygon
    # x and y are lists of point coordinates
    def drawPolygon(self, xs, ys, style):
        print 'Error: method drawPolygon not implemented in backend'

    # draw a regular polygon
    # x and y are center coordinates
    def drawRegularPolygon(self, x, y, nEdges, radius, style):
        print 'Error: method drawRegularPolygon not implemented in backend'

    # draw a text label with top left corner at x, y
    def drawText(self, label, x, y,
                 font, foregroundColour, backgroundColour):
        print 'Error: method drawText not implemented in backend'
    
    # draw several text labels with top left corners given in x, y
    def drawTexts(self, labels, xs, ys,
                 font, foregroundColour, backgroundColour):
        print 'Error: method drawText not implemented in backend'
    
    # draw a text label at x, y
    # this version allows to specify the coordinates reference point,
    # as well as a rotation
    def drawFancyText(self, label, x, y,
                      font, foregroundColour, backgroundColour,
                      angle=None,
                      referencePoint='northwest'):
        print 'Error: method drawFancyText not implemented in backend'
    
    # draw a bitmap, using the given point as NW corner
    def drawBitmap(self, bitmap, NWcorner):
        print 'Error: method drawBitmap not implemented in backend'
