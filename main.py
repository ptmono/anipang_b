import sys
sys.path.append(r"C:\python27\lib") 
# sys.path.append(r"C:\Python27\Scripts") 
#sys.path.append('C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319')
import numpy
import math
import time

import clr
clr.AddReferenceByPartialName("System")
clr.AddReferenceByPartialName("System.Windows.Forms")
clr.AddReferenceByPartialName("System.Drawing")

from System import * #Console, IntPtr
from System.Windows.Forms import *
from System.Drawing import *    # Point
from System.Diagnostics import Process


clr.AddReference("crop.dll")
from Crop import Crop2
from ZScreenLib import Capture

clr.AddReference("cslibs")
from UnmanagedCode import User32, GDI32
from DLibs import MonoPix

from libs import rgb_to_cielab

import clrtype

from System.Reflection import BindingFlags
import System
 
class Win32(object):
    __metaclass__ = clrtype.ClrClass
 
    from System.Runtime.InteropServices import DllImportAttribute
    DllImport = clrtype.attribute(DllImportAttribute)
 
    @staticmethod
    @DllImport("user32.dll")
    @clrtype.accepts(System.IntPtr, System.String, System.String, System.UInt32)
    @clrtype.returns(System.Int32)
    def MessageBox(hwnd, text, caption, type): raise RuntimeError("Runtime Error")
# Win32.MessageBox(System.IntPtr.Zero, "Hello, Win32 API(IronPython) World!", "Hello, World!", 0)


class AniWindow(object):
    name = "HD-FRONTEND"

    @classmethod
    def getRectangle(self):
        '''
        This will return WRECT struct.
	public struct WRECT
	{
	    public int Left;
	    public int Top;
	    public int Right;
	    public int Bottom;
	}
        '''


        hwnd = AniImageBoard.getProcessHanddle(self.name)

        # rec has 0. But rec_result has the result. Why???
        rec = User32.WRECT()
        rec_result = User32.GetWindowRect(hwnd, rec)
        if rec_result[0] is False:
            return
        return rec_result[1]

    @classmethod
    def click(self, x, y):
        info = 0
        Cursor.Position = Point(x, y)
        User32.mouse_event(0x202, 0, 0, 0, info)
        User32.mouse_event(0x204, 0, 0, 0, info)

    @classmethod
    def doubleClick(self, x, y):
        self.click(x, y)
        self.click(x, y)

    @classmethod
    def killClick(self, x1, y1, x2, y2):
        Cursor.Position = Point(x1, y1)
        User32.mouse_event(0x202, 0, 0, 0, 0)
        Cursor.Position = Point(x2, y2)
        User32.mouse_event(0x204, 0, 0, 0, 0)


class AniImageBoard(object):
    '''
    AniImageBoard.Rectangle gives the coordinate for anipang board.
    '''
    name = "HD-FRONTEND"
    Rectangle = None
    # Rectangle Structure. X, Y, Width, Height
    _instance = None

    # It is singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AniImageBoard, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def setRectangle(self, force=True):
        'If FORCE is True, then bluestack will be foregrounded.'
        if not self.Rectangle:
            if force: self.foregroundWindow()
            self.Rectangle = self.getRectangle()
            # Disapeared time of crop layer
            time.sleep(2)
        return self

    @staticmethod
    def getProcessHanddle(name):
        '''
        Get window handler from the name of process. Process also has
        Handle property which gives the handle of window.
        '''
        p = Process.GetProcessesByName(name)

        if len(p) == 0:
            raise RuntimeError("Error: We cann't detect BlueStack.")
        return p[0].MainWindowHandle

    @classmethod
    def getRectangle(self):
        Application.EnableVisualStyles()
        Application.SetCompatibleTextRenderingDefault(False)
        crop = Crop2(Capture.CaptureScreen(False))
        Application.Run(crop)

        return crop.Manager.CurrentArea.Rectangle

    @classmethod
    def foregroundWindow(self):
        hwnd = AniImageBoard.getProcessHanddle(self.name)
        if hwnd == 0:
            raise RuntimeError('There is no Window.')
        User32.SwitchToThisWindow(hwnd, True)



