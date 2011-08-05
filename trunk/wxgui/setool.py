#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 6th 2011 by Fabien Tricoire
#
import os

import wx
import wx.lib.colourselect as csel

from wxcanvas import convertColour
import events
import style

try:
    from agw import floatspin
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.floatspin as floatspin
    
# origin class for all style edit tools
class StyleEditTool:
    def __init__(self, styleToEdit, paramName):
        self.styleToEdit = styleToEdit
        self.parameterName = paramName

    def modifyValue(self, event=None):
        self.styleToEdit.setParameter(self.parameterName, self.getValue())
#         print('setting parameter', self.parameterName,
#               'to value', self.getValue())
        events.postStyleSheetUpdateEvent(self)

class BoolStyleEditTool(StyleEditTool, wx.CheckBox):
    def __init__(self, parent, styleToEdit, paramName):
        wx.CheckBox.__init__(self, parent, id=-1)
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.SetValue(self.styleToEdit.parameterValue[paramName])
        self.Bind(wx.EVT_CHECKBOX, self.modifyValue)
        
    def getValue(self):
        return self.IsChecked()
    
class IntStyleEditTool(StyleEditTool, wx.SpinCtrl):
    def __init__(self, parent, styleToEdit, paramName):
        wx.SpinCtrl.__init__(self, parent, id=-1)
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.SetRange(styleToEdit.parameterInfo[paramName].LB,
                      styleToEdit.parameterInfo[paramName].UB)
        currentValue = styleToEdit.parameterValue[paramName]
        if currentValue.__class__ == int:
            self.SetValue(styleToEdit.parameterValue[paramName])
            self.Bind(wx.EVT_SPINCTRL, self.modifyValue)

    def getValue(self):
        return self.GetValue()
    
class FloatStyleEditTool(StyleEditTool, floatspin.FloatSpin):
    def __init__(self, parent, styleToEdit, paramName):
        increment = (styleToEdit.parameterInfo[paramName].UB - \
            styleToEdit.parameterInfo[paramName].LB) / 100.0
        floatspin.FloatSpin.__init__(self, parent, id=-1,
                                     increment=increment,
                                     digits=2,
                                     # agwStyle=floatspin.FS_RIGHT
                                     )
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.SetRange(styleToEdit.parameterInfo[paramName].LB,
                      styleToEdit.parameterInfo[paramName].UB)
        self.SetValue(styleToEdit.parameterValue[paramName])
        self.Bind(floatspin.EVT_FLOATSPIN, self.modifyValue)
        
    def getValue(self):
        return self.GetValue()
    
def wxColourToColour(colour):
    return style.Colour(colour.Red(), colour.Green(), colour.Blue(),
                        colour.Alpha())

class ColourStyleEditTool(StyleEditTool, csel.ColourSelect):
    def __init__(self, parent, styleToEdit, paramName):
        value = styleToEdit.parameterValue[paramName]
        csel.ColourSelect.__init__(self, parent, -1,
                                   colour=convertColour(value))
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.Bind(csel.EVT_COLOURSELECT , self.modifyValue)

    def getValue(self):
        return wxColourToColour(self.GetColour())
        
class ChoiceListStyleEditTool(StyleEditTool, wx.Choice):
    def __init__(self, parent, styleToEdit, paramName):
        values = styleToEdit.parameterInfo[paramName].possibleValues
        wx.Choice.__init__(self, parent, -1, choices=values)
        if paramName in styleToEdit.parameterValue:
            self.SetSelection(self.FindString(\
                    styleToEdit.parameterValue[paramName]))
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.Bind(wx.EVT_CHOICE , self.modifyValue)
    #
    def getValue(self):
        return self.GetStringSelection()
        
class FileNameStyleEditTool(StyleEditTool, wx.Button):
    def __init__(self, parent, styleToEdit, paramName):
        wx.Button.__init__(self, parent, -1, 'Choose file')
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.Bind(wx.EVT_BUTTON , self.selectFile)
        self.fName = None
    #
    def selectFile(self, event):
        fileSelector = wx.FileDialog(self,
                                     message="Select a file",
                                     defaultDir=os.getcwd(),
                                     style=wx.OPEN | wx.CHANGE_DIR )
        if fileSelector.ShowModal() == wx.ID_OK:
            files = fileSelector.GetPaths()
            self.fName = str(files[0])
        fileSelector.Destroy()
        self.modifyValue()
    #
    def getValue(self):
        return self.fName

class ColourMapStyleEditTool(StyleEditTool, wx.Button):
    def __init__(self, parent, styleToEdit, paramName):
        wx.Button.__init__(self, parent, wx.ID_PROPERTIES)
        StyleEditTool.__init__(self, styleToEdit, paramName)
        self.Bind(wx.EVT_BUTTON , self.editMap)
        self.map = styleToEdit.parameterValue[paramName]
    #
    def editMap(self, event):
        mapEditor = ColourMapEditor(self,
                                    self.map)
        if mapEditor.ShowModal() == wx.ID_OK:
            self.map = mapEditor.getMap()
        mapEditor.Destroy()
        self.modifyValue()
    #
    def getValue(self):
        return self.map

# dialog used to edit a ColourMap object
import  wx.lib.scrolledpanel as scrolled
class ColourMapEditor(wx.Dialog):
    def __init__(self, parent, map):
        wx.Dialog.__init__(self, parent, -1,
                           title='Colour map editor')
        # main sizer for this dialog
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # window with the grid...
        panel = scrolled.ScrolledPanel(self, -1, size=(400, 200))
        # colour cells: initialization
        nColours = max(len(map), 100) # arbitrary
        nColumns = 10 # arbitrary too
        self.cells = [ csel.ColourSelect(panel, -1, colour=convertColour(x))
                       for x in map.colours ]
        # complete cells with transparent elements
        dummyColour = style.Colour(0,0,0,0)
        self.cells += [ csel.ColourSelect(panel, -1,
                                          colour=convertColour(dummyColour))
                        for x in range(nColours-len(self.cells)) ]
        nRows = len(self.cells) / nColumns
        # now we put the cells in a grid...
        gridSizer = wx.FlexGridSizer(cols=nColumns+1, vgap=3, hgap=3)
        gridSizer.Add(wx.StaticText(panel, -1, ''))
        for i in range(nColumns):
            gridSizer.Add(wx.StaticText(panel, -1, str(i)), -1, wx.ALIGN_CENTER)
        for i in range(nRows):
            gridSizer.Add(wx.StaticText(panel, -1, '+' + str(nColumns*i)))
            gridSizer.AddMany([ x#(x, 0, wx.EXPAND)
                                for x in self.cells[i*nRows:i*nRows+nColumns] ])
        panel.SetSizer(gridSizer)
        panel.SetAutoLayout(1)
        gridSizer.Fit(panel)
        panel.SetupScrolling()
        mainSizer.Add(panel, wx.EXPAND | wx.ALIGN_CENTER)
        # buttons
        padding = 10
        mainSizer.Add((0, padding))
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # add standard buttons
        okButton = wx.Button(self, wx.ID_OK)
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        buttonSizer.Add(okButton, 0)
        buttonSizer.Add((20,0), 1)
        buttonSizer.Add(cancelButton, 0)
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER)
        mainSizer.Add((0,padding), 0)
        # now we're ready
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnScreen()
        
    # return the edited map
    def getMap(self):
        newColours = [ wxColourToColour(cell.GetColour())
                       for cell in self.cells ]
        # remove all trailing transparent colours
        while newColours[-1].alpha == 0:
            del newColours[-1]
        return style.ColourMap(newColours)
