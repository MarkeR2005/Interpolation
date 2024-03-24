from customtkinter import *
from tkinterdnd2 import TkinterDnD, DND_ALL
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as polynom

#prebuiltSettings
matplotlib.use('TkAgg')
set_appearance_mode("system")
set_default_color_theme("blue")

#mainClass
class windowApp(CTk, TkinterDnD.DnDWrapper):
    def __init__(self, size, *args,**kwargs) -> None:
        super().__init__(*args,**kwargs)
        #sharedData
        self.dataVar = 'no file is present'
        self.points = []
        self.values = []

        self.Tkdndversion = TkinterDnD._require(self)
        self.title("Interpolation program")
        self.geometry(size)
        for i in range(10):
            self.rowconfigure(i, weight= 1)
            self.columnconfigure(i, weight= 1)

        #Input
        self.label = CTkLabel(self, text= "Enter a csv file with data", width= 180, height= 50)
        self.upbutton = CTkButton(self, text= "drop file here", command= self.loadfile, width = 180, height= 50)
        self.filebutton = CTkButton(self, text= "or open file dialog", command= self.filedialog, width = 180, height= 50)
        self.upbutton.drop_target_register(DND_ALL)
        self.upbutton.dnd_bind('<<Drop>>', self.uploadfile)

        self.showInput()

        #Control
        self.inputButton = CTkButton(self, text= "select other file", command= self.showInput, width = 180, height= 50)
        self.check_var1 = StringVar(value=0)
        self.LagrangeCheck = CTkCheckBox(self,text="draw Lagrange polynoms", variable=self.check_var1, onvalue=1, offvalue=0)
        self.check_var2 = StringVar(value=0)
        self.SplineCheck = CTkCheckBox(self,text="draw Splines polynoms", variable=self.check_var2, onvalue=1, offvalue=0)
        self.drawButton = CTkButton(self, text="draw graph", command=self.draw, width=180, height=50)
        self.clearButton = CTkButton(self, text = 'clear', command=self.clear, width=180, height=50)

        #Data
        self.frame = dataFrame(master=self)

        self.spec = CTkFrame(master= self, height=200,width=300)
        self.inter = Interpolation(self.spec, [],[])
        self.inter.get_tk_widget().pack()
        #self.nav = NavigationToolbar2Tk(self.inter, self)
        #essential
        self.protocol("WM_DELETE_WINDOW", quit)
        self.mainloop()
        
        #inputmethods
    def showInput(self):
        try:
            self.hideData()
        except:
            pass
        self.label.grid(sticky = 'nsew')
        self.upbutton.grid(sticky = 'nsew')
        self.filebutton.grid(sticky = 'nsew')

    def hideInput(self):
        self.label.grid_remove()
        self.upbutton.grid_remove()
        self.filebutton.grid_remove()


    def uploadfile(self, event):
        self.dataVar = event.data
        self.label.configure(text= str(self.dataVar).split('/')[-1]+' click to read')

    def filedialog(self):
        self.dataVar = filedialog.askopenfilename()
        self.label.configure(text= str(self.dataVar).split('/')[-1]+' click to read')

    def loadfile(self):
        try:
            data = pd.read_csv(self.dataVar, sep= ';', dtype= np.double)
            self.points, self.values = np.round(data.to_numpy().transpose(),6)
            self.hideInput()
            self.showData()
        except:
            self.label.configure(text= 'no proper file is present')




    #dataMethods
    def showData(self):  

        #Data
        self.frame = dataFrame(array =[self.points, self.values],master = self, height = 500, width=200)
        self.inter.get_tk_widget().pack_forget()
        self.inter = Interpolation(master = self.spec,points= self.points,values= self.values, height = 500)

        self.frame.grid(sticky = 'nsew')
        self.inter.get_tk_widget().pack()
        self.spec.grid(sticky='nsew')

        self.inter.config()

        self.inputButton.grid(sticky = 'nsew')
        self.LagrangeCheck.grid(sticky = 'nsew')
        self.SplineCheck.grid(sticky = 'nsew')
        self.drawButton.grid(sticky = 'nsew')
        self.clearButton.grid(sticky = 'nsew')

    def hideData(self):
        self.frame.grid_remove()
        self.spec.grid_remove()
        self.inputButton.grid_remove()
        self.LagrangeCheck.grid_remove()
        self.SplineCheck.grid_remove()
        self.drawButton.grid_remove()
        self.clearButton.grid_remove()


    #graphicsMethods
    def draw(self):
        count = counter(self.points, self.values)
        if self.check_var1.get() == '1':
            self.inter.addGraph(count.eval_Lag_poly(),color='blue', label='Интерполяция многочленами Лагранжа')
        if self.check_var2.get() == '1':
            self.inter.addGraph(count.eval_cubic_spl(), color='orange', label ='Интерполяция кубическими сплайнами')
        else:
            self.inter.draw()
    def clear(self):
        try:
            self.inter.clear()
        except:
            pass


