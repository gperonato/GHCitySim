# Interface to CitySim Solver
# http://citysim.epfl.ch/
#
# GH-Python component initiated by
# Giuseppe Peronato <giuseppe.peronato@epfl.ch> 
# 

"""
This component imports the geometry and runs the simulation for solar radiation.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        geometry: Tree of curves {building;surfaces}
        reflectance: Tree of reflectance (same structure as geometry)
        path: Directory
        name: name of the project
        climatefile: name of climate file (with extension)
        XML: extra XML strings (e.g. terrain, far-field obstructions)
        Write: Boolean to write the XML file
        Run: Boolean to start the simulation
    Returns:
        Out: nothing
"""

ghenv.Component.Name = "Honeybee_CitySim-Solar"
ghenv.Component.NickName = 'CitySim-Solar'
ghenv.Component.Message = 'VER 0.0.1\nJAN_16_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
#compatibleHBVersion = VER 0.0.56\nFEB_03_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "1"


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
reflectance = tree_to_list(reflectance, lambda x: x)

def getAttributes(HBZones):
    # call the objects from the lib
    thermalZonesPyClasses = hb_hive.callFromHoneybeeHive(HBZones)
    attributes = [['Type of surface','Solar Reflectance']] #when you add an attribute, list here what it means. 
    zoneatt = []
    for zone in thermalZonesPyClasses:
        type = []
        srefl = []
        for srf in zone.surfaces:
            if srf.type == 0:
                type.append('Wall')
            elif srf.type == 2.5:
                type.append('Floor')
            elif srf.type == 1:
                type.append('Roof')
            srf.construction = srf.EPConstruction
            materials = EPConstructionStr(srf.construction)
            srefl.append(str((1 - float(getMaterialProperties(materials[0])[0][4]))))
        zoneatt.append([type,srefl])    
    attributes.append(zoneatt)
    return attributes


def getextraXML(XML):
    horizon = ""
    terrain = ""
    shading = ""
    if len(XML) > 0:
        for i in XML:
            if i[1:7] == "Ground":
                terrain = i
            if i[1:9] == "FarField":
                horizon = i
            if i[1:8] == "Shading":
                shading = i
    return terrain, horizon, shading
        
print getextraXML(XML)
#Create XML file in CitySim format
def createXML(geometry,terrain,horizon,shading,reflectance):
    #Header and default values
    xml = '''<?xml version="1.0" encoding="ISO-8859-1"?>
    <CitySim name="test">
	    <Simulation beginMonth="1" endMonth="12" beginDay="1" endDay="31"/>'''

    xml += '<Climate location="' + climatefile + ' "city="Unknown"/>'
    xml += "	<District>"
    xml += horizon
    xml += '''
		    <Composite id="21" name="Simple wall" category="Wall">
			    <Layer Thickness="0.1500" Conductivity="200.0000" Cp="418" Density="8900" nre="0" gwp="0" ubp="0"/>
		    </Composite>
    '''

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
			    </CoolSource>
			    <Zone id="1" volume="1123.5" psi="0.2" Tmin="21" Tmax="27" groundFloor="true" >
				    <Occupants n="9" d="0.06" type="2"/>'''
        for s in xrange(len(geometry[b])):
            #xml += '<' + attributes[1][b][0][s] + ' id="'+str(s)+'" type="21" ShortWaveReflectance="' + attributes[1][b][1][s] + '" GlazingRatio="0.25" GlazingGValue="0.7" GlazingUValue="1.1" OpenableRatio="0">\n'
            xml += '<' + 'Wall' + ' id="'+str(s)+'" type="21" ShortWaveReflectance="' + str(reflectance[b][s]) + '" GlazingRatio="0.25" GlazingGValue="0.7" GlazingUValue="1.1" OpenableRatio="0">\n'
            srfpts = rs.CurvePoints(geometry[b][s])
            for i in xrange(len(srfpts)):
                #print '<V' + str(i) + ' x="' + str(srfpts[i][0]) +'" y="' + str(srfpts[i][1]) +'" z="' + str(srfpts[i][2])+'"/> \n'
                xml+= '<V' + str(i) + ' x="' + str(srfpts[i][0]) +'" y="' + str(srfpts[i][1]) +'" z="' + str(srfpts[i][2])+'"/> \n'
            xml+= '</' + 'Wall' + '>'        
            #xml+= '</' + attributes[1][b][0][s] + '>'
        xml+= '''   </Zone>
                </Building>'''
            
    #Add sample footer to the XML file
    if len(terrain) > 0:
        xml+= shading
    if len(terrain) > 0:
        xml+= terrain
    xml+= '''</District>
		   </CitySim> '''
    return xml



#Write XML file
def writeXML(xml, path, name):
    xmlpath = path+name+".xml"
    out_file = open(xmlpath,"w")
    out_file.write(xml)
    out_file.close()

if Write:
    terrain, horizon,shading = getextraXML(XML)
    xml = createXML(geometry,terrain,horizon,shading,reflectance)
    writeXML(xml,path,name)

#Run the simulation
if Run:

    xmlpath = path+name+'.xml'
    command = Solver + ' -I ' + xmlpath #Runs only irradiation simulation with -I

    import os
    os.chdir(path)
    os.system(command)