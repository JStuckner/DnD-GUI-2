#!/usr/bin/python

import tkinter as tk
from tab.tabula import rollTable, getTableNames, getTableGroups
from util import dice, randomMap, encounter
import random
from PIL import Image, ImageTk
from random import randint
import numpy as np
import matplotlib.pyplot as plt
from util.text import string_to_array
from scipy import ndimage, misc
from Characters.Character import getPCs
from util.getJson import getMonsters, getSpells
from util.getModifier import getMod
import re
import imageio
from skimage.transform import resize

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

class App(tk.Frame):

    def __init__(self, master=None):
      
        #Difficutly modifiers
        self.Diff = 2
        self.DiffThreshCR = 15
        

       

        # Character dictionaries.
        self.PCs = getPCs()
        for key in self.PCs:
            self.PCs[key]["hp"] = self.PCs[key]["maxHP"]


        # Monster dictionary
        self.monsters = getMonsters()
        self.characterList = []
        for key in self.PCs:
            self.characterList.append(self.PCs[key]["name"])
        for monster in self.monsters:
            self.characterList.append(monster["name"])

        # Spells
        self.spells = getSpells()
        self.spellList = []
        for key in self.spells:
            #print(key)
            self.spellList.append(key["name"])
        




        
        tk.Frame.__init__(self, master)
        self.pack()

        self.background = imageio.imread(r'maps\Elin.jpg')

        # Frame
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0)

        #Roll Table        
        groups = getTableGroups()
        tables = getTableNames(groups[0])

        self.groupvar = tk.StringVar(self)
        self.groupvar.set(groups[0])
        self.tablevar = tk.StringVar(self)
        self.tablevar.set(tables[0])
        self.txtTablevar = tk.StringVar(self)

        self.groupvar.trace('w', self.update_options)
        
        self.group = tk.OptionMenu(self.frame, self.groupvar, *groups)
        self.table = tk.OptionMenu(self.frame, self.tablevar, *tables)
        self.txtTable = tk.Entry(self.frame, width=6)
        self.butTable = tk.Button(self.frame,
                                  text="Roll on table",
                                  command=lambda:self.roll((self.groupvar.get(),self.tablevar.get(),self.txtTable.get())))


        self.group.grid(row=0, column=0)
        self.table.grid(row=0, column=1)
        self.txtTable.grid(row=0, column=2)
        self.butTable.grid(row=0, column=3)

##        #Roll Initiative
##        self.txtInit = tk.Entry(self.frame,width=25)
##        self.butInit = tk.Button(self.frame,
##                                 text="Roll for initiative",
##                                 command=lambda:self.rollInit())
##
##        self.txtInit.grid(row=2, column=0,columnspan=3, sticky='w')
##        self.butInit.grid(row=2, column=3)


        # Change Stat
        self.listPCVar = tk.StringVar(self)
        self.listPCVar.set(list(self.PCs.keys())[0])
        self.listStatVar = tk.StringVar(self)
        self.listStatVar.set(list(self.PCs[self.listPCVar.get()].keys())[0])
        self.listPCs = tk.OptionMenu(self.frame, self.listPCVar, *list(self.PCs.keys()), command = lambda x:self.updateStats(PClist=True))
        self.listStats = tk.OptionMenu(self.frame, self.listStatVar, *list(self.PCs[self.listPCVar.get()].keys()), command = lambda x:self.updateStats(PClist=False))
        self.lblStatVar = tk.StringVar(self)
        self.txtStat = tk.Entry(self.frame, textvariable=self.lblStatVar, width=10)
        self.butChangeStat = tk.Button(self.frame, text="Change Stat", command=lambda:self.changeStat())

        self.listPCs.grid(row=2,column=0)
        self.listStats.grid(row=2,column=1)
        self.txtStat.grid(row=2,column=2)
        self.butChangeStat.grid(row=2, column=3)

        self.updateStats(False)
    
        #Create Map
        self.mapframe=tk.Frame(self.frame)
        self.mapframe.grid(row=1, column=0, columnspan=3)
        self.txtXSize = tk.Entry(self.mapframe,width=4)
        self.txtYSize = tk.Entry(self.mapframe,width=4)
        self.txtXLoc = tk.Entry(self.mapframe,width=4)
        self.txtYLoc = tk.Entry(self.mapframe,width=4)
        
        self.butMap = tk.Button(self.frame,
                                text="Create map",
                                command=lambda:self.createMap())

        self.txtXSize.grid(row=1, column=0)
        self.txtYSize.grid(row=1, column=1)
        self.txtXLoc.grid(row=1, column=2)
        self.txtYLoc.grid(row=1, column=3)
        self.butMap.grid(row=1, column=3)

