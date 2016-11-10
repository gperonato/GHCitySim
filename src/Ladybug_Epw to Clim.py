# Interface to CitySim Solver
# http://citysim.epfl.ch/
#
# GH-Python component initiated by
# Giuseppe Peronato <giuseppe.peronato@epfl.ch> 
# 

"""
This component converts an EPW file into a CLI file.

-
This component will hopefully be part of
Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

-

    
    Args:
        _epwFile: EPW file
        path: Directory
        Run: Boolean
    Returns:
        climatefile: name of climate file (with extension)

"""




import scriptcontext as sc
import os
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Ladybug_Epw to Clim"
ghenv.Component.NickName = 'EPW-to-Clim'
ghenv.Component.Message = 'VER 0.0.1\nNOV_10_2016'
#compatibleLBVersion = VER 0.0.59\nJUN_07_2015
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"

try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


def main(_epw_file):
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
        
        return locationData, weatherData
    
    else:
        warningM = "First please let the Ladybug fly..."
        print warningM
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warningM)
        return -1
    

result = main(_epwFile)

if result!= -1:
    location, locName, latitude = result[0][-1], result[0][0], result[0][1]
    dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, horizontalInfraredRadiation, barometricPressure, modelYear = result[1][:]
    print 'Hourly weather data for ' + locName + ' is imported successfully!'


   
#Create the header

#standard values
if longitude == "None":
    longitude = 6.93 #Neuchatel
if altitude == "None":
    altitude = 0
if meridian == "None":
    meridian = 1
    
    
header = locName
header += "\n\n" + latitude + "," + str(longitude) + "," + str(altitude) + "," + str(meridian) + "\n\n\n\n" #Data missing here, substituted with "1+
header += "dm\tm\th\tG_Dh\tG_Bn\tTa\tFF\tDD\tRH\tRR\tN\n\n"



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
nebulosity = 0

if Run:
    data = ""
    for h in xrange(7,len(diffuseHorizontalRadiation)):
        data += "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n\n".format(1,1,1,int(diffuseHorizontalRadiation[h]),int(directNormalRadiation[h]),dryBulbTemperature[h],windSpeed[h],int(windDirection[h]),int(relativeHumidity[h]),precipitation,nebulosity)


    #Write CLI file
    clipath = path+locName+".cli"
    print clipath
    out_file = open(clipath,"w")
    out_file.write(header + data)
    out_file.close()


#Retrieve the name of the climate file  
climatefile = locName.lower()+".cli"

 