class AniImage(object):

    Rectangle = None
    bmp = None
    start_button_xy = (173, 136)
    # cell is square. So bmp also square
    cell_length = None
    cell_count = 7
    cell_dy_rates = [0.666]
    #cell_dx_rates = [0.342, 0.666]
    cell_dx_rates = [0.482, 0.666]
    cell_check_offsets = []
    

    def __init__(self, rectangle=None, bmp=None, force=True):
        # We will specify Rectangle only one time.
        if rectangle:
            self.Rectangle = rectangle
        else:
            print "why RECTANGLE?????"
            self.Rectangle = AniImageBoard().setRectangle(force).Rectangle

        if not bmp:
            self.setBmp()
        else:
            self.bmp = bmp

        self.setCellLength()
        self.setCheckOffsetsOfCell()

        #self.init()
        

    def matrix(self):
        result = []
        for count in range(self.cell_count * self.cell_count):
            ccl = self.cellCielab(count, roundup=True)
            #print count, str(ccl)
            #mat.item(count) = ccl
            result.append(ccl)

        #result = numpy.matrix(result)
        return result

    def cielab(self):
        result = []
        for count in range(self.cell_count * self.cell_count):
            ccl = self.cellCielab(count, roundup=True)
            result.append(ccl)
        return result

    def cellCielab(self, *args, **kargs):
        labs = self.cellCielabs(*args)

        result = [0, 0, 0]
        for lab in labs:
            result[0] += lab[0]
            result[1] += lab[1]
            result[2] += lab[2]

        try:
            if kargs['roundup']:
                return [round(result[0]/len(labs)), round(result[1]/len(labs)), round(result[2]/len(labs))]
        except:
            return [result[0]/len(labs), result[1]/len(labs), result[2]/len(labs)]

    def cellCielabs(self, *args):
        rgbs = self.cellColors(*args)

        result = []
        for rgb in rgbs:
            rr = rgb.R
            gg = rgb.G
            bb = rgb.B
            lab = rgb_to_cielab(rr, gg, bb)
            result.append(list(lab))
        return result

    def cellColors(self, *args):
        '''The count is started from 0. cellColor(6, 6) will be 7x7 element.
        Return a list of System.Drawing.Color.
        '''
        result = []
        if len(args) == 1:
            # The count is started from 0.
            # divmod(48, 7) --> (6, 6)
            # divmod(6, 7)  --> (0, 6)
            p = divmod(args[0], self.cell_count)
            p_row = p[0]
            p_col = p[1]
        else:
            p_col = args[0]
            p_row = args[1]

        for offset in self.cell_check_offsets:
            x = (self.cell_length * p_col) + offset[0]
            y = (self.cell_length * p_row) + offset[1]
            result.append(self.getPixel(x, y))
        return result
            
    def setCellLength(self):
        self.cell_length = self.Rectangle.Width/self.cell_count
        return self

    def setCheckOffsetsOfCell(self):
        if self.cell_check_offsets:
            return self
        for dy in self.cell_dy_rates:
            for dx in self.cell_dx_rates:
                x = int(self.cell_length * dx)
                y = int(self.cell_length * dy)
                self.cell_check_offsets.append((x, y))
        return self

    def setBmp(self):
        # Cursor.Position = Point(10, 10)
        # import time
        # # Screen crop layer need time to be disappeared
        # time.sleep(2)
        self.bmp = MonoPix.getRegion(self.Rectangle)
        return self

    def getPixel(self, *args):
        if len(args) == 2:
            x = args[0]
            y = args[1]
        elif isinstance(args[0], Point):
            x = args[0].X
            y = args[0].Y
        return self.bmp.GetPixel(x, y)

    # Fixme: Refactore the name. coordinate to (column, row)
    def locationToCoordinate(self, location):
        p = divmod(location, self.cell_count)
        return p[1], p[0] # (col, row)

    def coordinateToLocation(self, col, row):
        return self.cell_count * row + col
        
    def locationToXY(self, location):
        'Based on the board of image.'
        cell_center = self.cell_length/2
        col, row = self.locationToCoordinate(location)
        x = col * self.cell_length + cell_center
        y = row * self.cell_length + cell_center
        return x, y




class AniMatrix(object):

    def __init__(self, aniimage):
        if not isinstance(aniimage, AniImage):
            raise AttributeError("We need AniImage object.")

        self.image = aniimage
        self.lists = self.image.cielab()

    def item(self, *args):
        "The input is the number from 0 or column, row pair."
        if len(args) == 1:
            p = args[0]
        else:
            p = args[1] * self.image.cell_count + args[0]
        return self.lists[p]
        

    def __repr__(self):
        return str(self.image.matrix())

    def areEqual(self, step):
        pass


