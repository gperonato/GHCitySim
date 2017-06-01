# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
# © All rights reserved. Ecole polytechnique fédérale de Lausanne (EPFL), Switzerland,
# Laboratory of Integrated Performance in Design (LIPID), 2016-2017
# Author: Giuseppe Peronato, <giuseppe.peronato@epfl.ch>
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/

"""
This component produces the XML code for the occupancy schedules

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        day: occupancy profiles [0,1]for each hour of the day
        dir: directory of project
        name: title of project
        Write: Boolean to start
"""

ghenv.Component.Name = "Honeybee_CitySim-Schedules"
ghenv.Component.NickName = 'CitySim-Schedules'
ghenv.Component.Message = 'VER 0.0.3\nAVR_01_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "14 | CitySim"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

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

ReqInputs = True
    
if dir == None:
    print "Select a directory" #this is mandatory: no default
    ReqInputs = False
else:
    dir += "\\" #Add \ in case is missing
    
if name == None:
    name = "simulation" #default name

wday = tree_to_list(day, lambda x: x)


def makeDay(d):
    xml = ""
    for p in xrange(len(d)):
        xml += '<OccupancyDayProfile id="{0}" '.format(p)
        for h in xrange(len(d[p])):
            #<OccupancyDayProfile id="5" p1="0.31" p2="0.35" p3="0.37" p4="0.4" p5="0.42" p6="0.44" p7="0.46" p8="0.49" p9="0.57" p10="0.62" p11="0.69" p12="0.75" p13="0.8" p14="0.77" p15="0.7" p16="0.62" p17="0.59" p18="0.53" p19="0.51" p20="0.51" p21="0.48" p22="0.43" p23="0.47" p24="0.43" />
            xml += 'p{0}="{1}" '.format(h+1,d[p][h])
        xml += "/>\n"
    return xml
    
def makeYear():
    xml = ""
    for p in xrange(len(wday)):
        xml += '<OccupancyYearProfile id="{0}" '.format(p)
        for d in xrange(365):
            xml += 'd{0}="{1}" '.format(d+1,p)
        xml += "/>\n"
    return xml


if Write == False and ReqInputs == True:
    print "Set Write to True"     
elif Write == True and ReqInputs == True:
    FilePath = dir + name + ".sch"
    with open(FilePath, "w") as outfile:
        outfile.write(makeDay(wday))
        outfile.write(makeYear())
    print "XML file created"
    
try:
    CSobj = FilePath
except:
    pass 