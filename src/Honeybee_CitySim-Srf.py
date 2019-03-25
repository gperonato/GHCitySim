﻿# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
# © All rights reserved. Ecole polytechnique fédérale de Lausanne (EPFL), Switzerland,
# Laboratory of Integrated Performance in Design (LIPID), 2016-2018
# Developer: Giuseppe Peronato <giuseppe.peronato@alumni.epfl.ch>

# Further development conducted at Uppsala University, Sweden.
# Division of Construction Engineering, 2019
# Developer: Giuseppe Peronato <giuseppe.peronato@angstrom.uu.se>
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/

"""
This component imports the geometry and produces the XML code representing shading surfaces or terrain (simulated but excluded from results)

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        S: List of  meshes
        R: List (or single value) for SW reflectance; Default = 0.1
        EPConstructionName: List of names or single name of EnergyPlus Construction, needed for considering thermal exchanges with the ground. The solar properties of the construction are not considered here, use the R parameter instead.
        type: either "Surface" or "Terrain" - default = "Surface"
        Dup: Boolean to duplicate obstructing surfaces with reversed normals: Default = True
        Sim: Boolean to include the surfaces in the results: Default = False
        dir: directory of project
        name: title of project
        Write: Boolean to start
"""

ghenv.Component.Name = "Honeybee_CitySim-Srf"
ghenv.Component.NickName = 'CitySim-Srf'
ghenv.Component.Message = 'VER 0.0.5\nMAR_25_2019'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh

EPConstructions = sc.sticky ["honeybee_constructionLib"].keys() 


#Default reflectance
if len(R) == 0:
    R.append(0.1) 

#If multiple meshes and only 1 reflectance/construction, use this for all meshes
while len(R) < len(S):
    R.append(R[0])
    

if len(EPConstructionName) == 0:
    EPConstructionName = [""]
while len(EPConstructionName) < len(S):
    EPConstructionName.append(EPConstructionName[0])



ReqInputs = True

if Dup == None:
    Dup = True # By default duplicate surfaces
   
if type == None:
    type = "shading" # By default surfaces are considered as shading

if name == None:
    name = "simulation" #default name
    
if dir == None:
    print "Select a directory" #this is mandatory: no default
    ReqInputs = False
else:
    dir += "\\" #Add \ in case is missing  

if Write == False and ReqInputs == True:
    print "Set Write to True"     
elif Write == True and ReqInputs == True:
    if type == "terrain":
        FilePath = dir + name + ".gnd"
    else:
        FilePath = dir + name + ".shd"
    with open(FilePath, "w") as outfile:
        obj = FilePath
        if type == "terrain":
            outfile.write("<GroundSurface>\n")
        else:
            outfile.write("<ShadingSurface>\n")         
        for meshcount, Tmesh in enumerate(S):
            #for v in Tmesh.Vertices:
            facecount = 0
            for face in Tmesh.Faces:
                if type == "terrain":
                    s = "Ground"
                else:
                    s = "Surface"
                if len(EPConstructionName[meshcount]) > 0:
                    try:
                        construction = 'type="{}"'.format(EPConstructions.index(EPConstructionName[meshcount].upper()))
                    except:
                         warning = "Check EPConstructionName"
                         ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
                         print(warning)
                         construction = ""
                else:
                    construction = ""
                outfile.write('<{0} id="s{1}" {3} ShortWaveReflectance="{2}">\n'.format(s,str(meshcount)+'-'+str(facecount),str(R[0]),construction))
                outfile.write('<V0 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.A].X,Tmesh.Vertices[face.A].Y,Tmesh.Vertices[face.A].Z))
                outfile.write('<V1 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.B].X,Tmesh.Vertices[face.B].Y,Tmesh.Vertices[face.B].Z))
                outfile.write('<V2 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.C].X,Tmesh.Vertices[face.C].Y,Tmesh.Vertices[face.C].Z))
                if face.IsQuad:
                    outfile.write('<V3 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.D].X,Tmesh.Vertices[face.D].Y,Tmesh.Vertices[face.D].Z))
                outfile.write('</{0}>'.format(s))
            
                if Dup: #Duplicate surfaces with reversed normals
                    outfile.write('<{0} id="s{1}-verso" {3} ShortWaveReflectance="{2}">\n'.format(s,str(meshcount)+'-'+str(facecount),str(R[0]),construction))
                    if face.IsQuad:
                        outfile.write('<V3 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.D].X,Tmesh.Vertices[face.D].Y,Tmesh.Vertices[face.D].Z))
                    outfile.write('<V0 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.C].X,Tmesh.Vertices[face.C].Y,Tmesh.Vertices[face.C].Z))
                    outfile.write('<V1 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.B].X,Tmesh.Vertices[face.B].Y,Tmesh.Vertices[face.B].Z))
                    outfile.write('<V2 x ="{0}" y="{1}" z ="{2}"/>\n'.format(Tmesh.Vertices[face.A].X,Tmesh.Vertices[face.A].Y,Tmesh.Vertices[face.A].Z))
                    outfile.write('</{0}>'.format(s))
                facecount += 1
        if type == "terrain":
            outfile.write("</GroundSurface>")
        else:
            outfile.write("</ShadingSurface>")
    print "XML file created"
elif Write == True and ReqInputs == False:
    warning = "Check Required Inputs"
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
try:
    CSobj = obj
except:
    pass