from main import *

import unittest


def getCoordinateFromRegion(color, step):
    ai = AniImage()
    rect = ai.coordinate()

    print rect
    x = rect.X
    y = rect.Y
    width = rect.Width
    height = rect.Height
    result = []
    count = 0

    for dy in range(1, width, step):
        for dx in range(1, height, step):
            count = count + 1
            xx = x + dx
            yy = y + dy
            hdc_color = getPixelColor(xx, yy)
            print '----'
            print color
            print hdc_color
            print '-----'
            if color.Equals(hdc_color):
                p = Point(xx, yy)
                result.append(p)
    print count
    return result
    

class HelloTest(unittest.TestCase):

    def test_getPixelColor(self):
        self.assertIsInstance(getPixelColor(12, 14), Color)
        p = Point()
        p.X = 3
        p.Y = 5
        self.assertIsInstance(getPixelColor(p), Color)

    def test_getCoordinate(self):
        #color = Color.FromArgb(0x8068a6)
        #print len(getCoordinateFromRegion(color, 5))
        pass


class Test_AniWindow(unittest.TestCase):

    def test_getProcessHanddle(self):
        #aa = AniWindow()
        #print aa.getRectangle().Top
        pass


class Test_AniImage(unittest.TestCase):

    ai = None

    @classmethod
    def setUpClass(self):
        bmp = Bitmap("test_board.jpg")
        rect = Rectangle(Point(0,0), bmp.Size)
        self.ai = AniImage(rectangle=rect, bmp=bmp)
        pass



    def test_setImage(self):
        #bmp = AniImage().setBmp().bmp
        #bmp.Save("ccc.jpg", System.Drawing.Imaging.ImageFormat.Jpeg)
        pass

    def test_getPixel(self):
        # ai = AniImage()
        # print ai.getPixel(40, 40)
        pass
    
    def test_matrix(self):
        import numpy
        aaa = numpy.arange(49)
        aaa.shape = (7, 7)
        #x = np.matrix(np.arange(12).reshape((3,4)))
        bbb = numpy.mat(aaa)
        self.assertEqual(bbb.item((6,6)), 48)
        self.assertEqual(bbb.item(48), 48)
        # There is itemset to set item.

        bmp = Bitmap("test_board.jpg")
        rect = Rectangle(Point(0,0), bmp.Size)
        ai = AniImage(rectangle=rect, bmp=bmp)
        #ai.bmp.Save("bbb.jpg", System.Drawing.Imaging.ImageFormat.Jpeg)
        #ai.matrix()
        self.assertEqual(ai.cell_check_offsets, [(17, 33), (33, 33)])

        #aa = ai.matrix()
        #import numpy
        #bb = numpy.asarray(aa)
        #print numpy.matrix(bb.reshape((7,7)))
        
        pass

    def test_cellColors(self):
        self.assertEqual(self.ai.cellColors(6, 6)[0].ToString(), "Color [A=255, R=249, G=150, B=144]")
        # for count in range(self.ai.cell_count * self.ai.cell_count):
        #     print count, str(self.ai.cellColors(count)[0].ToString())

    def test_cellCielab(self):
        self.assertEqual(self.ai.cellCielab(1), [74.533848010764146, 36.4065900126665, 16.988401914079731])
        self.assertEqual(self.ai.cellCielab(1, roundup=True), [75.0, 36.0, 17.0])
        # for count in range(self.ai.cell_count * self.ai.cell_count):
        #     print count, str(self.ai.cellCielab(count, roundup=True))

    def test_locationToXY(self):
        self.assertEqual(self.ai.locationToXY(1), (75, 25))
        self.assertEqual(self.ai.locationToXY(13), (325, 75))

class Test_AniMatrix(unittest.TestCase):

    ai = None
    am = None

    @classmethod
    def setUpClass(cls):
        bmp = Bitmap("test_board.jpg")
        rect = Rectangle(Point(0,0), bmp.Size)
        cls.ai = AniImage(rectangle=rect, bmp= bmp)
        cls.am = AniMatrix(cls.ai)
        

    def test_basic(self):
        #print self.am
        pass

    def test_item(self):
        self.assertEqual(self.am.item(4), [71.0, 0.0, -1.0])
        self.assertEqual(self.am.item(3, 1), [99.0, -1.0, 1.0])
    
