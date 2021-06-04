import json
import glob, os

def getMonsters():
    '''
    Reads the files in this folder and returns a dictionary of PCs
    '''
    dirname = os.path.dirname(__file__)
    file = os.path.join(dirname, 'AppFiles/Json/beastiary.json')

    json_data=open(file).read()        
    Monsters = json.loads(json_data)

    dirname = os.path.dirname(__file__)
    file = os.path.join(dirname, 'AppFiles/Json/myMonsters.json')



    json_data=open(file).read()
    myMonsters = json.loads(json_data)
    for monster in myMonsters['monster']:
        Monsters['monster'].append(monster)


    return Monsters["monster"]


def getSpells():
    dirname = os.path.dirname(__file__)
    file = os.path.join(dirname, 'AppFiles/Json/spells.json')
    json_data=open(file).read()        
    spells = json.loads(json_data)

    return spells["spell"]

#getMonsters()
