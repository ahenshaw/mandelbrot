import time
import wx

from mandelrust import mandelbrot, mandelbrot_mt

VERSION = "0.1.0"
FANCY_APP_NAME = 'Mandelbrot'

MAX_ITER = 100

##########  Code for Python version of Mandelbrot Set computation
def escape_time(c):
    z = 0
    n = 0
    while abs(z) <= 2 and n < MAX_ITER:
        z = z*z + c
        n += 1
    return n

def mandelbrot_python(width, height, left, right, top, bottom):
    pixels = []
    for y in range(height):
        for x in range(width):
            c = complex(left + (x / width) * (right - left), bottom + (y / height) * (top - bottom))
            m = escape_time(c)
            color = 255 - int(m * 255 / MAX_ITER)
            pixels.extend([color, color, color])
    return bytes(pixels)

##########


class Mandelbrot(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.left = -2
        self.right = 1
        self.top   = -1
        self.bottom = 1
        self.bitmap = None
        self.dirty = True
        self.elapsed = None
        self.engine = 'Rust'
        self.stack = []

        self.Bind(wx.EVT_PAINT, self.onPaint)            
        self.Bind(wx.EVT_LEFT_DOWN, self.onClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        self.Bind(wx.EVT_KEY_UP, self.onChar)
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onErase)
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.parent.statusbar.SetStatusText(self.engine, 1)
        
    def onErase(self, event):
        pass

    def onIdle(self, event):
        if self.dirty:
            w, h = self.GetClientSize()
            wait = wx.BusyCursor()
            fn = {'Python': mandelbrot_python, 'Rust': mandelbrot, 'Rust MT': mandelbrot_mt}[self.engine]
            start = time.monotonic()
            pixels = fn(w, h, self.left, self.right, self.top, self.bottom)
            self.elapsed = time.monotonic() - start
            self.bitmap = wx.Bitmap.FromBuffer(w, h, pixels)

            self.dirty = False
            self.Update()
            self.Refresh(False)
            self.parent.statusbar.SetStatusText(f"{self.elapsed:0.3}s", 2)

    def onSize(self, event):
        self.dirty = True
        self.elapsed = None
        self.Update()
        self.Refresh(False)
        w, h = self.GetClientSize()
        self.parent.statusbar.SetStatusText(f'{w} x {h}', 0)
        
    def onClick(self, event):
        x, y = event.GetX(), event.GetY()
        w, h = self.GetClientSize()
        self.stack.append((self.left, self.right, self.top, self.bottom))

        self.reposition(x / w, y / h)
        self.zoom(2)
        self.recompute()
    
    def onRightClick(self, event):
        if self.stack:
            self.left, self.right, self.top, self.bottom = self.stack.pop()
            self.recompute()

    def recompute(self):
        self.dirty = True
        self.elapsed = None
        self.Update()
        self.Refresh(False)
        self.parent.statusbar.SetStatusText(f"Computing...", 2)
    
    def reposition(self, fx, fy):
        span_x = self.right - self.left
        span_y = self.top - self.bottom
        dx = span_x * (0.5 - fx)
        dy = span_y * (0.5 - fy)
        self.left   -= dx
        self.right  -= dx
        self.top    -= dy
        self.bottom -= dy
    
    def zoom(self, scale):
        span_x = self.right - self.left
        span_y = self.top - self.bottom
        cx = (self.right + self.left) / 2
        cy = (self.top + self.bottom) / 2
        self.left   = cx - span_x / 2 / scale
        self.right  = cx + span_x / 2 / scale
        self.top    = cy + span_y / 2 / scale
        self.bottom = cy - span_y / 2 / scale

    def onChar(self, event):
        if event.GetKeyCode() == 27 and self.stack:
            # restore to initial state
            self.stack = [self.stack[0]]
            self.left, self.right, self.top, self.bottom = self.stack.pop()
            self.recompute()
            return
        valid = {'P': 'Python', 'R': 'Rust', 'M': 'Rust MT'}
        try:
            self.engine = valid[chr(event.GetKeyCode())]
            self.recompute()
            self.parent.statusbar.SetStatusText(self.engine, 1)
        except:
            pass
        
    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        w, h = self.GetClientSize()
        if self.bitmap is not None:
            bmp = self.bitmap
            if self.dirty:
                img = bmp.ConvertToImage()
                img = img.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
            dc.DrawBitmap(bmp, 0, 0)


class MainFrame(wx.Frame):
    def __init__(self, **kwargs):
        wx.Frame.__init__(self, None, **kwargs)
        
        self.statusbar = self.CreateStatusBar(4)
        self.statusbar.SetStatusWidths([-1, -1, -1, -3])
        self.statusbar.SetStatusText("Hit 'R' for Rust, 'M' for Rust MT, 'P' for Python rendering", 3)

        self.main = Mandelbrot(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.main, 1, flag=wx.EXPAND|wx.ALL, border=0)
        self.SetSizer(sizer)        


def main():
    app = wx.App(redirect=False)
    frame = MainFrame(title=FANCY_APP_NAME, pos=(100, 0),size=(800, 600))
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()