import tkinter.ttk as tk_
import tkinter as tk
from tkinter.ttk import Label, Button, LabelFrame
from tkinter import Canvas
import asyncio
import cv2
from PIL import Image, ImageTk

'''
Python >3.9
Polma Izhak Eliyahu
08 june 2022
ver 0.1

A simple program in one file - for readability
Makes two asynchronous processes:
    - prints to terminal
    - shows two forms in tkinter with internal camera video

Requires asyncio, opencv, Pillow, tkinter libraries to work
'''

class GUIButtonsTest:
    '''
    Class with test buttons
    '''    
    def __init__(self):        
        self.label_fr_main = LabelFrame(self.master, text = "Control buttons")
        self.label_fr_main.pack(side = tk.RIGHT, padx = 5, pady= 5)

        self.label = Label(self.label_fr_main, text="This is our first GUI!")
        self.label.pack(side = tk.LEFT, padx = 5, pady= 5)

        self.greet_button = Button(self.label_fr_main, text="Greet", command=self.greet)
        self.greet_button.pack(side = tk.LEFT, padx = 5, pady= 5)

        self.close_button = Button(self.label_fr_main, text="Close", command=self.master_state)
        self.close_button.pack(side = tk.LEFT, padx = 5, pady= 5)
        
        
    def greet(self, text= "Greetengs!"):
        '''Function for send string to the terminal'''
        print(text)


class GUIClass:
    '''
    Base my class for Tkinter forms - updates and destroy
    '''
    
    flag_run = False # False - stop updates and destroy, True - continue updates

    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.master_state) #For on press close make some function
        self.flag_run = True
        self.update_period = 0.1


    def master_state(self):
        '''make state flag_run to False for stop updates of form and destroy'''
        print(f'destroy {self.master.title()}')
        self.flag_run = False

    async def update_tk(self):
        '''function for redescribing in children - append some procedures before update'''
        self.master.update_idletasks()
        self.master.update()

    async def destroy(self):
        if (len(self.master.children) > 0): # if form was destroyed, she not contains childrens
            self.master.destroy()
        self.master.quit()

    async def go(self):
        '''life function for form'''    
        while (self.flag_run or self.master == None):
            await self.update_tk()
            await asyncio.sleep(self.update_period)
        await self.destroy()

    def __del__(self):        
        print("stop win")


class GUIClassSimple(GUIClass, GUIButtonsTest):
    '''
    Sample GUI form on base class functionality and class with simle buttons
    '''
    
    def __init__(self, master):
        GUIClass.__init__(self, master)
        self.master.title("GUI Simple Form")
        GUIButtonsTest.__init__(self)


