# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
# © All rights reserved. Ecole polytechnique fédérale de Lausanne (EPFL), Switzerland,
# Interdisciplinary Laboratory of Performance-Integrated Design (LIPID), 2016-2017
# Author: Giuseppe Peronato, <giuseppe.peronato@epfl.ch
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/

"""
This component transforms a list of horizontal and vertical angles representing far field obstructions in CitySim format.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        H: List of horizontal angles
        V: List of vertical angles (obstructions)
        dir: directory of project
        name: title of project
        Write: Boolean to start
"""

ghenv.Component.Name = "Honeybee_CitySim-Horizon"
ghenv.Component.NickName = 'CitySim-Horizon'
ghenv.Component.Message = 'VER 0.0.3\nAVR_01_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import rhinoscriptsyntax as rs

ReqInputs = True

if H == None or V == None:
    print "Add angles"
    ReqInputs = False
    
if dir == None:
    print "Select a directory" #this is mandatory: no default
    ReqInputs = False
else:
    dir += "\\" #Add \ in case is missing
    
if name == None:
    name = "simulation" #default name
		    
XML = "<FarFieldObstructions>\n"
if ReqInputs:
    for a in range(len(H)):
            XML += '<Point phi="{0}" theta="{1}"/>\n'.format(H[a],V[a])
    XML += '</FarFieldObstructions>'


def writeXML(xml, path, name):
    xmlpath = path+name+".hor"
    out_file = open(xmlpath,"w")
    out_file.write(xml)
    out_file.close()
    return xmlpath

if ReqInputs and Write:
    obj = writeXML(XML,dir,name)
    print "XML file created"
else:
    print "Set Write to true"
 
try:
    CSobj = obj
except:
    pass