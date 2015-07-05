import Tkinter as tk
import tkMessageBox
import os
import numpy as np
import cv2
from PIL import Image, ImageTk, ImageDraw


# Supported filetypes
supportedFiletypes = [('JPEG Image', '*.jpg'), ('PNG Image', '*.png'),
 ('PPM Image', '*.ppm')]


def error(msg):
    tkMessageBox.showerror("Error", msg)


class ImageWidget(tk.Canvas):
    '''This class represents a Canvas on which OpenCV images can be drawn.
       The canvas handles shrinking of the image if the image is too big,
       as well as writing of the image to files. '''

    def __init__(self, parent):
        self.imageCanvas = tk.Canvas.__init__(self, parent)
        self.originalImage = None
        self.bind("<Configure>", self.redraw)

    def convertCVToTk(self, cvImage):
        height, width, _ = cvImage.shape
        if height == 0 or width == 0:
            return 0, 0, None
        img = Image.fromarray(cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB))
        return height, width, ImageTk.PhotoImage(img)

    def fitImageToCanvas(self, cvImage):
        height, width, _ = cvImage.shape
        if height == 0 or width == 0:
            return cvImage
        ratio = width / float(height)
        if self.winfo_height() < height:
            height = self.winfo_height()
            width = int(ratio * height)
        if self.winfo_width() < width:
            width = self.winfo_width()
            height = int(width / ratio)
        dest = cv2.resize(cvImage, (width, height),
            interpolation=cv2.INTER_LANCZOS4)
        return dest

    def drawCVImage(self, cvImage):
        self.originalImage = cvImage
        height, width, img = self.convertCVToTk(self.fitImageToCanvas(cvImage))
        if height == 0 or width == 0:
            return
        self.tkImage = img # prevent the image from being garbage collected
        self.delete("all")
        x = (self.winfo_width() - width) / 2.0
        y = (self.winfo_height() - height) / 2.0
        self.create_image(x, y, anchor=tk.NW, image=self.tkImage)

    def redraw(self, _):
        if self.originalImage is not None:
            self.drawCVImage(self.originalImage)

    def writeToFile(self, filename):
        if self.originalImage is not None:
            cv2.imwrite(filename, self.originalImage)

    def hasImage(self):
        return self.originalImage is not None


def showMatrixDialog(parent, text='Ok', rows=0, columns=0, array=None):
    '''This displays a modal dialog with the specified row and columns.'''

    top = tk.Toplevel(parent)

    if rows == 0 or columns == 0:
        assert array is not None
        model = array
    else:
        assert rows > 0 and columns > 0
        model = np.zeros((rows, columns), dtype=np.float)

    cells = []

    for i in range(rows):
        r = []
        for j in range(columns):
            entry = tk.Entry(top)
            entry.insert(0, str(model[i, j]))
            entry.grid(row=i, column=j)
            r.append(entry)
        cells.append(r)

    def acceptButtonClick():
        for i in range(rows):
            for j in range(columns):
                try:
                    model[i, j] = float(cells[i][j].get())
                except:
                    cells[i][j].configure(bg='red')
                    return
        top.destroy()

    wasCancelled = {'value' : False}

    def cancelButtonClick():
        model = None
        wasCancelled['value'] = True
        top.destroy()

    tk.Button(top, text=text, command=acceptButtonClick).grid(row=rows,
        column=columns-1, sticky=tk.E + tk.W)

    tk.Button(top, text='Cancel', command=cancelButtonClick).grid(row=rows,
        column=0, sticky=tk.E + tk.W)

    parent.wait_window(top)

    return None if wasCancelled['value'] else model


def concatImages(imgs):
    # Skip Nones
    imgs = [x for x in imgs if x is not None] # Filter out Nones
    if len(imgs) == 0:
        return None
    imgs = [img for img in imgs if img is not None]
    maxh = max([img.shape[0] for img in imgs]) if imgs else 0
    sumw = sum([img.shape[1] for img in imgs]) if imgs else 0
    vis = np.zeros((maxh, sumw, 3), np.uint8)
    vis.fill(255)
    accumw = 0
    for img in imgs:
        h, w = img.shape[:2]
        vis[:h, accumw:accumw+w, :] = img
        accumw += w
    return vis


if __name__ == '__main__':
    root = tk.Tk()
    frame = tk.Frame(root)

    def doClick():
        showMatrixDialog(frame, rows=3, columns=4)

    tk.Button(frame, text='Click', command=doClick).pack()
    frame.pack()
    root.mainloop()

