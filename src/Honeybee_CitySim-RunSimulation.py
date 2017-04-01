# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
# © All rights reserved. Ecole polytechnique fédérale de Lausanne (EPFL), Switzerland,
# Interdisciplinary Laboratory of Performance-Integrated Design (LIPID), 2016-2017
# Author: Giuseppe Peronato, <giuseppe.peronato@epfl.ch
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/
#
# This component relies on Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

"""
This component imports the geometry and runs the simulation.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        _HBZones: List of Honeybee zones
        _Windows: List of Window ratios for walls (or tree in which each branch is a building): GlazingRatio, GValue, GlazingUValue, OpenableRatio
        _Occupancy: List of (or tree in which each branch is a building): Number of occupants and ScheduleProfileID
        _CSobjs: List of CitySim objects (e.g. climate file, schedules)
        type: type of simulation (F = Full thermal + SW, I = SW-only). Default = F
        dir: Directory of simulation
        name: name of the project
        Write: Boolean to write the XML file
        Run: Boolean to start the simulation
    Returns:
        Out: nothing
"""

ghenv.Component.Name = "Honeybee_CitySim-RunSimulation"
ghenv.Component.NickName = 'CitySim-RunSimulation'
ghenv.Component.Message = 'VER 0.2.2\nAVR_01_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
#compatibleHBVersion = VER 0.0.56\nNOV_04_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass



import Rhino as rc
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os
import System
import Grasshopper.Kernel as gh
import math
import shutil
import collections
import subprocess
import copy

rc.Runtime.HostUtils.DisplayOleAlerts(False)

#Default values

type = "F"

if _Occupancy.BranchCount == 0:
    warning = "Missing Occupancy: Add list or Tree"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    print warning
    
lb_preparation = sc.sticky["ladybug_Preparation"]()
hb_reEvaluateHBZones= sc.sticky["honeybee_reEvaluateHBZones"]
hb_hive = sc.sticky["honeybee_Hive"]()
hb_EPScheduleAUX = sc.sticky["honeybee_EPScheduleAUX"]()
hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
hb_EPPar = sc.sticky["honeybee_EPParameters"]()
EPConstructions = sc.sticky ["honeybee_constructionLib"].keys() 
EPMaterials =  sc.sticky ["honeybee_materialLib"].keys()
EPWindowMaterials = sc.sticky ["honeybee_windowMaterialLib"].keys()
ThermMaterials = sc.sticky["honeybee_thermMaterialLib"].keys()   
thermalZonesPyClasses = hb_hive.callFromHoneybeeHive(_HBZones)
    
EPConstructions.sort()
EPMaterials.sort()
EPWindowMaterials.sort()
ThermMaterials.sort()      
def EPConstructionStr(constructionName):
        constructionData = None
        if constructionName in sc.sticky ["honeybee_constructionLib"].keys():
            constructionData = sc.sticky ["honeybee_constructionLib"][constructionName]
        
        if constructionData!=None:
            materials = []
            numberOfLayers = len(constructionData.keys())
            constructionStr = constructionData[0] + ",\n"
            # add the name
            constructionStr =  constructionStr + "  " + constructionName + ",   !- name\n"
            
            for layer in range(1, numberOfLayers):
                if layer < numberOfLayers-1:
                    constructionStr =  constructionStr + "  " + constructionData[layer][0] + ",   !- " +  constructionData[layer][1] + "\n"
                else:
                    constructionStr =  constructionStr + "  " + constructionData[layer][0] + ";   !- " +  constructionData[layer][1] + "\n\n"
                materials.append(constructionData[layer][0])
                
            return materials
        else:
            warning = "Failed to find " + constructionName + " in library."
            if constructionName != "Interior Wall": #Do not raise exception with interior wall, as this is automatically defined for adjacent srfs
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return None, None
            
def getMaterialProperties(matName):
    if not sc.sticky["honeybee_release"]:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")
        return -1
        
    # get the constuction
    try:
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
    except:
        msg = "Failed to load EP constructions!"
        print msg
        ghenv.Component.AddRuntimeMessage(w, msg)
        return -1
    
    if sc.sticky.has_key("honeybee_materialLib"):
        result = hb_EPMaterialAUX.decomposeMaterial(matName.upper(), ghenv.Component)
        if result == -1:
            warning = "Failed to find " + matName + " in the Honeybee material library."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return result

#Get surfaces from Honeybee zones
def getSurfaces(HBZones):
    hb_hive = sc.sticky["honeybee_Hive"]()
    geometry = []
    HBO = hb_hive.callFromHoneybeeHive(HBZones)
    for b in HBO:
        crvs = []
        HBSurfaces  = hb_hive.addToHoneybeeHive(b.surfaces, ghenv.Component.InstanceGuid.ToString())
        for s in HBSurfaces:
            edges = rs.DuplicateEdgeCurves(s)
            crvs.append(rs.JoinCurves(edges))
        geometry.append(crvs)
    return geometry