##        #Random Zombie
##        self.butZombie = tk.Button(self,
##                                   text="Spawn Zombies",
##                                   command=lambda:self.spawnZombie())
##        self.butZombie.grid(row=4, column=0)

        #Active Perception
        self.butPerceive = tk.Button(self.frame,
                                   text="Perception",
                                   command=lambda:self.perceive())
        self.butPerceive.grid(row=4, column=3)

        # Check carry weight
        self.butWeight = tk.Button(self.frame,
                                   text="Check weight",
                                   command=lambda:self.checkWeight())
        self.butWeight.grid(row=4, column=1)

        # Fight
        self.butFight = tk.Button(self.frame,
                                   text="Fight",
                                   command=lambda:self.setupFight())
        self.butFight.grid(row=4, column=0)

        # Rest
        self.butRest = tk.Button(self.frame,
                                   text="Rest",
                                   command=lambda:self.rest())
        self.butRest.grid(row=4, column=2)

        

        # Map picture
        self.mapIm = [] #store the image
        self.canvasMap = tk.Canvas(self, height=800, width=800)
        self.canvasMap.grid(row=0, column=4, columnspan=10, rowspan=30)

        # Map List
        self.txtMap = tk.Text(self, height=40, width=30)
        self.txtMap.grid(row=0, column=14, rowspan=30, columnspan=3)

        # Map arrows
        self.aFrame = tk.Frame(self)
        self.aFrame.grid(row=3,column=0)
        self.upButton = tk.Button(self.aFrame,
                                  text='^',
                                  command=lambda:self.createMap('up'))
        self.downButton = tk.Button(self.aFrame,
                                  text='v',
                                  command=lambda:self.createMap('down'))
        self.leftButton = tk.Button(self.aFrame,
                                  text='<',
                                  command=lambda:self.createMap('left'))
        self.rightButton = tk.Button(self.aFrame,
                                  text='>',
                                  command=lambda:self.createMap('right'))
        self.inButton = tk.Button(self.aFrame,
                                  text='+',
                                  command=lambda:self.createMap('in'))
        self.outButton = tk.Button(self.aFrame,
                                  text='-',
                                  command=lambda:self.createMap('out'))
        self.upButton.grid(row=0, column = 1)
        self.downButton.grid(row=2, column = 1)
        self.leftButton.grid(row=1, column = 0)
        self.rightButton.grid(row=1, column = 2)
        self.inButton.grid(row=0, column = 4)
        self.outButton.grid(row=2, column = 4)

        # Print text box
        self.txtPrint = tk.Text(self,height=35, width=50)
        self.txtPrint.grid(row=4, column=0, rowspan=20, columnspan=4)

    def updateStats(self, PClist):
            
