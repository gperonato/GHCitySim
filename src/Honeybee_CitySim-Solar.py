# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
# © All rights reserved. Ecole polytechnique fédérale de Lausanne (EPFL), Switzerland,
# Interdisciplinary Laboratory of Performance-Integrated Design (LIPID), 2016-2017
# Author: Giuseppe Peronato, <giuseppe.peronato@epfl.ch>
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/

"""
This component imports the geometry and runs the simulation for solar radiation.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        _Geometry: Tree of curves {building;surfaces}
        _Reflectance: Tree of reflectance (same structure as geometry)
        _CSobjs: list of CitySim objects
        dir: Directory
        name: name of the project
        Write: Boolean to write the XML file
        Run: Boolean to start the simulation
    Returns:
        Out: nothing
"""

ghenv.Component.Name = "Honeybee_CitySim-Solar"
ghenv.Component.NickName = 'CitySim-Solar'
ghenv.Component.Message = 'VER 0.0.3\nAVR_01_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
#compatibleHBVersion = VER 0.0.56\nFEB_03_2016
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import Rhino as rc
import scriptcontext as sc
import os
import System
import Grasshopper.Kernel as gh
import math
import shutil
import collections
import subprocess
import copy


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
    
def getCSobjs(CSobjs):
    climate = ""
    horizon = ""
    shading = ""
    terrain = ""
    for path in CSobjs:
        if path != None and path.split(".")[1] == "cli":
            climate = path
        elif path != None and path.split(".")[1] == "hor":
            horizon = path
        elif path != None and path.split(".")[1] == "shd":
            shading = path
        elif path != None and path.split(".")[1] == "gnd":
            terrain = path
    return terrain,horizon,shading,climate

#Create XML files in CitySim format
def createXML(geometry,reflectance):
    xml = '''
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
            for p in range(geometry[b][s].Count):
            #srfpts = rs.CurvePoints(geometry[b][s])
            #for i in xrange(len(srfpts)):
                #print '<V' + str(i) + ' x="' + str(srfpts[i][0]) +'" y="' + str(srfpts[i][1]) +'" z="' + str(srfpts[i][2])+'"/> \n'
                xml+= '<V' + str(p) + ' x="' + str(geometry[b][s].X[p]) +'" y="' + str(geometry[b][s].Y[p]) +'" z="' + str(geometry[b][s].Z[p])+'"/> \n'
            xml+= '</' + 'Wall' + '>'        
            #xml+= '</' + attributes[1][b][0][s] + '>'
        xml+= '''   </Zone>
                </Building>'''
    return xml

def createHeader():
    xml = '''<?xml version="1.0" encoding="ISO-8859-1"?>
    <CitySim name="test">
	    <Simulation beginMonth="1" endMonth="12" beginDay="1" endDay="31"/>'''

    xml += '<Climate location="' + climate + ' "city="Unknown"/>'
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
    
geometry = tree_to_list(geometry, lambda x: x)
reflectance = tree_to_list(reflectance, lambda x: x)

terrain,horizon,shading,climate = getCSobjs(_CSobjs)
if dir != None:
    dir += "\\" #Add \ in case is missing

if climate == "":
    warning = "Missing climate file: add one as CSobj."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    print warning
    
if Write:
    xml = createXML(geometry,reflectance)
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
    join += "+" +dir+name+"_main.xml"
    if terrain != "":
        join += "+" + terrain
    if shading != "":
        join += "+" + shading
    join += "+" +dir+name+"_foot.xml"
    join += " " +dir+name+".xml"
    
    #Merge files
    os.chdir(dir)
    os.system(join)

#Run the simulation
if Run:
    simulation = Solver + ' -I ' + xmlpath #only solar irradiation
    os.chdir(dir)
    os.system(simulation)