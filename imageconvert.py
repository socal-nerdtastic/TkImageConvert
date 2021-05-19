#!/usr/bin/env python3

"""
This program will convert images to python/tkinter source code!

This was inspired by the trouble freezing programs (pyinstaller, etc) have in bundleing data with the program. By using images as source code the image data is automatically included in the .exe.

Run this program to create a new python file. Then you can import that new file into your current program to use the images.

Be sure all the files have unique names. This program does not store folder names.

# EXAMPLE: to show an image:
import tkinter as tk
from images import load_image
root = tk.Tk()
lbl = tk.Label(image=load_image('myphotoname.gif'))
lbl.pack()
root.mainloop()

# EXAMPLE: to use as a tkinter icon:
from images import load_image
root = tk.Tk()
root.iconphoto(True, load_image('myphotoname.jpg'))
root.mainloop()
"""

# todo:
# improve help text popup
# add resize option to GUI if PIL is available
# add custom use documentation into success popup window

import os
import base64
import io
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
    PIL = True
except ImportError:
    PIL = False

PIL_FILETYPES = (
    ("Image files",
        ("*.jpg", "*.jpeg", "*.gif", "*.png", )
        ),
    ("All files","*.*"))
NOPIL_FILETYPES = (
    ("GIF files",
        ("*.gif",)
        ),
    ("All files","*.*"))
FILETYPES = PIL_FILETYPES if PIL else NOPIL_FILETYPES

TEMPLATE = r"""#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from functools import lru_cache

IMAGES = {{
{}
}}

@lru_cache(None)
def load_image(name):
    return tk.PhotoImage(data=IMAGES[name])

def main():
    def disp_image(*args):
        disp.config(image=load_image(var.get()))
    root = tk.Tk()
    tk.Label(text="Image tester:").grid()
    var = tk.StringVar()
    ttk.OptionMenu(root, var, "choose an image:", *IMAGES, command=disp_image).grid(column=1, row=0)
    disp = tk.Label(root)
    disp.grid(columnspan=2)
    root.mainloop()

if __name__ == '__main__':
    main()
"""

def convert_to_b64(filename, new_size=None):
    """resize only works in PIL mode"""
    if PIL:
        img = Image.open(filename)
        if new_size:
            img = img.resize(new_size)
        f = io.BytesIO()
        img.save(f, format='GIF')
        b64_img = base64.encodestring(f.getvalue())
    else:
        with open(filename, 'rb') as f:
            b64_img = base64.encodestring(f.read())
    return b64_img.decode()

def pip_install_popup():
    """In some situations, this will crash if you try to install a module that is currently imported :/"""
    INSTALL = "pillow"
    from subprocess import Popen, PIPE
    import sys
    import tkinter as tk
    from tkinter import ttk
    from tkinter.scrolledtext import ScrolledText
    from threading import Thread

    def pipe_reader(pipe, term=False):
        for line in iter(pipe.readline, b''):
            st.insert(tk.END, line)
            st.see(tk.END)
        if term:
            popup.event_generate("<<done>>")
    def disp_done(event=None):
        tk.Label(popup, fg='red', text="DONE. Restart required.", font=('bold',14)).pack()
        ttk.Button(popup, text="Exit program", command=sys.exit).pack()
    popup = tk.Toplevel()
    popup.bind("<<done>>", disp_done)
    tk.Label(popup, text="Installing: "+INSTALL, font=('bold',14)).pack()
    st= ScrolledText(popup, width=60, height=12)
    st.pack()
    sub_proc = Popen([sys.executable, '-m','pip', 'install', INSTALL], stdout=PIPE, stderr=PIPE)
    Thread(target=pipe_reader, args=[sub_proc.stdout]).start()
    Thread(target=pipe_reader, args=[sub_proc.stderr, True]).start()

class ScrolledListbox(tk.Listbox):
    def __init__(self, master=None, **kwargs):
        self.frame = tk.Frame(master)
        self.vbar = tk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        kwargs.update({'yscrollcommand': self.vbar.set})
        super().__init__(self.frame, **kwargs)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar['command'] = self.yview
        text_meths = vars(tk.Listbox).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
    def __str__(self):
        return str(self.frame)

def helpdisp(*args):
    popup = tk.Toplevel()
    tk.Message(popup, text=__doc__).pack()
    ttk.Button(popup, text="OK", command=popup.destroy).pack()

class GUI(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.files = []

        helpbtn = tk.Label(self, text="Help",relief=tk.RIDGE)
        helpbtn.pack(anchor='w')
        helpbtn.bind("<1>", helpdisp)

        title = tk.Label(self, text="Tkinter image interner", font=('bold',15))
        title.pack()

        if not PIL:
            warn_frame = ttk.LabelFrame(self, text="WARNING")
            warn_frame.pack(fill=tk.X, expand=True)
            lbl = tk.Label(warn_frame, text="Pillow (PIL) not installed.\nOnly .gif files will work", fg='red')
            lbl.pack()
            btn = ttk.Button(warn_frame, text="Install Pillow Now.", command=pip_install_popup)
            btn.pack()
        file_frame = ttk.LabelFrame(self, text="Image Input Files:")
        file_frame.pack(fill=tk.X, expand=True)
        btn = ttk.Button(file_frame, text="Browse", command=self.browse)
        btn.pack()
        self.filesdisp = ScrolledListbox(file_frame)
        self.filesdisp.pack(fill=tk.X, expand=True)

        outframe = ttk.LabelFrame(self, text="Output .py File:")
        outframe.pack(fill=tk.X, expand=True)
        self.fn = tk.StringVar(value="images.py")
        ent = tk.Entry(outframe, textvariable=self.fn)
        ent.pack(fill=tk.X, expand=True)

        gotime = ttk.Button(self, text="START!", command=self.calculate)
        gotime.pack()

    def browse(self):
        filenames = filedialog.askopenfilenames(initialdir='.', filetypes=FILETYPES)
        if not filenames: return # user cancel
        for fn in filenames:
            fn = os.path.normpath(fn)
            name = os.path.split(fn)[1]
            self.filesdisp.insert(tk.END, name)
            self.files.append((fn, name))

    def calculate(self):
        if os.path.exists(self.fn.get()):
            ans = messagebox.askyesno('File conflict', "The output file already exists!\nOverwrite?")
            if not ans: return
        try:
            b64_data = []
            for fn, name in self.files:
                data = convert_to_b64(fn)
                b64_data.append(f'"{name}": """\n{data}""",')
            with open(self.fn.get(), 'w') as f:
                f.write(TEMPLATE.format('\n'.join(b64_data)))
            messagebox.showinfo("Success!", f"Success!\n  {self.fn.get()}\nwas created!")
        except Exception as e:
            messagebox.showerror("ERROR!", str(e))
            raise

def main():
    root = tk.Tk()
    window = GUI(root)
    window.pack()
    root.mainloop()

if __name__ == '__main__':
    main()