def getAttributes(HBZones):
    # call the objects from the lib
    thermalZonesPyClasses = hb_hive.callFromHoneybeeHive(HBZones)
    attributes = [['Type of surface','Solar Reflectance','Boundary Condition']] #when you add an attribute, list here what it means. 
    zoneatt = []
    for zone in thermalZonesPyClasses:
        type = []
        srefl = []
        BC = []
        for srf in zone.surfaces:
            if srf.type == 0:
                type.append('Wall')
            elif srf.type >= 2.0 and srf.type < 3.0: #Floor
                type.append('Floor')
            elif srf.type == 1:
                type.append('Roof')
            srf.construction = srf.EPConstruction
            materials = EPConstructionStr(srf.construction)
            if srf.BC =="Outdoors" or srf.BC=="Ground":
                srefl.append(str((1 - float(getMaterialProperties(materials[0])[0][-2]))))
            else:
                srefl.append('None')
            BC.append(srf.BC)
        zoneatt.append([type,srefl,BC])    
    attributes.append(zoneatt)
    return attributes
     
def getLayers(cnstrName):
    return hb_EPMaterialAUX.decomposeEPCnstr(cnstrName.upper())
    
def getMaterials(matName):
    return hb_EPMaterialAUX.decomposeMaterial(matName.upper(), ghenv.Component)

def getVolume(b):
    volume = _HBZones[b].GetVolume()
    return volume

def getConLibrary():
    xml = ''
    for c in range(len(EPConstructions)):
        if getMaterials(getLayers(EPConstructions[c])[0][0])[0][0] == 'Material': 
            xml += '<Composite id="{0}" name="{1}">\n'.format(c,EPConstructions[c])
            for l in getLayers(EPConstructions[c])[0]:
                mats = getMaterials(l)[0]
                if mats[0] == 'Material': #Check that the material has all properties we need
                    xml += '<Layer Thickness="{0}" Conductivity="{1}" Cp="{2}" Density="{3}"/>\n'.format(mats[2],mats[3],mats[5],mats[4])
            xml += '</Composite>\n'
        elif getMaterials(getLayers(EPConstructions[c])[0][0])[0][0] == 'Material:NoMass': #This material has no mass
               l = getLayers(EPConstructions[c])[0][0] #Take the external layer in a construction without mass
               mats = getMaterials(l)[0]
               try:
                    i = getMaterials(l)[1].index('Thermal Resistance {m2-K/W}') #Index of resistance
               except:
                    pass
               try:
                    i = getMaterials(l)[1].index('- Thermal Resistance {m2-K/W}') #Index of resistance
               except:
                    pass
               UValue = 1/float(mats[i]) #Calculate U-value from R-Value
               xml += '<Composite id="{0}" name="{1}" Uvalue="{2}">\n'.format(c,EPConstructions[c],UValue)
               xml += '</Composite>\n'
    return xml

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


def getWindows():
    if _Windows != None:
       ratios = tree_to_list(_Windows, lambda x: x)
    else:
       #GlazingRatio="0.5" GlazingGValue="0.3" GlazingUValue="0.45" OpenableRatio="0"
       ratios = [0.5,0.3,0.45,0.0]
    return ratios
    
def getOccupancy():
    if _Occupancy != None:
       occupancy = tree_to_list(_Occupancy, lambda x: x)
    else:
       print 'Error'
    return occupancy 

