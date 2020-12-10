from tkinter import *
import random
from time import sleep
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


############# Graphics layer functions
def DrawLine(canvas, x1, y1, x2, y2, color, w, tag=''):
    canvas.create_line(x1, y1, x2, y2, fill=color, width=w, tags = tag)

def DrawCircle(canvas, x, y, r, fill_color, stroke_color, w, tag=''):
    canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline=stroke_color, width=w, tags = tag)

def DrawRectangle(canvas, x1, y1, x2, y2, fill_color, stroke_color, tag=''):
    canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline = stroke_color, tags = tag)

def DrawText(canvas, x, y, text, size, color, tag=''):
    canvas.create_text(x, y, fill=color, font=("Arial", size), text=text, tags = tag)
##############

# Count alive bots
def Alive(Bots):
    c = 0
    for i in Bots:
        if i.dead == 0:
            c += 1
    return c

# Food and poison function
def Food(canvas, state, Bot_size, Field_size, x = None, y = None):
    if str(x)+':'+str(y) in Resources.keys() or str(x)+':'+str(y) in Positions.keys():
        return
    if state == 1:
        color = '#00cc00'
    else:
        color = '#cc0000'
    if x is None or y is None:
        x = random.randint(0, Field_size-1)
        y = random.randint(0, Field_size-1)
    Resources[str(x)+':'+str(y)] = state
    DrawCircle(canvas, x*Bot_size+Bot_size/2, y*Bot_size+Bot_size/2, Bot_size/2-3, color, color, 1, "resource_"+str(x)+'_'+str(y))

# Bots class
class Bot():
    def __init__(self, x=0, y=0, dna=[0], color='blue', text_color='white', index=None, canvas=None):
        self.x = x
        self.y = y
        self.dna = dna
        self.color = color
        self.text_color = text_color
        self.energy = 99
        self.size = Bot_size
        self.cannibal = 0
        self.dna_cursor = 0
        self.DNA_run_count = 0
        self.index = index
        self.dead = 0
        self.love = None
        self.direction = None
        self.canvas = canvas
        
    def Energy(self, x):
        self.energy += x
        if self.energy>99:
            self.energy = 99
        if self.energy <= 0:
            self.dead = 1
        
    def MixDNA(self, DNA):
        #print (len(DNA))
        for i in range(len(DNA)):
            if random.randint(0,5) == 0:
                self.dna[i] = DNA[i]
    
    def Show(self):
        if str(self.x)+':'+str(self.y) in Positions.keys() and self.love is not None and Love:
            #print ('Lets make love!', self.index, Positions[str(self.x)+':'+str(self.y)])
            #print('B.mix:', self.dna, Positions[str(self.x)+':'+str(self.y)])
            self.MixDNA(Bots[Positions[str(self.x)+':'+str(self.y)]].dna)
            #print('A.mix:', self.dna)
            self.color = 'pink'
            self.text_color = 'black'
            #Bots[Positions[str(self.x)+':'+str(self.y)]].energy = 0
        Positions[str(self.x)+':'+str(self.y)] = self.index
        DrawRectangle(self.canvas, self.x*Bot_size+1, self.y*Bot_size+1, self.x*Bot_size+self.size-1, self.y*Bot_size+self.size-1, self.color, self.color, "bot_"+str(self.index))
        DrawText(self.canvas, self.x*Bot_size+8, self.y*Bot_size+8, str(self.energy), Font_size, self.text_color, "bot_energy_"+str(self.index))
        
    def Hide(self):
        Positions.pop(str(self.x)+':'+str(self.y), None)
        self.canvas.delete("bot_"+str(self.index))
        self.canvas.delete("bot_energy_"+str(self.index))
    
    # Main action function
    def Look(self, task=0, n=1):
        x = self.x
        y = self.y
        self.love = None
        
        for i in range(16):
            if self.direction is not None:
                direction = self.direction
            else:
                direction = random.randint(0, 7)
            if direction == 0:
                y = y - n
            if direction == 1:
                y = y - n
                x = x + n
            if direction == 2:
                x = x + n
            if direction == 3:
                x = x + n
                y = y + n
            if direction == 4:
                y = y + n
            if direction == 5:
                y = y + n
                x = x - n
            if direction == 6:
                x = x - n
            if direction == 7:
                y = y - n
                x = x - n
                
            if x<0 or x>=Field_size:
                x = 0
            if y<0 or y>=Field_size:
                y = 0
                
            if (str(x)+':'+str(y)) in Resources.keys():
                if task == 1 and Resources[str(x)+':'+str(y)] == 1:
                    #print('I see food!', self.dna, task, self.energy, len(Bots))
                    self.x = x
                    self.y = y
                    Resources.pop(str(x)+':'+str(y), None)
                    self.canvas.delete("resource_"+str(x)+'_'+str(y))
                    self.Energy(10)
                    if self.energy < 30:
                        self.direction = direction
                if 4>=task>1 and Resources[str(x)+':'+str(y)] == 2:
                    #print('Convert poison!', self.dna, task, self.energy, len(Bots))
                    Resources.pop(str(x)+':'+str(y), None)
                    self.canvas.delete("resource_"+str(x)+'_'+str(y))
                    Food(self.canvas, 1, Bot_size, Field_size, x, y)
                    self.x = x
                    self.y = y
                    self.Energy(5)
                    self.direction = None
                if 5>=task>4 and (str(x)+':'+str(y)) in Positions.keys():
                    #print('Go to love!', self.dna, task, self.energy, len(Bots))
                    self.x = x
                    self.y = y
                    self.Energy(5)
                    self.love = 1
                    self.direction = None
            if 7>=task>5:
                #print('Goto random cell', self.dna, task, self.energy)
                self.x = x
                self.y = y
                if str(x)+':'+str(y) in Resources.keys() and Resources[str(x)+':'+str(y)] == 2:
                    #print('Eat poison!', self.dna, task, self.energy)
                    self.Energy(-100)
                return
            if str(x)+':'+str(y) not in Resources.keys() and task>7:
                #print('Goto free cell', self.dna, task, self.energy)
                self.x = x
                self.y = y
                self.direction = None
                return
        #print ('No move!')
    
    def NextDNA(self):
        self.dna_cursor = self.dna_cursor + 1
        if self.dna_cursor>len(self.dna)-2:
            self.dna_cursor = 0
    
    def RunDNA(self):
        self.NextDNA()
        # Look:
        if self.dna[self.dna_cursor]<20:
            self.Energy(-1)
            task = self.dna[self.dna_cursor+1] % 10
            n = 1
            self.Hide()
            self.Look(task, n)
            if self.dead == 0:
                self.Show()
        # Goto:
        if self.dna[self.dna_cursor]==20:
            self.dna_cursor = self.dna[self.dna_cursor+1]
            self.Energy(-1)
            if self.dead == 0:
                self.DNA_run_count += 1
                if self.DNA_run_count < 20:
                    self.RunDNA()
                else:
                    self.dna_cursor = 0
                    self.DNA_run_count = 0
            else:
                self.Hide()
        return

