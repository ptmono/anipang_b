using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;
using System.Drawing;

namespace UnmanagedCode
{
    public class GDI32
    {
        [DllImport("GDI32.dll")]
        public static extern IntPtr CreateCompatibleDC(IntPtr hdc);

        [DllImport("GDI32.dll")]
        public static extern IntPtr CreateCompatibleBitmap(IntPtr hdc, int nWidth,
							   int nHeight);

        [DllImport("GDI32.dll")]
        public static extern IntPtr SelectObject(IntPtr hdc, IntPtr hgdiobj);

        [DllImport("GDI32.dll")]
        public static extern bool BitBlt(IntPtr hdcDest, int nXDest, int nYDest,
                                         int nWidth, int nHeight, IntPtr hdcSrc,
                                         int nXSrc, int nYSrc, TernaryRasterOperations dwRop);


        [DllImport("GDI32.dll")]
        public static extern bool DeleteDC(IntPtr hdc);

        [DllImport("GDI32.dll")]
        public static extern bool DeleteObject(IntPtr hObject);

	[DllImport("gdi32.dll")]
	public static extern uint GetPixel(IntPtr hdc, int nXPos, int nYPos);

	public enum TernaryRasterOperations : uint {
	    SRCCOPY     = 0x00CC0020,
	    SRCPAINT    = 0x00EE0086,
	    SRCAND      = 0x008800C6,
	    SRCINVERT   = 0x00660046,
	    SRCERASE    = 0x00440328,
	    NOTSRCCOPY  = 0x00330008,
	    NOTSRCERASE = 0x001100A6,
	    MERGECOPY   = 0x00C000CA,
	    MERGEPAINT  = 0x00BB0226,
	    PATCOPY     = 0x00F00021,
	    PATPAINT    = 0x00FB0A09,
	    PATINVERT   = 0x005A0049,
	    DSTINVERT   = 0x00550009,
	    BLACKNESS   = 0x00000042,
	    WHITENESS   = 0x00FF0062,
	    CAPTUREBLT  = 0x40000000 //only if WinVer >= 5.0.0 (see wingdi.h)
	}

    }

    public class User32
    {
        [DllImport("user32.dll")]
        public static extern IntPtr GetDesktopWindow();

        [DllImport("user32.dll")]
        public static extern IntPtr GetTopWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern IntPtr GetWindow(IntPtr hWnd, uint wCmd);

        [DllImport("User32.dll")]
        public static extern IntPtr GetWindowDC(IntPtr hWnd);

        [DllImport("User32.dll")]
        public static extern IntPtr ReleaseDC(IntPtr hWnd, IntPtr hDC);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);


	[DllImport("user32.dll", EntryPoint="FindWindow", SetLastError = true)]
	public static extern IntPtr FindWindowByCaption(IntPtr ZeroOnly, string lpWindowName);


	[DllImport("user32.dll", SetLastError = true)]
	public static extern IntPtr FindWindowEx(IntPtr parentHandle, IntPtr childAfter, string className,  string windowTitle);

	[DllImport("user32.dll", SetLastError=true)]
	public static extern void SwitchToThisWindow(IntPtr hWnd, bool fAltTab);

	[DllImport("user32.dll", SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool GetWindowRect(IntPtr hWnd, ref WRECT lpRect);
	[StructLayout(LayoutKind.Sequential)]
	public struct WRECT
	{
	    public int Left;
	    public int Top;
	    public int Right;
	    public int Bottom;
	}

	[DllImport("user32.dll")]
	public static extern IntPtr GetDC(IntPtr hwnd);

	[DllImport("user32.dll",EntryPoint="GetSystemMetrics")]
	public static extern int GetSystemMetrics(int nIndex);




	[DllImport("user32.dll")]
	public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData,
				       int dwExtraInfo);
    }
}

namespace DLibs
{
    using UnmanagedCode;

    public static class MonoPix
    {
	public static Bitmap GetDesktop()
	    {
		int screenX;
		int screenY;
		IntPtr hBmp;
		IntPtr  hdcScreen = User32.GetDC(User32.GetDesktopWindow());
		IntPtr hdcCompatible = GDI32.CreateCompatibleDC(hdcScreen);

		screenX = User32.GetSystemMetrics(0);
		screenY = User32.GetSystemMetrics(1);
		hBmp = GDI32.CreateCompatibleBitmap(hdcScreen, screenX, screenY);

		if (hBmp!=IntPtr.Zero)
		{
			IntPtr hOldBmp = (IntPtr) GDI32.SelectObject(hdcCompatible, hBmp);
			GDI32.BitBlt(hdcCompatible, 0, 0,screenX,screenY, hdcScreen, 0, 0, GDI32.TernaryRasterOperations.SRCCOPY);
			
			GDI32.SelectObject(hdcCompatible, hOldBmp);
			GDI32.DeleteDC(hdcCompatible);
			User32.ReleaseDC(User32.GetDesktopWindow(), hdcScreen);
			
			Bitmap bmp = System.Drawing.Image.FromHbitmap(hBmp); 
			
			GDI32.DeleteObject(hBmp);
			GC.Collect();
			
			return bmp;
		}
		
		return null;
	    }


	public static Bitmap getRegion(Rectangle rect)
	    {
		int x = rect.X;
		int y = rect.Y;
		int width = rect.Width;
		int height = rect.Height;
		IntPtr hBmp;
		IntPtr  hdcScreen = User32.GetDC(User32.GetDesktopWindow());
		IntPtr hdcCompatible = GDI32.CreateCompatibleDC(hdcScreen);

		hBmp = GDI32.CreateCompatibleBitmap(hdcScreen, width, height);

		if (hBmp!=IntPtr.Zero)
		{
			IntPtr hOldBmp = (IntPtr) GDI32.SelectObject(hdcCompatible, hBmp);
			GDI32.BitBlt(hdcCompatible, 0, 0, width, height, hdcScreen, x, y, GDI32.TernaryRasterOperations.SRCCOPY);
			
			GDI32.SelectObject(hdcCompatible, hOldBmp);
			GDI32.DeleteDC(hdcCompatible);
			User32.ReleaseDC(User32.GetDesktopWindow(), hdcScreen);
			
			Bitmap bmp = System.Drawing.Image.FromHbitmap(hBmp); 
			
			GDI32.DeleteObject(hBmp);
			GC.Collect();
			
			return bmp;
		}
		
		return null;
	    }

	
    }
    
}
