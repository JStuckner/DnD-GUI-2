import json
import glob, os

def getMonsters():
    '''
    Reads the files in this folder and returns a dictionary of PCs
    '''
    file = r'D:\Anaconda3\Lib\site-packages\stuckpy\DnD\AppFiles\Json\beastiary.json'




    json_data=open(file).read()        
    Monsters = json.loads(json_data)



    #for key in Monsters["monster"]:
        #print(key["name"])



getMonsters()