def NextGeneration(Bots, Generation, canvas, TL, prev_timelife=0):
    timelife = 0
    ClearCanvas(canvas)
    Resources = {}
    Positions = {}
    for i in range(Food_limit):
        Food(canvas, 1, Bot_size, Field_size)
    for i in range(Poison_limit):
        Food(canvas, 2, Bot_size, Field_size)
    i = 0
    DrawText(canvas, 150, C_H-70, 'Generation №' + str(Generation), Font_size, "white")
    DrawText(canvas, 150, C_H-50, 'Bots: ' + str(len(Bots)), Font_size, "white")
    DrawText(canvas, 150, C_H-30, 'Lifetime (prev, best): ' + str(TL[-1]) + ',' + str(max(TL)), Font_size, "white")
    
    while Alive(Bots)>Survivers:
        if Bots[i].dead == 0:
            Bots[i].RunDNA()
        canvas.update()
        timelife += 1
        i += 1
        if i > len(Bots)-1:
            i = 0
        if random.randint(0,Food_generation) == 0:
            Food(canvas, random.randint(1,2), Bot_size, Field_size)
        if sleep_time is not None:
            sleep(sleep_time)
    
    NewBots = []
    for k in Bots:
        if k.dead == 0:
            if timelife>max(TL):
                print('TL:, ', timelife, '[G:', Generation, '] DNA:',k.dna, 'E:', k.energy)
            for x in range(int(Bots_num/Survivers)):
                NewBots.append(Bot(random.randint(0, Field_size-1), random.randint(0, Field_size-1), k.dna, k.color, k.text_color, len(NewBots)-1, canvas))

    # Do Mutations
    for i in range(Mutation):
        rnd1 = random.randint(0, len(NewBots)-1)
        rnd2 = random.randint(0, DNA_lenght-1)
        NewBots[rnd1].color = 'yellow'
        NewBots[rnd1].text_color = 'black'
        for k in range(Mutation_dna):
            #print(rnd1, rnd2, NewBots[rnd1].dna)
            NewBots[rnd1].dna[rnd2] = random.randint(0, DNA_commands)
    TL.append(timelife)
    return NewBots