#classToCalculateInterpolationCoefficient
class counter():
    def __init__(self, points, values):
        self.points = points
        self.values = values
        self.n = len(points)


    #LagrangePolynomCalculation
    def Lag_poly_basis(self):
        points = self.points.tolist()
        l = []
        for i in range(self.n):
            l.append(polynom.Polynomial.fromroots(points[:i:]+points[i+1:self.n:]))
            for j in range(self.n):
                if i == j:
                    continue
                l[i]= l[i] // polynom.Polynomial(np.round(points[i]-points[j],9))
        return l
    def Lag_poly(self):
        return np.sum((self.values[i] * self.Lag_poly_basis()[i] for i in range(self.n)))
    def eval_Lag_poly(self):
        x = self.points
        pln = self.Lag_poly()
        xx, yy = pln.linspace(1000, [min(x),max(x)])
        return (xx, yy)
    

    #CubicSplinesCalculation
    def calc_cubic_spl(self):
        n = self.n-1
        h = np.diff(self.points)
        df = np.diff(self.values) / h
        A = np.zeros((n+1, n+1))
        B = np.zeros(n+1)
        A[0, 0] = 1
        A[n, n] = 1
        for i in range(1, n):
            A[i, i-1] = h[i-1]
            A[i, i] = 2 * (h[i-1] + h[i])
            A[i, i+1] = h[i]
            B[i] = 3 * (df[i] - df[i-1])
        c = np.linalg.solve(A, B)
        d = np.diff(c) / (3 * h)
        b = df - h * (2 * c[:-1] + c[1:]) / 3
        return b, c[:-1], d
    def eval_cubic_spl(self):
        x, y = self.points, self.values
        b, c, d = self.calc_cubic_spl()
        n = len(x) - 1
        xx = np.linspace(x[0], x[-1], 1000)
        yy = np.piecewise(xx, [((x[i] <= xx) & (xx <= x[i+1])) for i in range(n)],
                        [lambda xx, i=i: y[i] + b[i] * (xx - x[i]) + c[i] * (xx - x[i])**2 + d[i] * (xx - x[i])**3 for i in range(n)])
        return (xx, yy)



#WindowSubclassForBetterTable
class dataFrame(CTkScrollableFrame):
    def __init__(self, array = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        for j, x in enumerate(array):
              for i, proc in enumerate(x):
                self.app_frame = CTkFrame(
                    master=self,
                    width=100,
                    height=50,
                    corner_radius=3,
                    border_width=0,
                    
                )
                self.app_name_label = CTkLabel(
                    self.app_frame,
                    text=proc,
                )
                self.app_frame.grid(row=i, column=j, pady=2) 
                self.app_name_label.place(y=25, x=20)

    

#PlotClass
class Interpolation(FigureCanvasTkAgg):
        
    def __init__(self, master ,points, values, *args,**kwargs):
        #SharedData
        self.fig = plt.Figure(figsize=(10, 8))
        self.points = points
        self.values = values
        super().__init__(self.fig, master)
        #self._tkcanvas.configure(*args, **kwargs)
        #self.nav = NavigationToolbar2Tk(self, self)
        #BasicPlot
        self.ax = self.fig.add_subplot()
        self.ax.plot(points,values,'o',label = 'точки',color = 'red')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.fig.tight_layout()

    #drawMethodToUpdatePlot
    def draw(self):
        self.config()
        a, b = self.ax.get_legend_handles_labels()
        self.fig.legend(a,b)
        super().draw()
        plt.show()

    #UsefulMethod
    def config(self):
        minv = min(self.values)
        maxv = max(self.values)
        minp = min(self.points)
        maxp = max(self.points)
        self.ax.set_ylim(minv-0.1*abs(minv), maxv+0.1*abs(maxv))
        self.ax.set_xlim(minp-0.1*abs(minp), maxp+0.1*abs(maxp))
        self.ax.set_xticks(np.linspace(int(minp),int(maxp),20))
        self.ax.set_yticks(np.linspace(int(minv),int(maxv),20))

    #GraphDrawerMethod
    def addGraph(self, dots, color, label):
        xx,yy =dots
        self.ax.plot(xx, yy, color, label)
        self.config()
        self.draw()

    #CleanerMethod
    def clear(self):
        self.ax.cla()
        self.ax.plot(self.points,self.values,'o',label = 'точки',color='red')
        self.draw()

    def destroy(self):
        self._tkcanvas.destroy()

wind = windowApp("600x400")
