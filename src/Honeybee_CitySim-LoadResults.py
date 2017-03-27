# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
#  All rights reserved. Ecole polytechnique fdrale de Lausanne (EPFL), Switzerland,
# Interdisciplinary Laboratory of Performance-Integrated Design (LIPID), 2016-2017
# Author: Giuseppe Peronato, <giuseppe.peronato@epfl.ch
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/
#
# This component relies on Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

"""
This component loads the Citysim ouput into Grasshopper.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        path: Directory
        paths: List of Paths of the DataTree
        name: name of the project
        Run: set Boolean to True to load the results
    Returns:
        SW: Shortwave irradiation {Building;Surface}
        H: Heating needs {Building}
        C: Cooling needs {Building}
        Geometry: Curves of input geometry {Building;Surface}
"""

ghenv.Component.Name = "Honeybee_CitySim-LoadResults"
ghenv.Component.NickName = 'CitySim-LoadResults'
ghenv.Component.Message = 'VER 0.1.2\nMAR_24_2017'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import uuid

hb_hive = sc.sticky["honeybee_Hive"]()

geometry = []


HBO = hb_hive.callFromHoneybeeHive(_HBZones)
for b in HBO:
    crvs = []
    HBSurfaces  = hb_hive.addToHoneybeeHive(b.surfaces, ghenv.Component.InstanceGuid.ToString() + str(uuid.uuid4()))
    for s in HBSurfaces:
        edges = rs.DuplicateEdgeCurves(s)
        crvs.append(rs.JoinCurves(edges))
    geometry.append(crvs)
    


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
    
    
def loadOut(path,name,type="SW"):
    #Load SW output file
    in_file = open(path+name+"_"+type+".out","r")
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
    annIrr = []
    for s in xrange(len(bIDs)):
        if bIDs[s] != "NA" and bIDs[s] != "" : #remove columns
            sIDs2.append(int(sIDs[s]))
            bIDs2.append(int(bIDs[s]))
            IDs.append([int(bIDs[s]),int(sIDs[s])])
            irrS2.append(irrS[s])
            annIrr.append(sum(irrS[s])/1000)
    return irrS2, bIDs2, sIDs2, annIrr


def ParseTHhead(THhead):
    #Parse header
    import re
    header = THhead.split()
    #header.pop(0)
    print header
    
def ParseTHres(THres,yrl=False):
    nbuildings = (len(THres[0].split())-1)/12
    heating = []
    cooling = []
    for i in THres:
        values = i.split()
        heat = []
        cool = []
        for h in xrange(2,len(values),len(values)/nbuildings):
            heat.append(float(values[h]))
            cool.append(float(values[h+1]))
        heating.append(heat)
        cooling.append(cool)
    #for each building
    heating2 = []
    cooling2 = []
    for b in xrange(nbuildings): #for each surface
        heat = []
        cool = []
        for h in xrange(len(heating)): #for each hour
              heat.append(heating[h][b])
              cool.append(cooling[h][b])
        if yrl:
            heating2.append([sum(heat)])
            cooling2.append([sum(cool)])
        else:
            heating2.append(heat)
            cooling2.append(cool)
    return heating2, cooling2
   
if Run:
    header, results = loadOut(path,name,"SW")
    THhead, THres = loadOut(path,name,type="TH")
    bIDs, sIDs = parseHead(header)
    irrS = parseRes(results,sIDs)
    irrS2, bIDs2, sIDs2, annIrr = removeTerr(irrS,bIDs,sIDs)
    
    
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
    hSW = []
    ySW = []
    for b in bIDs3set:
        hrl = []
        yrl = []
        for s in xrange(len(sIDs3)):
            if bIDs3[s] == b:
                #print b, sIDs2[s]
                #print str(b)+'-'+str(sIDs3[s])
                hrl.append(diction.get(str(b)+'-'+str(sIDs3[s]),[-1])) #if the key is valid retun list of hourly values, otherwise empty list
                yrl.append([sum(diction.get(str(b)+'-'+str(sIDs3[s]),[-1]))])
        ySW.append(yrl)
        hSW.append(hrl)
    if yearly:
        SW = list_to_tree(ySW,none_and_holes=True, source=[])
        heating, cooling = ParseTHres(THres,yrl=True)
        H = list_to_tree(heating,none_and_holes=True, source=[])
        C = list_to_tree(cooling,none_and_holes=True, source=[])
    else:
        SW = list_to_tree(hSW,none_and_holes=True, source=[])
        heating, cooling = ParseTHres(THres)
        H = list_to_tree(heating,none_and_holes=True, source=[])
        C = list_to_tree(cooling,none_and_holes=True, source=[]) 
    
    Geometry = list_to_tree(geometry, source=[])