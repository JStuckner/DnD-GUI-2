import json
import glob, os

def getPCs():
    '''
    Reads the files in this folder and returns a dictionary of PCs
    '''
    path = os.path.dirname(__file__)
    print(path)

    PCs = {} #PC dictionary
    
    for file in glob.glob(path+"\\*.txt"):
        print(file)
        json_data=open(file).read()        
        PCs[file.split('\\')[-1][:-4]] = json.loads(json_data)
    return PCs


#getPCs()