##        if PClist:
##            self.listStats['menu'].delete(0, tk.END)
##            for i, stat in enumerate(list(self.PCs[self.listPCVar.get()].keys())):
##                self.listStats['menu'].add_command(label=stat, command=tk._setit(self.listStatVar, stat))
##                #self.listStatVar.set(list(self.PCs[self.listPCVar.get()].keys())[0])

        if PClist:
            self.listStats = tk.OptionMenu(self.frame, self.listStatVar, *list(self.PCs[self.listPCVar.get()].keys()), command = lambda x:self.updateStats(PClist=False))
            self.listStatVar.set(list(self.PCs[self.listPCVar.get()].keys())[0])
            self.listStats.grid(row=2,column=1)

            
        self.lblStatVar.set(self.PCs[self.listPCVar.get()][self.listStatVar.get()])
        tempInsert = str(self.lblStatVar.get())
        self.txtStat.delete(0,100)
        self.txtStat.insert(0, tempInsert)

    def changeStat(self):
        self.PCs[self.listPCVar.get()][self.listStatVar.get()] = self.lblStatVar.get()

    def rest(self):
        for PC in self.PCs:
            self.PCs[PC]['hp'] = self.PCs[PC]['maxHP']

    def roll(self, argv):
        output = rollTable(argv, retString=True)

        # Find the total gold value of the treasure.
        
        if argv[0] == 'treasure':
            total = 0
            flagMult = 1
            interp = re.sub(',','',output) #Delete commas
            interp = re.sub("\)",'',interp)
            interp = re.sub("\(",'',interp)
            interp = interp.split()
            for i, word in enumerate(interp):
                # Flag '2x' or 'ix' to multiply next gold value
                if word[-1] == 'x':
                    try:
                        flagMult = int(word[:-1])
                        
                    except:
                        pass                       
                        
                if word == 'cp':
                    total += flagMult*int(interp[i-1])/100
                    flagMult = 1
                if word == 'sp':
                    total += flagMult*int(interp[i-1])/10
                    flagMult = 1
                if word == 'gp':
                    total += flagMult*int(interp[i-1])
                    flagMult = 1
                if word == 'pp':
                    total += flagMult*int(interp[i-1])*10
                    flagMult = 1
                    
            output += ' TOTAL GOLD VALUE: ' + str(total) + '(' + str(total/4) + ').\n' 
            
        self.write(output)


    def write(self, *strings, sep=' ', end='\n'):
        output = ''
        for i in range(len(strings)):            
            output = output+str(strings[i])+sep
        output = output + end         
            
            
        self.txtPrint.insert(tk.END,output)
        self.txtPrint.see(tk.END)

    def checkWeight(self):
        from stuckpy.DnD.inventory import checkWeight
        self.write('Encumberance Check')
        names = ('Anastasia', 'Cameron', 'Travis', 'Seth', 'Keith',
                 'Bag of Holding', 'Tensors Floating Disk', 'Keith Donkey')
        strength = (self.PCs['Geralda']["str"],
                    self.PCs['Zana']["str"],
                    self.PCs['Traubon']["str"],
                    self.PCs['Saleek']["str"],
                    self.PCs['Varis']["str"],
                    0, 0, 10)
        bonus = (self.PCs['Geralda']["bonuscarry"],
                 self.PCs['Zana']["bonuscarry"],
                 self.PCs['Traubon']["bonuscarry"],
                 self.PCs['Saleek']["bonuscarry"],
                 self.PCs['Varis']["bonuscarry"],
                 500, 500, 0)
        light = []
        heavy = []
        maximum = []
        
        for i in range(len(strength)):
            light.append(strength[i]*5+bonus[i])
            heavy.append(strength[i]*10+bonus[i])
            maximum.append(strength[i]*15+bonus[i])
            carry = checkWeight(names[i])
            self.write('{0} is carrying {1}/{2} lbs.'.format(names[i],carry,maximum[i]))
            if carry > maximum[i]:
                self.write('{0} is overencumbered and must immediately carry less'.format(names[i]))
            elif carry > heavy[i]:
                self.write('{0} is heavily encumbered.  Minus 20 movespeed and disadvantage on all ability checks, attack rolls, and saving throws that use Strenght, Dexterity, or Constitution'.format(names[i]))                           
            elif carry > light[i]:
                self.write('{0} is lightly encumbered.  Minus 10 movespeed.'.format(names[i]))
            else:
                self.write('{0} is not encumbered.'.format(names[i]))
            self.write('')
                           
      

    def perceive(self):
        seth = random.randint(1,20) + 6
        ana = random.randint(1,20) + 1
        cam = random.randint(1,20) + 4
        trav = max(random.randint(1,20),random.randint(1,20)) + 6
        self.write('Rolling for perception:')
        self.write('Seth        =',seth)
        self.write('Anastasia   =',ana)
        self.write('Travis      =',trav)
        self.write('Cameron     =',cam)
        self.write('')

    def update_options(self, *args):
        tables = getTableNames(self.groupvar.get())
        menu = self.table['menu']
        menu.delete(0,'end')
        for i in tables:
            menu.add_command(label=i, command=lambda val=i:self.tablevar.set(val))
        self.tablevar.set(tables[0])

    def rollInit(self, Return=False):
        params = self.txtInit.get()
        params = params.split()
        intparams = []
        for i in params:
            try:
                intparams.append(int(i))
            except:
                pass

        if Return:
            return(encounter.order(intparams))
        else:
            self.write('Rolling for initiative...')
            self.write(encounter.order(intparams))
            self.write('')

    def createMap(self, direction='none'):
        # Kill 0s
        if direction != 'none':
            if self.txtXLoc.get() == '':
                self.txtXLoc.insert(0,'20')
            if self.txtYLoc.get() == '':
                self.txtYLoc.insert(0,'20')
            if self.txtXSize.get() == '':
                self.txtXSize.insert(0,'15')
            if self.txtYSize.get() == '':
                self.txtYSize.insert(0,'15')

        if direction == 'up':
            new = int(self.txtXLoc.get())-1
            self.txtXLoc.delete(0,10)            
            self.txtXLoc.insert(0,str(new))

        if direction == 'down':
            new = int(self.txtXLoc.get())+1
            self.txtXLoc.delete(0,10)            
            self.txtXLoc.insert(0,str(new))

        if direction == 'left':
            new = int(self.txtYLoc.get())-1
            self.txtYLoc.delete(0,10)            
            self.txtYLoc.insert(0,str(new))

        if direction == 'right':
            new = int(self.txtYLoc.get())+1
            self.txtYLoc.delete(0,10)            
            self.txtYLoc.insert(0,str(new))

        if direction == 'in':
            new = int(self.txtXSize.get())-1
            self.txtXSize.delete(0,10)            
            self.txtXSize.insert(0,str(new))
            new = int(self.txtYSize.get())-1
            self.txtYSize.delete(0,10)            
            self.txtYSize.insert(0,str(new))
            
        if direction == 'out':
            new = int(self.txtXSize.get())+1
            self.txtXSize.delete(0,10)            
            self.txtXSize.insert(0,str(new))
            new = int(self.txtYSize.get())+1
            self.txtYSize.delete(0,10)            
            self.txtYSize.insert(0,str(new))

        
        try:
            x = int(self.txtXSize.get())
        except ValueError:
            x = 15
        try:
            y = int(self.txtYSize.get())
        except ValueError:
            y = 15
        try:
            xloc = int(self.txtXLoc.get())
        except ValueError:
            xloc = 20
        try:
            yloc = int(self.txtYLoc.get())
        except ValueError:
            yloc = 20
        try:
            items = int(self.txtTable.get())
        except ValueError:
            items = dice.parse(self.txtTable.get())

        rolls = rollTable(('map',
                          'Map',
                          self.txtTable.get()),
                          retString=True,
                          retList=True)
        
        self.txtMap.delete(1.0, tk.END) # clear box
        self.txtMap.insert(tk.END,"Map Items:")
        for i in range(len(rolls)):
            if i < 9:
                self.txtMap.insert(tk.END,'\n ' + str(i+1) + ' = ' + str(rolls[i]))
            else:
                self.txtMap.insert(tk.END,'\n'+ str(i+1)+' = '+str(rolls[i]))
        #print('')

        Map = self.create(x,y,items,xloc,yloc, get=True)
        #Map = resize(Map,(int(750/Map.shape[0]), int(750/Map.shape[1])))
        self.mapIm = ImageTk.PhotoImage(Image.fromarray(np.uint8(Map*255)))

        #mapx, mapy = self.mapIm.shape

        self.canvasMap.config(width=self.mapIm.width(), height=self.mapIm.height())
        self.canvasMap.create_image(0,0,image=self.mapIm, anchor='nw')
        self.update_idletasks()




    def setupFight(self, newFight=True):
        self.top = tk.Toplevel(self)

        if not newFight:
            self.Ftop.destroy()

        # Create Widgets
        checkVar = tk.IntVar()        
        self.search_var = tk.StringVar()
        self.listnumber_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.updateList())
        self.entry = tk.Entry(self.top, textvariable=self.search_var, width=13)
        self.listFrom = tk.Listbox(self.top, width=45, height=15)
        self.scrollbar = tk.Scrollbar(self.top, orient=tk.VERTICAL)
        self.listTo = tk.Listbox(self.top, width=45, height=15, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listTo.yview)

        self.butSetupIn = tk.Button(self.top, text="Add ->", command=lambda:self.addList())
        self.butSetupOut = tk.Button(self.top, text="<- Remove", command=lambda:self.removeList())
        self.butSetupFight = tk.Button(self.top, text="Fight!", command=lambda:self.goFight(newFight, checkVar.get()))
        self.txtSetupNum = tk.Entry(self.top, width=3, textvariable=self.listnumber_var)


        self.checkAdjDiff = tk.Checkbutton(self.top,
                                           text ="Adjust Difficulty?",
                                           variable = checkVar,
                                           onvalue=1,
                                           offvalue=0,
                                           height=5, width=20)
        
        
        # Pack Widgets
        self.entry.grid(row=0, column=0, padx=10, pady=3)
        self.listFrom.grid(row=1, column=0, padx=10, pady=3, rowspan=10)
        self.listTo.grid(row=1, column=2, padx=0,pady=3, rowspan=10)
        self.scrollbar.grid(row=1, column=3, rowspan=10, sticky=tk.N+tk.S+tk.W)
        self.txtSetupNum.grid(row=3, column=1, padx=5, pady=2)
        self.butSetupIn.grid(row=4, column=1, padx=5, pady=2)
        self.butSetupOut.grid(row=5, column=1, padx=5, pady=2)
        self.butSetupFight.grid(row=7,column=1, padx=5, pady=20)
        self.checkAdjDiff.grid(row=8, column=1)

        # Call to poplulate initial lists
        
        self.updateList()
        
        if newFight:
            self.startToList()

    def goFight(self, newFight=True, adjDiff=True):

        if newFight:
            self.fighters = []
            self.order = []
            
        for item in self.listTo.get(0,tk.END):
            for PC in self.PCs:
                if item.lower() == self.PCs[PC]["name"].lower():
                    self.fighters.append(self.PCs[PC])
            for monster in self.monsters:
                if item.lower() == monster["name"].lower():
                    #print(type(monster))
                    self.fighters.append(monster.copy())

                    # Apply difficulty modifiers
                    cr = self.fighters[-1]["cr"]
                    try:
                        cr = int(cr)
                    except ValueError:
                        cr = int(1) #actually equals less than 1 but this is temporary
                    if " " in self.fighters[-1]["hp"]:
                        self.fighters[-1]["hp"] = self.fighters[-1]["hp"].split()[0]
                    if " " in self.fighters[-1]["ac"]:
                        self.fighters[-1]["ac"] = self.fighters[-1]["ac"].split()[0]
                    self.fighters[-1]["hp"] = int(self.fighters[-1]["hp"])
                    self.fighters[-1]["ac"] = int(self.fighters[-1]["ac"])

                    if cr < self.DiffThreshCR and adjDiff:
                        self.fighters[-1]["hp"] = int(self.fighters[-1]["hp"] + self.fighters[-1]["hp"]*self.Diff*5/100)
                        self.fighters[-1]["ac"] = self.fighters[-1]["ac"] + self.Diff
                    
                    
            
        self.top.destroy()
        self.fight(newFight)



    def startToList(self):
        for PC in self.PCs:
            self.listTo.insert(tk.END, self.PCs[PC]["name"])
        #self.listTo.insert(tk.END, "Keith Polar Bear")

    def updateList(self):
        search_term = self.search_var.get()
        self.listFrom.delete(0,tk.END)

        if 'cr=' in search_term.lower():
            crList = []
            cr = search_term.lower().split('cr=')[1]
            
            search_term= ''
            for monster in self.monsters:
                if monster['cr'] == cr:
                    crList.append(monster["name"])
            for item in crList:
                if search_term.lower() in item.lower():
                    self.listFrom.insert(tk.END, item)        

        else:
            for item in self.characterList:
                if search_term.lower() in item.lower():
                    self.listFrom.insert(tk.END, item)
        
    def addList(self):
        toAdd = self.listFrom.get(self.listFrom.curselection())
        numAdd = 1
        try:
            numAdd = int(self.listnumber_var.get())
        except:
            pass

        for i in range(numAdd):
            self.listTo.insert(tk.END, toAdd)

    def removeList(self):
        removes = self.listTo.curselection()
        for i in range(len(removes)):
            self.listTo.delete(removes[i]-i)
            

    def fight(self, newFight=True):

        self.Ftop = tk.Toplevel(self)
        numPrevFighters = len(self.order)


        # get initiative
        if numPrevFighters == 0:
            self.order = np.zeros(len(self.fighters),
                             dtype=[('index', (int)),('roll', (int))])
        else:    
            for i in range(len(self.fighters)-numPrevFighters):

                neworder = np.zeros(1, dtype=[('index', (int)),('roll', (int))])
                self.order = np.concatenate((self.order, neworder))




            

        
        for idx, fighter in enumerate(self.fighters):
            if idx >= numPrevFighters:
                self.order['index'][idx]=idx
                try:
                    if 'initadv' in fighter and fighter['initadv'] == 1:
                        self.order['roll'][idx] = int(fighter['init']) + max(randint(1,20),randint(1,20))
                    else:
                        self.order['roll'][idx] = int(fighter['init']) + randint(1,20)
                except KeyError:
                    if 'initadv' in fighter and fighter['initadv'] == 1:
                        self.order['roll'][idx] = getMod(int(fighter['dex'])) + max(randint(1,20),randint(1,20))
                    else:
                        self.order['roll'][idx] = getMod(int(fighter['dex'])) + randint(1,20)

        # Sort Initiative
        np.random.shuffle(self.order)
        self.order['roll'] = -self.order['roll']
        self.order.sort(order='roll')
        self.order['roll'] = -self.order['roll']

        print(self.order['roll'])

        
        startCol = 2
        txtHP = []
        lblName = []
        lblAC = []
        butHit = []
        butInfo = []
        HP = []
        tag = []
        txtTag = []
        fighterFrame = tk.Frame(self.Ftop)
        lblHeading = []
        headings = ['Name','Tag','AC','HP','Hit', 'Info']

        lblDamage = tk.Label(self.Ftop, text='Damage:')
        txtDamage = tk.Entry(self.Ftop, width=4)
        lblDamage.grid(row=0, column=0, sticky=tk.E)
        txtDamage.grid(row=0, column=1)

        self.txtInfo = tk.Text(self.Ftop, height=40, width=80)
        self.txtInfo.grid(row=0, column=4, rowspan=10)



        for i, heading in enumerate(headings):
            lblHeading.append(tk.Label(fighterFrame, text = heading))
            lblHeading[i].grid(row=0,column=i)
                     
        
        for i, idx in enumerate(self.order['index']):

            # Remove extra info in monster manual
            if ' ' in str(self.fighters[idx]['ac']):
                self.fighters[idx]['ac'] = str(self.fighters[idx]['ac']).split()[0]
            if ' ' in str(self.fighters[idx]['hp']):
                self.fighters[idx]['hp'] = str(self.fighters[idx]['hp']).split()[0]            


            
            lblName.append(tk.Label(fighterFrame, text=self.fighters[idx]['name']))
            lblAC.append(tk.Label(fighterFrame, text=self.fighters[idx]['ac'], width=5))
            tag.append(tk.StringVar())
            txtTag.append(tk.Entry(fighterFrame, textvariable=tag[i], width=10, text=''))
            HP.append(tk.StringVar())
            HP[i].set(self.fighters[idx]['hp'])
            txtHP.append(tk.Entry(fighterFrame, textvariable=HP[i], width=4))
            butHit.append(tk.Button(fighterFrame, text='Hit',command=lambda x=txtHP[i], y=idx:self.hit(int(txtDamage.get()),x, y)))
            butInfo.append(tk.Button(fighterFrame, text='Info',command=lambda x = self.fighters[idx]:self.getInfo(x)))
            lblName[i].grid(row=i+1, column=0)
            txtHP[i].grid(row=i+1, column=3)
            butHit[i].grid(row=i+1, column=4)
            txtTag[i].grid(row=i+1, column=1)
            lblAC[i].grid(row=i+1, column = 2)
            butInfo[i].grid(row=i+1, column=5)
                           
                           
                                     
        # Set tab order
        for widget in txtTag + txtHP:
            widget.lift()                      


        fighterFrame.grid(row=0, column=startCol)

        # Spell list
        self.spellSearch_var = tk.StringVar()
        self.spellSearch_var.trace("w", lambda name, index, mode: self.updateSpellList())
        self.spellEntry = tk.Entry(self.Ftop, textvariable=self.spellSearch_var, width=13)
        self.listSpells = tk.Listbox(self.Ftop, width=45, height=15)
        self.spellInfo = tk.Button(self.Ftop, text="Info", command=lambda: self.getSpellInfo())
        self.spellEntry.grid(row=2, column=2)
        self.listSpells.grid(row=3, column=2)
        self.spellInfo.grid(row=4, column=2)
        self.updateSpellList()

        # Add fighter
        self.butAdd = tk.Button(self.Ftop, text="Add Fighter", command=lambda: self.setupFight(newFight=False))
        self.butAdd.grid(row=0, column=3)

        # Roll
        self.txtFRollVar = tk.StringVar()
        self.txtFRoll = tk.Entry(self.Ftop, width=10, textvariable=self.txtFRollVar)
        self.lblFRoll = tk.Label(self.Ftop, )        
        self.butFRoll = tk.Button(self.Ftop, text="Roll", command=lambda: self.FRoll())

        

        self.txtFRoll.grid(row=5, column=1)
        self.butFRoll.grid(row=5, column=2)
        self.lblFRoll.grid(row=5, column=3)



    def FRoll(self):
       roll = dice.parse(self.txtFRollVar.get())
       self.lblFRoll['text'] = roll
       

    def hit(self, damage, textBox, idx):
        self.fighters[idx]['hp'] = int(self.fighters[idx]['hp']) - damage
        textBox.delete(0,tk.END)
        textBox.insert(0,str(self.fighters[idx]['hp']))
        try:
            self.PCs[self.fighers[idx]["name"]]['hp'] = self.fighters[idx]['hp']
        except:
            pass
            #print('line 509 isn\'t right')


        
    def updateSpellList(self):
        search_term = self.spellSearch_var.get()
        self.listSpells.delete(0,tk.END)

        for item in self.spellList:
            if search_term.lower() in item.lower():
                self.listSpells.insert(tk.END, item)
                
    def getSpellInfo(self):
        idx = self.listSpells.curselection()
        selection = self.listSpells.get(idx,idx)[0]

        for key in self.spells:
            if key['name'] == selection:
                s = key

        t = self.txtInfo
        t.delete('0.0',tk.END)            
        t.insert('1.1', '\n\n\n\n\n\n\n\n\n\n')
        
        t.insert('1.1', 'Name: ')
        t.insert('1.7', s['name'])    
        t.insert('2.1', 'Level: ')
        t.insert('2.8', s['level'])
        t.insert('3.1', 'Classes: ')
        t.insert('3.10', s['classes'])
        t.insert('4.1', 'School: ')
        t.insert('4.9', s['school']) 
        t.insert('5.1', 'Range: ')
        t.insert('5.8', s['range'])    
        t.insert('6.1', 'Components: ')
        t.insert('6.13', s['components']) 
        t.insert('7.1', 'Duration: ')
        t.insert('7.11', s['duration'])
        t.insert('8.1', 'Roll: ')
        t.insert('8.7', s.get('roll', 'N/A'))
        t.insert('9.1', 'Cast time: ')
        t.insert('9.11', s.get('time'))
        
        if type(s["text"]) is str:
           t.insert(tk.END, s["text"])
           t.insert(tk.END, '\n')
        else:
           for text in s["text"]:
               t.insert(tk.END, text)
               t.insert(tk.END, '\n')
        
                                                        
    def getInfo(self,f):


            
        t = self.txtInfo
        t.delete('0.0',tk.END)
        t.insert('1.1', '\n\n\n\n\n\n\n\n')
        
        t.insert('1.1', 'Name: ')
        t.insert('1.7', f['name'])
        t.insert('2.1', 'Ac: ')
        t.insert('2.7', f['ac'])
        t.insert('3.1', 'HP: ')
        t.insert('3.7', f['hp'])

        t.insert('5.1', '  Str    Dex    Con    Int    Wis    Cha ')
        Str = str(f['str'])+'('+str(getMod(int(f['str'])))+')      '
        t.insert('6.1',Str)
        dex = str(f['dex'])+'('+str(getMod(int(f['dex'])))+')     '
        t.insert('6.8',dex)
        con = str(f['con'])+'('+str(getMod(int(f['con'])))+')     '
        t.insert('6.15',con)
        Int = str(f['int'])+'('+str(getMod(int(f['int'])))+')     '
        t.insert('6.22',Int)
        wis = str(f['wis'])+'('+str(getMod(int(f['wis'])))+')     '
        t.insert('6.29',wis)
        cha = str(f['cha'])+'('+str(getMod(int(f['cha'])))+')     '
        t.insert('6.36',cha)

        stats = ['cr', 'type', 'alignment', 'speed', 'save', 'skill', 'senses',
                'passive', 'languages', 'immune', 'resist', 'vulnerable',
                 'bonuscarry', 'spellDC',
                 'maxHP','init']
        for stat in stats:
            if f.get(stat) is not None:
                t.insert(tk.END, stat.title())
                t.insert(tk.END, ': ')
                t.insert(tk.END, f[stat])
                t.insert(tk.END, '\n')

        if f.get('trait') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Traits:')
            for i in range(len(f['trait'])):
                try:
                    if f['trait'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['trait'][i]['name'])
                    if f['trait'][i].get('trait') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['trait'][i]['attack'])
                    if f['trait'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['trait'][i]['text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['trait'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['trait']['name'])
                    if f['trait'].get('trait') is not None:
                        t.insert(tk.END, '\n  attack:')
                        
                        t.insert(tk.END, f['trait']['attack'])
                    if f['trait'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['trait']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop.

                    
        if f.get('action') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Actions:')
            for i in range(len(f['action'])):
                try:
                    if f['action'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['action'][i]['name'])
                    if f['action'][i].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['action'][i]['attack'])
                    if f['action'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['action'][i]['text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['action'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['action']['name'])
                    if f['action'].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['action']['attack'])
                    if f['action'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['action']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop.

            
        if f.get('legendary') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Legendary:')
            for i in range(len(f['legendary'])):
                try:
                    if f['legendary'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['legendary'][i]['name'])
                    if f['legendary'][i].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['legendary'][i]['attack'])
                    if f['legendary'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['legendary'][i]['text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['legendary'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['legendary']['name'])
                    if f['legendary'].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['legendary']['attack'])
                    if f['legendary'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['legendary']['text'])                
                    t.insert(tk.END, '\n')                
                    break #Stupid way to exit loop. 


                          
                                    
                                    

    def create(self, xsize,ysize,items,xloc=0,yloc=0,get=False):

        pix = 50 #pixels per unit

        back_unit_width = 68
        back_unit_height = 60
        #background = resize(background,(back_unit_height*pix*6,back_unit_width*pix*6))

        xmin = int(xloc*100)
        xmax = int((xloc+xsize/6)*100)
        ymin = int(yloc*100)
        ymax = int((yloc+ysize/6)*100)

        zoom = self.background[xmin:xmax, ymin:ymax, :]
        zoom = resize(zoom, (xsize*50, ysize*50))
                  


 

        for i in range(ysize):
            zoom[:,pix*i,:] = 0

        for i in range(xsize):
            zoom[pix*i,:,:] = 0

        print(items)
        for i in range(items):
            xloc = randint(0,xsize-1)
            yloc = randint(0,ysize-1)
            num = string_to_array(str(i+1), height=20, color=255)
            num = 255 - num #invert 1s and 0s.
            if i < 9:
                y = yloc*pix+10
            else:
                y = yloc*pix+1
            x = xloc*pix+10
            xl,yl = num.shape
            num = np.uint8(num*255)
            zoom[x:x+xl,y:y+yl,0] = num
            zoom[x:x+xl,y:y+yl,1] = num
            zoom[x:x+xl,y:y+yl,2] = num


        if not get:
            plt.imshow(zoom)
            plt.show()

        if get:
            return zoom
            
            
            
myapp = App()
myapp.master.title('DnD GUI')
myapp.mainloop()
