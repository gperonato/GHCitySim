# Interface to CitySim Solver
# http://citysim.epfl.ch/
#
# GH-Python component initiated by
# Giuseppe Peronato <giuseppe.peronato@epfl.ch> 
# 

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
        path: path of project
        name: title of project
        Write: Boolean to start
"""

ghenv.Component.Name = "Honeybee_CitySim-Horizon"
ghenv.Component.NickName = 'CitySim-Horizon'
ghenv.Component.Message = 'VER 0.0.2\nJAN_18_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import rhinoscriptsyntax as rs


		    
XML = "<FarFieldObstructions>\n"
for a in range(len(H)):
        XML += '<Point phi="{0}" theta="{1}"/>\n'.format(H[a],V[a])
XML += '</FarFieldObstructions>'


def writeXML(xml, path, name):
    xmlpath = path+name+"_horizon.xml"
    out_file = open(xmlpath,"w")
    out_file.write(xml)
    out_file.close()

if Write:
    writeXML(XML,path,name)
    print "XML file created"
else:
    print "Set Write to true"