class Test_AniKiller(unittest.TestCase):
    ak = None

    @classmethod
    def setUpClass(cls):
        bmp = Bitmap("test_board.jpg")
        rect = Rectangle(Point(0,0), bmp.Size)
        cls.ak = AniKiller(rectangle=rect, bmp= bmp)

    def test_basic(self):
        #print self.ak.areEqual(1, 2)
        #ai = AniImage(force=None)
        #ai.bmp.Save("test_board_boom.jpg", System.Drawing.Imaging.ImageFormat.Jpeg)
        # bmp = Bitmap("test_board_boom.jpg")
        # rect = Rectangle(Point(0,0), bmp.Size)
        # ak = AniKiller(rectangle=rect, bmp = bmp)
        # print ak.cellColors(0)
        # print ak.cellCielab(0, roundup=True)
        pass

    def test_getLocationsForStep(self):
        self.assertEqual(self.ak.getLocationsForStep(1, 2), (-13, 3, 15, -1))
        self.assertEqual(self.ak.getLocationsForStep(0, 2), (-14, 2, 14, -1))
        self.assertEqual(self.ak.getLocationsForStep(24, 2), (10, 26, 38, 22))
        self.assertEqual(self.ak.getLocationsForStep(12, 2), (-2, -1, 26, 10))
        self.assertEqual(self.ak.getLocationsForStep(47, 2), (33, -1, -1, 45))

        self.assertEqual(self.ak.getLocationsForStep(24, 1), (17, 25, 31, 23))

    def test_getLocationsForStepX(self):
        self.assertEqual(self.ak.getLocationsForStepX(24, 1), (18, 32, 30, 16))
        self.assertEqual(self.ak.getLocationsForStepX(1, 2), (-11, 17, -1, -1))
        self.assertEqual(self.ak.getLocationsForStepX(13, 1), (-1, -1, 19, 5))
        self.assertEqual(self.ak.getLocationsForStepX(22, 2), (10, 38, -1, -1))
        self.assertEqual(self.ak.getLocationsForStepX(48, 1), (-1, -1, -1, 40))
        #self.assertEqual(self.ak.getLocationsForStepX(24

    def test_isEqual(self):
        # for p in range(self.ak.cell_count * self.ak.cell_count):
        #     cp = 3
        #     print p, str(self.ak.isEqual(cp, p)), str(self.ak.distance(cp, p))
        self.assertEqual(self.ak.isEqual(-12, 3), False)
        pass

    def test_distance(self):

        aa = [75.0, 36.0, 17.0]
        bb = [74.0, 35.0, 18.0]
        cc = [85.0, 3.0, 67.0]
        dd = [80.0, -42.0, -13.0]
        ee = [100.0, 0.0, -0.0]
        # self.assertEqual(self.ak.distance(aa, bb), 1.7320508075688772)
        # self.assertEqual(self.ak.distance(aa, cc), 60.737138556240858)
        # self.assertEqual(self.ak.distance(aa, dd), 83.719770663804383)
        # self.assertEqual(self.ak.distance(aa, ee), 47.010637094172637)

        self.assertEqual(self.ak.distance(1, 2), 60.737138556240858)

    def test_getTarget(self):
        targets = {}
        targets_result = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: 18, 18: None, 19: None, 20: None, 21: 14, 22: None, 23: None, 24: 25, 25: None, 26: None, 27: 20, 28: None, 29: None, 30: 23, 31: 32, 32: None, 33: None, 34: None, 35: None, 36: None, 37: None, 38: None, 39: 46, 40: 39, 41: 40, 42: None, 43: None, 44: None, 45: None, 46: None, 47: None, 48: None}
        for a in range(49):
            targets[a] = self.ak.getTarget(a)
        self.assertEqual(targets, targets_result)
        

    def test_getTargetX(self):
        self.assertEqual(self.ak.getTargetX(31), 32)
        self.assertEqual(self.ak.getTargetX(39), 46)
        self.assertEqual(self.ak.getTargetX(21), 14)
        self.assertEqual(self.ak.getTargetX(24), 25)
        self.assertEqual(self.ak.getTargetX(41), 40)


    def test_getLocationsForStepS(self):
        self.assertEqual(self.ak.getLocationsForStepS(17, 1, 1), (10, 18))
        self.assertEqual(self.ak.getLocationsForStepS(17, 1, 2), (18, 24))
        self.assertEqual(self.ak.getLocationsForStepS(17, 1, 3), (24, 16))
        self.assertEqual(self.ak.getLocationsForStepS(17, 1, 4), (16, 10))

    def test_getLocationForLineL(self):
        self.assertEqual(self.ak.getLocationForLineL(17, 12), 10)
        self.assertEqual(self.ak.getLocationForLineL(17, 8), 10)
        self.assertEqual(self.ak.getLocationForLineL(17, 32), 18)
        self.assertEqual(self.ak.getLocationForLineL(17, 30), 16)
        self.assertEqual(self.ak.getLocationForLineL(17, 2), 16)
        self.assertEqual(self.ak.getLocationForLineL(17, 4), 18)
        

    def test_startGame(self):
        #AniWindow.click(x, y)
        # ai = AniImage()
        # print ai.Rectangle
        # print AniImageBoard().Rectangle
        pass

class Test_AniImageBoardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): pass
    @classmethod
    def tearDownClass(cls): pass
    def setUp(self): pass
    def tearDown(self): pass

    def test_basic(self):
        # aa = AniImageBoard()
        # aa.setRectangle()
        # print aa.Rectangle

        # bb = AniImageBoard()
        # bb.setRectangle()
        # print bb.Rectangle

        # self.assertEqual(aa.Rectangle, bb.Rectangle)
        pass

    def test_getWindow(self):
        # aa = AniImageBoard()
        # aa.foregroundWindow()
        pass

    def test_setRectangle(self):
        #aa = AniImageBoard()
        #aa.setRectangle()
        #aa = AniImageBoard().setRectangle()
        pass

if __name__ == '__main__':
    unittest.main()