class GUIClassVideo(GUIClass, GUIButtonsTest):
    '''
    GUI class for video frames from internal cam
    '''


    def __init__(self, master, cap):
        self.master = master
        self.window = tk.Toplevel(master)
        self.top_level = False
        GUIClass.__init__(self, self.window)
        
        #self.window = window
        self.cap = cap
        max_image_size = max(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = max_image_size
        self.height = max_image_size
        self.interval = 10 # Interval in ms to get the latest frame
        
        self.label_fr_canvas = LabelFrame(self.window, text = "Live image from source")
        self.label_fr_canvas.pack(side=tk.TOP, padx = 5, pady = 5)
        
        # Create canvas for image
        
        self.canvas = tk.Canvas(self.label_fr_canvas, width=self.width, height=self.height)
        #self.canvas.grid(row=0, column=0)
        self.canvas.pack()
        self.update_period = 0.01

        self.flag_rot = 3 #without rotate, 0 - rot90, 1 - rot 180, 2 - rot 270
        self.flag_flip = 2 # 2 = not flip #a flag to specify how to flip the array; 0 means flipping around the x-axis and positive value (for example, 1) means flipping around y-axis. Negative value (for example, -1) means flipping around both axes. 
        self.label_fr_rotate = LabelFrame(self.window, text = "Operations with image")
        self.label_fr_rotate.pack(side=tk.LEFT, padx = 5, pady = 5)
        
        self.rotate_clkw_button = Button(self.label_fr_rotate, text="Rotate 90", command=lambda: self.rotate_flag_chng(1, 0))
        self.rotate_clkw_button.pack(side=tk.LEFT, padx = 5, pady = 5)
        self.rotate_aclkw_button = Button(self.label_fr_rotate, text="Rotate -90", command=lambda: self.rotate_flag_chng(-1, 0))
        self.rotate_aclkw_button.pack(side=tk.LEFT, padx = 5, pady = 5)
        self.rotate_fliph_button = Button(self.label_fr_rotate, text="Flip hor", command=lambda: self.rotate_flag_chng(0, 1))
        self.rotate_fliph_button.pack(side=tk.LEFT, padx = 5, pady = 5)
        self.rotate_flipv_button = Button(self.label_fr_rotate, text="Flip vert", command=lambda: self.rotate_flag_chng(0, 2))
        self.rotate_flipv_button.pack(side=tk.LEFT, padx = 5, pady = 5)
        
        GUIButtonsTest.__init__(self)

    def rotate_flag_chng(self, rotate_flag = 0, flip_flag = 0):
        '''
        flags for opencv 'flip' function
        '''
        self.flag_rot  = (self.flag_rot + rotate_flag) % 4
        self.flag_flip = ((((self.flag_flip + 1) ^ flip_flag))&7) - 1

    async def rotate_image(self, image):
        '''
        make rotates for every frame
        '''
        im_res = image.copy()
        if (self.flag_rot <3) and (self.flag_rot > -1):
            im_res = cv2.rotate(image.copy(), self.flag_rot)
        if (self.flag_flip > -2) and (self.flag_flip < 2):
            
            im_res = cv2.flip(im_res.copy(), self.flag_flip)
        
        return im_res

    async def update_image(self):
        ''' 
        Get the latest frame and convert image format
        '''
        ret, im = self.cap.read()
        if ret:
            try:
                image = await self.rotate_image(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)) # to RGB
                image1 = Image.fromarray(image) # to PIL format
                # Update image
                self.image2 = ImageTk.PhotoImage(image1) # to ImageTk format
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image2)
            except:
                print("stop")
                self.flag_run = False
                

    async def update_tk(self):
        await self.update_image()
        await asyncio.sleep(self.update_period)
        if (self.top_level): #if is form - main form, make update, else - not
            await super().update_tk()
    
    async def destroy(self):
        if (len(self.window.children) > 0):
            self.window.destroy()
            print("destroy")
            self.window.update()
        if (self.top_level):
            self.window.quit()

    async def go(self):    
        while (self.flag_run or self.master == None):            
            await self.update_tk()
            await asyncio.sleep(self.update_period)
        await self.destroy()


class StartClass:
    ''' Class with main data
    '''    

    def __init__(self):
        print("go")
        self.root = tk.Tk()
    
    def __del__(self):
        print("stop")

    async def get_root(self):
        return self.root

    async def init_form_simple(self):
        return GUIClassSimple(await self.get_root())        

    async def init_form_video(self, video_object):
        return GUIClassVideo(await self.get_root(), video_object)        
        

    async def form_main(self):
        #main
        new_form_obj1 = await self.init_form_simple()
        #next level
        new_form_obj2 = await self.init_form_video(cv2.VideoCapture(0))
        Task1 = asyncio.create_task(new_form_obj1.go())
        Task2 = asyncio.create_task(new_form_obj2.go())
        await Task1
        print("ok")

class Repeat_data:
    '''
    Simple class with repeat data to terminal for demonstrate async
    '''

    def __init__(self):
        print("rep")

    async def for_rep(self):
        for i in range(50):
            print(i)
            await asyncio.sleep(0.1)


async def main():
    start_class_object = StartClass()
    start_class_object1 = Repeat_data()

    Task1 = asyncio.create_task(start_class_object.form_main())
    Task2 = asyncio.create_task(start_class_object1.for_rep())
    
    await Task1 
    await Task2

    start_class_object = None
    start_class_object1 = None

asyncio.run(main())