#Create XML files in CitySim format
def createXML(geometry,attributes):
    #Header and default values
    xml = ""
    xml += getConLibrary()
    #Windows ratios
    wratios = getWindows()
    #Add geometry to the XML file
    for b in xrange(len(geometry)):
        xml += '''<Building Name="GROUP_1" id="'''+ str(b) + '''" key="1" Vi="1123.5" Ninf="0.15" BlindsLambda="0.2" BlindsIrradianceCutOff="100" Simulate="true">
                <HeatTank V="0.01" phi="20" rho="1000" Cp="4180" Tmin="20" Tmax="35"/>
			    <CoolTank V="0.01" phi="20" rho="1000" Cp="4180" Tmin="5" Tmax="20"/>
			    <HeatSource beginDay="1" endDay="365">
				    <HeatPump Pmax="1000" eta_tech="0.3" Ttarget="55" Tsource="ground" depth="5" alpha="0.0700000003" position="vertical" z1="10" />
			    </HeatSource>
			    <CoolSource beginDay="1" endDay="365">
				    <HeatPump Pmax="10000000" eta_tech="0.3" Ttarget="5" Tsource="ground" depth="5" alpha="0.0700000003" position="vertical" z1="10" />
			    </CoolSource>\n'''

        #Check if there is a surface with BC=Ground
        GroundFloor = False #default no ground
        for BC in attributes[1][b][2]:
            if BC =="Ground":
                GroundFloor = True
        xml += '<Zone id="1" volume="{0}" psi="0.2" Tmin="20" Tmax="26" groundFloor="{1}" >'.format(getVolume(b),str(GroundFloor))
        
        occupancy = getOccupancy()
        if len(occupancy) == 1:
            occ = occupancy[0]
        else:
            occ = occupancy[b]
        xml +=	'<Occupants n="{0}" type="{1}"/>\n'.format(occ[0],occ[1])
        
        for s in xrange(len(geometry[b])):
            #xml += '<' + attributes[1][b][0][s] + ' id="'+str(s)+'" type="'+ str(EPConstructions.index(thermalZonesPyClasses[b].surfaces[s].EPConstruction))+'" ShortWaveReflectance="' + attributes[1][b][1][s] + '" GlazingRatio="0.25" GlazingGValue="0.7" GlazingUValue="1.1" OpenableRatio="0">\n'
            if attributes[1][b][0][s] == 'Wall' and len(wratios)>1: #Use windows ratios only for walls
                windows = wratios[b]
            elif attributes[1][b][0][s] == 'Wall' and len(wratios)==1: #This is the case when ratios are defined globally and not per building
                windows = wratios[0]
            else:
                windows = [0,0,0,0] #default values for windows ratios for non-wall surfaces
            
            if attributes[1][b][2][s] == 'Outdoors' or attributes[1][b][2][s] == 'Ground': #Do not write surface with adjacent BC
                xml += '<{0} id="{1}" type="{2}" ShortWaveReflectance="{3}" GlazingRatio="{4}" GlazingGValue="{5}" GlazingUValue="{6}" OpenableRatio="{7}">\n'.format(attributes[1][b][0][s],s,EPConstructions.index(thermalZonesPyClasses[b].surfaces[s].EPConstruction),attributes[1][b][1][s],windows[0],windows[1],windows[2],windows[3])
                srfpts = rs.CurvePoints(geometry[b][s])
                for i in xrange(len(srfpts)):
                    #print '<V' + str(i) + ' x="' + str(srfpts[i][0]) +'" y="' + str(srfpts[i][1]) +'" z="' + str(srfpts[i][2])+'"/> \n'
                    xml+= '<V' + str(i) + ' x="' + str(srfpts[i][0]) +'" y="' + str(srfpts[i][1]) +'" z="' + str(srfpts[i][2])+'"/> \n'
                xml+= '</' + attributes[1][b][0][s] + '>'
        xml+= '''   </Zone>
                </Building>'''
    return xml
    
def createHeader():
    xml = '''<?xml version="1.0" encoding="ISO-8859-1"?>
    <CitySim name="test">
	    <Simulation beginMonth="1" endMonth="12" beginDay="1" endDay="31"/>'''

    xml += '<Climate location="' + climatefile + ' "city="Unknown"/>'
    xml += "	<District>"
    return xml
    
def createFooter():
    xml = ""
    xml+= '''</District>
		   </CitySim> '''
    return xml
    

#Write XML file
def writeXML(xml, path, name):
    xmlpath = path+name+".xml"
    out_file = open(xmlpath,"w")
    out_file.write(xml)
    out_file.close()
    
def getCSobjs(CSobjs):
    climate = ""
    horizon = ""
    shading = ""
    schedule = ""
    terrain = ""
    for path in CSobjs:
        if path != None and path.split(".")[1] == "cli":
            climate = path
        elif path != None and path.split(".")[1] == "hor":
            horizon = path
        elif path != None and path.split(".")[1] == "shd":
            shading = path
        elif path != None and path.split(".")[1] == "sch":
            schedule = path
        elif path != None and path.split(".")[1] == "gnd":
            terrain = path
    return terrain,horizon,shading,schedule,climate
 
terrain,horizon,shading,schedule,climate = getCSobjs(_CSobjs)
dir += "\\" #Add \ in case is missing

if climate == "":
    warning = "Missing climate file: add one as CSobj."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    print warning

if Write:
    geometry = getSurfaces(_HBZones)
    attributes = getAttributes(_HBZones)
    #terrain, horizon,shading,schedule = getextraXML()
    xml = createXML(geometry,attributes)
    writeXML(xml,dir,name+"_main")
    header = createHeader()
    footer = createFooter()
    writeXML(header,dir,name+"_head")
    writeXML(footer,dir,name+"_foot")

xmlpath = dir+name+'.xml'

#Create copy command
join = "copy "+dir+name+"_head.xml"
if horizon != "":
    join += "+" + horizon 
if schedule != "":
    join += "+" + schedule
else:
    warning = "Missing occupancy schedule: add one as CSobj."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    print warning
join += "+" +dir+name+"_main.xml"
if terrain != "":
    join += "+" + terrain
if shading != "":
    join += "+" + shading
join += "+" +dir+name+"_foot.xml"
join += " " +dir+name+".xml"

#Create simulation command
if type == "F": 
    simulation = Solver + ' ' + xmlpath
elif type =="I":
    imulation = Solver + ' -I ' + xmlpath

#Run the simulation
if Run:
    os.chdir(dir)
    os.system(join)
    os.system(simulation)