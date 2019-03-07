# GH-CitySim: an interface to CitySim started by Giuseppe Peronato
#
# © All rights reserved. Ecole polytechnique fédérale de Lausanne (EPFL), Switzerland,
# Interdisciplinary Laboratory of Performance-Integrated Design (LIPID), 2016-2017
# Developer: Giuseppe Peronato, <giuseppe.peronato@alumni.epfl.ch
#
# Further development conducted at Uppsala University, Sweden.
# Division of Construction Engineering, 2019
# Developer: Giuseppe Peronato <giuseppe.peronato@angstrom.uu.se>
#
# CitySim is a software developed and distributed by the
# Laboratory of Solar Energy and Building Physics (LESO-PB)
# http://citysim.epfl.ch/
#
# Contributions:
# Aymeric Delmas <aymeric.delmas@imageen.re>

"""
This component converts an EPW file into a CLI file.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        _epwFile: EPW file
        dir: Directory
        Run: Boolean
    Returns:
        climatefile: name of climate file (with extension)

"""




import scriptcontext as sc
import os
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Honeybee_Epw to Cli"
ghenv.Component.NickName = 'EPW-to-Cli'
ghenv.Component.Message = 'VER 0.0.4\nMAR_07_2019'
#compatibleLBVersion = VER 0.0.59\nJUN_07_2015
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "0 | Honeybee"

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


def main(_epw_file):
    #This function has been copied (with some adaptations)
    #from Ladybug's "Import epw" component, version VER 0.0.63\nAUG_10_2016'
    #All credits to the authors.
    
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        if not os.path.isfile(_epw_file):
            warningM = "Failed to find the file: " + str(_epw_file)
            print warningM
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warningM)
            return -1
        
        locationData = lb_preparation.epwLocation(_epw_file)
        weatherData = lb_preparation.epwDataReader(_epw_file, locationData[0])
        groundtemp = lb_preparation.groundTempData(_epwFile,[]);
        
        return locationData, weatherData, groundtemp
    
    else:
        warningM = "First please let the Ladybug fly..."
        print warningM
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warningM)
        return -1
    

result = main(_epwFile)

if result!= -1:
    location, locName, latitude, longitude, meridian, altitude = result[0][-1], result[0][0], result[0][1], result[0][2], result[0][3], result[0][4]
    dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, horizontalInfraredRadiation, barometricPressure, modelYear = result[1][:]
    groundtemp = result[2]
    print 'Hourly weather data for ' + locName + ' is imported successfully!'

#Ground Temperatures.
for d in groundtemp:
    if len(d) > 7:
        groundData = True
        groundtempNum = d[7:]
    
yearlyGroundTemp = []
if groundData: #Use groundtemperature is exists
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[0])
    for d in xrange(28*24):
        yearlyGroundTemp.append(groundtempNum[1])
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[2])
    for d in xrange(30*24):
        yearlyGroundTemp.append(groundtempNum[3])
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[4])
    for d in xrange(30*24):
        yearlyGroundTemp.append(groundtempNum[5])
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[6])
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[7])
    for d in xrange(30*24):
        yearlyGroundTemp.append(groundtempNum[8])
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[9])
    for d in xrange(30*24):
        yearlyGroundTemp.append(groundtempNum[10])
    for d in xrange(31*24):
        yearlyGroundTemp.append(groundtempNum[11])   
else: #Use meanDryBulbTemperature
    meanDryBulbTemperature = round(float(sum(dryBulbTemperature[7:])) / float(len(dryBulbTemperature[7:])),1)
    for d in xrange(8760):
        yearlyGroundTemp.append(meanDryBulbTemperature)

#Create the header
locName = locName.strip()
header = locName
header += "\n\n" + str(latitude) + "," + str(longitude) + "," + str(altitude) + "," + str(meridian) + "\n\n\n\n"
header += "dm\tm\th\tG_Dh\tG_Bn\tTa\tTs\tFF\tDD\tRH\tRR\tN\n\n"


# Create time stamps
def datetime_range(start, end, delta):
    current = start
    if not isinstance(delta, timedelta):
        delta = timedelta(**delta)
    while current < end:
        yield current
        current += delta
#start = datetime(2010,1,1)
#end = datetime(2011,1,1)
#count = 0
#dates = []
#for dt in datetime_range(start,end,{'hours':1}):
    #dates.append((dt.day, dt.month, dt.hour))
    
    
#Import and write weather data
#default values
precipitation  = 0
nebulosity = 0 #clear sky


dir += "\\" #Add \ in case is missing
filename = _epwFile.replace("\\","/")
filename = filename.split("/")[-1].split(".")[0]

if Run:
    data = ""
    for h in xrange(7,len(diffuseHorizontalRadiation)):
        data += "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(1,1,1,int(diffuseHorizontalRadiation[h]),int(directNormalRadiation[h]),dryBulbTemperature[h],yearlyGroundTemp[h-7],windSpeed[h],int(windDirection[h]),int(relativeHumidity[h]),precipitation,nebulosity)


    #Write CLI file
    clipath = dir+filename+".cli"
    out_file = open(clipath,"w")
    out_file.write(header + data)
    out_file.close()


#Retrieve the name of the climate file  
CSobj = dir+filename+".cli"
