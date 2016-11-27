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
    Returns:
        XML: XML code
"""

ghenv.Component.Name = "Honeybee_CitySim-Horizon"
ghenv.Component.NickName = 'CitySim-Horizon'
ghenv.Component.Message = 'VER 0.0.1\nNOV_25_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import rhinoscriptsyntax as rs


		    
XML = "<FarFieldObstructions>\n"
for a in range(len(H)):
        XML += '<Point phi="{0}" theta="{1}"/>\n'.format(H[a],V[a])
XML += '</FarFieldObstructions>'
print XML            