class AniKiller(AniImage):
    # 1 | 2
    #   5
    # 3 | 4
    group1 = [0, 1, 2, 7, 8, 9, 14, 15, 16]
    group2 = [4, 5, 6, 11, 12, 13, 18, 19, 20]
    group3 = [28, 29, 30, 35, 36, 37, 42, 43, 44]
    group4 = [32, 33, 34, 39, 40, 41, 46, 47, 48]
    group5 = [3, 10, 17, 21, 22, 23, 24, 25, 26, 27, 31, 38, 45]
    boom_cielab = [8.0, 20.0, 12.0]
    cursor_rest = Point(10, 10)

    def __init__(self, rectangle=None, bmp=None, force=True):
        super(AniKiller, self).__init__(rectangle, bmp, force)
        self.animatrix = AniMatrix(self)

    def resetBmp(self):
        self.setBmp()
        self.animatrix = AniMatrix(self)

    def dododo(self):

        for a in self.group1:
            if self.kill(a): return True
        for a in self.group4:
            if self.kill(a): return True
        for a in self.group3:
            if self.kill(a): return True
        for a in self.group2:
            if self.kill(a): return True
        for a in self.group5:
            if self.kill(a): return True
        #self.useBoom()

    def kill(self, location):
        target = self.getTarget(location)
        print target
        if target:
            dx1, dy1 = self.locationToXY(location)
            x1 = self.Rectangle.X + dx1
            y1 = self.Rectangle.Y + dy1

            dx2, dy2 = self.locationToXY(target)
            x2 = self.Rectangle.X + dx2
            y2 = self.Rectangle.Y + dy2
            
            AniWindow.killClick(x1, y1, x2, y2)
            Cursor.Position = self.cursor_rest
            return True

    def useBoom(self):
        pass

    def startGame(self):
        'Click start button.'
        ai = AniImage()
        related_coordinate_of_start_button = self.start_button_xy
        x = self.Rectangle.X + related_coordinate_of_start_button[0]
        y = self.Rectangle.Y + related_coordinate_of_start_button[1]
        AniWindow.click(x, y)

    def getTarget(self, location):
        target = self.getTargetCross(location)
        if target:
            return target
        return self.getTargetX(location)

    def getTargetCross(self, location):
        # To detect
        # O O X 0 X O O
        step2_near_locations = self.getLocationsForStep(location, 2)
        step2_result = []
        for loc in step2_near_locations:
            step2_result.append(self.isEqual(location, loc))

        step3_result = []
        # TODO: We can reduce the routines. We only need the location for
        # True.
        step3_near_locations = self.getLocationsForStep(location, 3)
        for loc in step3_near_locations:
            step3_result.append(self.isEqual(location, loc))

        step3 = numpy.matrix(numpy.array(step3_result).reshape(2,2))
        step2 = numpy.matrix(numpy.array(step2_result).reshape(2,2))

        step = step3 & step2
        step = list(numpy.array(step).reshape(-1))

        step1_near_locations = self.getLocationsForStep(location, 1)
        #print step1_near_locations, "aaa"
        counter = 0
        for loc in step:
            if loc:
                target_location = step1_near_locations[counter]
                if not self.isEqual(location, target_location):
                    # It's not boom time
                    return target_location
            counter += 1
        


    def getTargetX(self, location):

        # To detect
        # X O  
        # 0 X
        # X 0 ... 
        step1_near_locations = self.getLocationsForStep(location, 1)
        stepX_near_locations = self.getLocationsForStepX(location, 1)
        stepX_result = []
        for loc in stepX_near_locations:
            stepX_result.append(self.isEqual(location, loc))

        if stepX_result[0] and stepX_result[1]:
            return step1_near_locations[1]
        if stepX_result[1] and stepX_result[2]:
            return step1_near_locations[2]
        if stepX_result[2] and stepX_result[3]:
            return step1_near_locations[3]
        if stepX_result[3] and stepX_result[0]:
            return step1_near_locations[0]

        # To detect
        # X O X     X 0 X
        # X O O ... X 2 0
        # 0 X X     1 X X
        # ...
        for i in range(4):
            #print stepX_result, 'bcc'
            if stepX_result[i]:
                if i == 3:
                    side = 4
                else:
                    side = i + 1
                # the location of 2.
                #print stepX_near_locations[i], 'X locations'
                step1_locations_for_side = self.getLocationsForStepS(stepX_near_locations[i], 1, side)
                #print step1_locations_for_side, 'acc'
                for loc in step1_locations_for_side:
                    if self.isEqual(location, loc):
                        return self.getLocationForLineL(location, loc)

                
    def getLocationForLineL(self, p1, p2):
        '''
        Get the point Y.

            Y O O(p2)
        (p1)0 X X

            X O(p2)
            X O
        (p1)0 Y
        '''
        p1_cr = self.locationToCoordinate(p1)
        p2_cr = self.locationToCoordinate(p2)

        p1_col = p1_cr[0]
        p1_row = p1_cr[1]
        p2_col = p2_cr[0]
        p2_row = p2_cr[1]

        if abs(p1_col - p2_col) == 1:
            return self.coordinateToLocation(p2_col, p1_row)

        if abs(p1_row - p2_row) == 1:
            return self.coordinateToLocation(p1_col, p2_row)
        

    def isEqual(self, p1, p2, max_deltaE=10):

        if p1 < 0 or p2 < 0:
            return False
        dist = self.distance(p1, p2)
        if dist < max_deltaE:
            return True
        return False

    # We can create the dictionary of the table to speed up, location vs
    # the surround locations.
    def getLocationsForStep(self, location, step):
        '''
        surround locations on step.
            p1
            |
        p4-----p2
            |
            p3
        '''
        p = self.locationToCoordinate(location)
        col = p[0]
        row = p[1]

        p1 = self.cell_count * (row - step) + col # 0 degree
        p2 = self.cell_count * row + col + step   # 90
        p3 = self.cell_count * (row + step) + col # 180
        p4 = self.cell_count * row + col - step   # 260

        # We are calurating the location with the list. It has a problem.
        # The location 12 and step2 returns (-2, 14, 26, 10). 14 is not on
        # same line. We does not interest these locations.
        # -----12-
        # 14-------
        # So it have to be deleted. Vertical line also has the problem.
        max_location = self.cell_count * self.cell_count - 1
        location_row = divmod(location, self.cell_count)[0]
        # p1 returns minus value
        # p2 is in same row
        if location_row != divmod(p2, self.cell_count)[0]:
            p2 = -1
        # p4 is in same row
        if location_row != divmod(p4, self.cell_count)[0]:
            p4 = -1
        if p3 > max_location:
            p3 = -1
        return p1, p2, p3, p4

    def getLocationsForStepS(self, location, step, side):
        '''
            p1
         s4 | s1
        p4--0--p2
         s3 | s2
            p3

        s1 = (p1, p2). The side is 1.
        s2 = (p2, p3). The side is 2.

        '''
        p = self.getLocationsForStep(location, step)

        if side == 4:
            return p[-1], p[0]
        return p[side-1:side+1]

    def getLocationsForStepX(self, location, step):
        '''
        surround locations on step
          p4 p1
           \/
           /\
          p3 p2
        '''
        p = self.locationToCoordinate(location)
        col = p[0]
        row = p[1]

        p1 = self.cell_count * (row - step) + col + step
        p2 = self.cell_count * (row + step) + col + step
        p3 = self.cell_count * (row + step) + col - step
        p4 = self.cell_count * (row - step) + col - step

        max_location = self.cell_count * self.cell_count - 1
        location_row = divmod(location, self.cell_count)[0]
        p1_row = divmod(p1, self.cell_count)[0]
        p2_row = divmod(p2, self.cell_count)[0]
        p3_row = divmod(p3, self.cell_count)[0]
        p4_row = divmod(p4, self.cell_count)[0]

        # The row of p1 is location_row - step
        if (location_row - step) != p1_row:
            #print location_row, divmod(p2, self.cell_count)[0], "aaa"
            p1 = -1
        if (p2 > max_location) or (location_row + step) != p2_row:
            p2 = -1
        if (p3 > max_location) or (location_row + step) != p3_row:
            p3 = -1
        if (location_row - step) != p4_row:
            p4 = -1

        return p1, p2, p3, p4

    def distance(self, a, b):
        if isinstance(a, int):
            a = self.animatrix.item(a)
            b = self.animatrix.item(b)
        return math.sqrt(math.pow((a[0] - b[0]), 2) + \
                             math.pow((a[1] - b[1]), 2) + \
                             math.pow((a[2] - b[2]), 2))


# This function have no guaranty
def getPixelColor(*args):
    # the result will be such as Color [A=255, R=107, G=107, B=107].
    if len(args) == 2:
        x = args[0]
        y = args[1]

    if isinstance(args[0], Point):
        x = args[0].X
        y = args[0].Y

    hdc = User32.GetDC(IntPtr.Zero)
    pixel = GDI32.GetPixel(hdc, x, y)
    User32.ReleaseDC(IntPtr.Zero, hdc)
    result = Color.FromArgb(pixel & 0x000000FF, # R
                            # First And operation
                            (pixel & 0x0000FF00) >> 8, # G
                            (pixel & 0x00FF0000) >> 16) # B
    return result


def main():
    ak = AniKiller()
    print ak.Rectangle
    Cursor.Position = Point(10, 10)
    time.sleep(2)
    ak.startGame()
    for i in range(390):            # (0.12, 440), (0.24, 250)
        ak.resetBmp()
        ak.dododo()
        time.sleep(0.14)

if __name__ == "__main__":
    main()
