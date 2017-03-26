# Interface to CitySim Solver
# http://citysim.epfl.ch/
#
# GH-Python component initiated by
# Giuseppe Peronato <giuseppe.peronato@epfl.ch> 
# 

"""
This component loads the Citysim ouput into Grasshopper.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        path: Directory
        name: name of the project
        yearly: Loads yearly results (default = False)
        geometry: same geometry used as simulation input
        type: choose between SW or DC (default = SW)
        Run: set Boolean to True to load the results
    Returns:
        results: SW radiation
"""

ghenv.Component.Name = "Honeybee_CitySim-LoadSolar"
ghenv.Component.NickName = 'CitySim-LoadSolar'
ghenv.Component.Message = 'VER 0.0.1\nJAN_17_2017'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import uuid

#Default values
type = "SW"
yearly = False

#Get surfaces from Honeybee zones
# written by Giulio Piacentino, giulio@mcneel.com
def tree_to_list(input, retrieve_base = lambda x: x[0]):
    """Returns a list representation of a Grasshopper DataTree"""
    def extend_at(path, index, simple_input, rest_list):
        target = path[index]
        if len(rest_list) <= target: rest_list.extend([None]*(target-len(rest_list)+1))
        if index == path.Length - 1:
            rest_list[target] = list(simple_input)
        else:
            if rest_list[target] is None: rest_list[target] = []
            extend_at(path, index+1, simple_input, rest_list[target])
    all = []
    for i in range(input.BranchCount):
        path = input.Path(i)
        extend_at(path, 0, input.Branch(path), all)
    return retrieve_base(all)
    
geometry = tree_to_list(geometry, lambda x: x)





def list_to_tree(input, none_and_holes=True, source=[0]):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""
    # written by Giulio Piacentino, giulio@mcneel.com
    from Grasshopper import DataTree as Tree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from System import Array
    def proc(input,tree,track):
        path = Path(Array[int](track))
        if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
        for i,item in enumerate(input):
            if hasattr(item, '__iter__'): #if list or tuple
                track.append(i); proc(item,tree,track); track.pop()
            else:
                if none_and_holes: tree.Insert(item,path,i)
                elif item is not None: tree.Add(item,path)
    if input is not None: t=Tree[object]();proc(input,t,source[:]);return t
    
    
def loadOut(path,name,type="SW",yearly=True):
    #Load SW output file
    if yearly:
        ending = "_yearly.out"
    else:
        ending = ".out"
    in_file = open(path+name+"_"+type+ending,"r")
    txt = in_file.read()
    in_file.close()
    results = txt.splitlines()
    header = results[0]
    results.pop(0) #remove header
    return header, results

def parseHead(head):        
    #Parse header
    import re
    header = head.split()
    #header.pop(0)
    bIDs = []
    sIDs = []
    for i in range(len(header)):
        if i == 0:
            bIDs.append('')
            sIDs.append('')
        else:
            b = header[i].split('(')
            s = re.search('(?<=:)\w+', header[i])
            b = b[0]
            s = s.group(0)
            #print 'building', b, 'surface', s
            bIDs.append(b)
            sIDs.append(int(s))
    return bIDs, sIDs

def parseRes(results,sIDs):
    #Parse results
    irrH = []

    for l in results: #for each line corresponding to a hour
        bldg = []
        isrf = []
        for i in l.split(): #split the surfaces
            isrf.append(float(i))
        irrH.append(isrf)
    #print len(isrf)
    irrS = []
    for s in xrange(len(sIDs)): #for each surface
        srf = []
        for h in range(len(irrH)): #for each hour
            srf.append(irrH[h][s])
        irrS.append(srf)
    return irrS

def removeTerr(irrS,bIDs,sIDs):   
    #Remove terrain from results 
    bIDs2 = []
    sIDs2 = []
    IDs = []
    irrS2 = []
    for s in xrange(len(bIDs)):
        if bIDs[s] != "NA" and bIDs[s] != "" : #remove columns
            sIDs2.append(int(sIDs[s]))
            bIDs2.append(int(bIDs[s]))
            IDs.append([int(bIDs[s]),int(sIDs[s])])
            irrS2.append(irrS[s])
    return irrS2, bIDs2, sIDs2


if Run:
    header, results = loadOut(path,name,type,yearly)
    bIDs, sIDs = parseHead(header)
    irrS = parseRes(results,sIDs)
    irrS2, bIDs2, sIDs2 = removeTerr(irrS,bIDs,sIDs)
    
    
    #Create a dictionary from the output file
    diction = {}
    for i in xrange(len(bIDs2)):
        diction[str(bIDs2[i])+"-"+str(sIDs2[i])]= irrS2[i]
        
    #Create lists of IDs from geometry data tree
    bIDs3 = []
    sIDs3 = []
    for b in xrange(len(geometry)):
        for s in xrange(len(geometry[b])):
            bldgid, srfid = b, s, 
            bIDs3.append(int(bldgid))
            sIDs3.append(int(srfid))
    bIDs3set = list(set(bIDs3)) #create a set of unique building IDs from geometry data tree
    
    #Iterate over the geometry IDs
    output = []
    for b in bIDs3set:
        bldg = []
        for s in xrange(len(sIDs3)):
            if bIDs3[s] == b:
                #print b, sIDs2[s]
                #print str(b)+'-'+str(sIDs3[s])
                bldg.append(diction.get(str(b)+'-'+str(sIDs3[s]),[-1])) #if the key is valid retun list of hourly values, otherwise empty list
        output.append(bldg)

    results = list_to_tree(output,none_and_holes=True, source=[])