# Clear canvas 
def ClearCanvas(canvas):
    canvas.delete("all")
    # Draw field
    for i in range(Field_size):
        DrawLine(canvas, 0, i*Bot_size, Bot_size*Field_size, i*Bot_size, "#333333", 1)
        DrawLine(canvas, i*Bot_size, 0, i*Bot_size, Bot_size*Field_size, "#333333", 1)
    DrawRectangle(canvas, 0, 0, Bot_size*Field_size, Bot_size*Field_size, None, "white", "Field")
    
    Help_X = C_W - 100
    Help_Y = 20
    
    DrawRectangle(canvas, Help_X, Help_Y, Help_X + Bot_size, Help_Y + Bot_size, "blue", "blue")
    DrawText(canvas, Help_X + Bot_size/2, Help_Y + Bot_size/2, '99', Font_size, "white")
    DrawText(canvas, Help_X, Help_Y + 32, 'Helthy bot', Font_size, "white")
    
    DrawRectangle(canvas, Help_X, Help_Y + 60, Help_X + Bot_size, Help_Y + Bot_size + 60, "purple", "purple")
    DrawText(canvas, Help_X + Bot_size/2, Help_Y + Bot_size/2 + 60, '52', Font_size, "white")
    DrawText(canvas, Help_X, Help_Y + 90, 'CustomDNA bot', Font_size, "white")
    
    DrawRectangle(canvas, Help_X, Help_Y + 120, Help_X + Bot_size, Help_Y + Bot_size + 120, "pink", "pink")
    DrawText(canvas, Help_X + Bot_size/2, Help_Y + Bot_size/2 + 120, '36', Font_size, "black")
    DrawText(canvas, Help_X, Help_Y + 145, 'InLove bot', Font_size, "white")
    
    DrawRectangle(canvas, Help_X, Help_Y + 170, Help_X + Bot_size, Help_Y + Bot_size + 170, "yellow", "yellow")
    DrawText(canvas, Help_X + Bot_size/2, Help_Y + Bot_size/2 + 170, '36', Font_size, "black")
    DrawText(canvas, Help_X, Help_Y + 200, 'Mutated bot', Font_size, "white")

    DrawRectangle(canvas, Help_X, Help_Y + 170, Help_X + Bot_size, Help_Y + Bot_size + 170, "yellow", "yellow")
    DrawText(canvas, Help_X + Bot_size/2, Help_Y + Bot_size/2 + 170, '36', Font_size, "black")
    DrawText(canvas, Help_X, Help_Y + 200, 'Mutated bot', Font_size, "white")
    
    DrawCircle(canvas, Help_X, Help_Y + 360, Bot_size/2-3, "green", "green", 1)
    DrawText(canvas, Help_X, Help_Y + 375, 'Food, +10 energy', Font_size, "white")
    
    DrawCircle(canvas, Help_X, Help_Y + 420, Bot_size/2-3, "red", "red", 1)
    DrawText(canvas, Help_X, Help_Y + 435, 'Poison, -100 / +5 energy', Font_size, "white")


########### Run SIMULATION ################

# Setup values
Resources = {}
Positions = {}

# Graphics
Bot_size = 16
Field_size = 24
C_W = 640
C_H = 480
Font_size = 8

# World values
DNA_commands = 32
Food_limit = 100
Poison_limit = 0
Food_generation = 200
sleep_time = None
Bots_num = 8
DNA_lenght = 32
Survivers = 2
Mutation = 1
Love = True
Mutation_dna = 2

TL = [0]
master = Tk()
canvas_width = C_W
canvas_height = C_H
gg_canvas = Canvas(master, 
           width=canvas_width,
           height=canvas_height, bg = "black")
gg_canvas.pack()
Bots = []
for i in range(Bots_num):
    Bots.append(Bot(random.randint(0, Field_size-1), random.randint(0, Field_size-1), [random.randint(0, DNA_commands) for z in range(0,DNA_lenght)], 'blue', 'white', len(Bots)-1, gg_canvas))

#CustomDNA = [4, 21, 28, 5, 21, 30, 9, 31, 17, 4, 28, 24, 22, 26, 31, 20, 9, 28, 5, 28, 1, 1, 15, 21, 21, 16, 18, 16, 23, 22, 13, 25]
#Bots[-1] = Bot(random.randint(0, Field_size-1), random.randint(0, Field_size-1), CustomDNA, 'purple', 'white', len(Bots)-1, gg_canvas) 

for i in range(10000):
    Bots = NextGeneration(Bots, i, gg_canvas, TL)

mainloop()

# Show Graph of generations lifetime
root = Tk()
figure = Figure(figsize=(5, 4), dpi=100)
plot = figure.add_subplot(1, 1, 1)
plot.plot(TL, color="blue", marker="x", linestyle="")
canvas = FigureCanvasTkAgg(figure, root)
canvas.get_tk_widget().grid(row=0, column=0)
root.mainloop()
