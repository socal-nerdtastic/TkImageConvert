# TkImageConvert
Convert image files to python / tkinter source code

Are you having trouble freezing / packaging your tkinter program with Pyinstaller, py2exe, etc because you can't figure out how to include the image files in your program? Or do you just want fewer files in your program? 

Here's an easy fix! Convert your images to python source code and import them. That way they are automatically included in any .exe. 

Just run this program, select some image files, and click start. A new python file will be created for you with all your images in it. To use the new file in your existing code just put it in the same folder as your current code and import it. For example instead of 

    img = PhotoImage(file='cat.jpg')
    
You would use 

    from images import load_image # assuming you named the new file "images.py"
    img = load_image('cat.jpg')
    
As a bonus this means that you no longer need to worry about tkinter image references going out of scope!

## help wanted: 

Pull requests appreciated. Especially for updating this readme with a better guide and maybe images. But also for code. 
