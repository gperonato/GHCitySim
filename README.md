GHCitySim
========================================
Set of Grasshopper components for interfacing with CitySim, an urban-scale building energy simulation tool.

GHCitySim requires [Ladybug and Honeybee legacy plugins](https://www.food4rhino.com/app/ladybug-tools "Ladybug + Honeybee") (as well as [GHPython](http://www.food4rhino.com/app/ghpython "GhPython") if you are using Rhino 5) to be installed.
A copy of the components from Ladybug and Honeybee needed to run GHCitySim is contained in this repository.

The GHCitySim components are saved both as compiled GH components (/userObjects) and source code (/src).
To install, just drag and drop the files in the /UserObjects directory onto the Grasshopper canvas.

In the resources folder you will find:
* two *.ghx files containing sample Grasshopper definitions where the components are used; the *_solar.ghx file contains an alternative workflow for solar simulations only, which does not rely on Ladybug/Honeybee libraries.
* a sample weather file in EnergyPlus format *.epw converted in CitySim format *.cli;

The simulation output files for the two sample workflows (*test* and *test_solar*) are saved in the /simulation directory.

About CitySim
---------------------
CitySim is a software developed and distributed by the Laboratory of Solar Energy and Building Physics (LESO-PB) of the Ecole polytechnique fédérale de Lausanne (EPFL).
The CitySim Solver can be downloaded from [here](https://citysim.epfl.ch).


Citation
---------------------
GHCitySim is free to use. You are kindly invited to acknowledge its use by citing it in a research paper you are writing, reports, and/or other applicable materials.
Please cite the following paper ([PDF](https://infoscience.epfl.ch/record/228832/files/Peronato_PLEA2017_paper_final_1.pdf)):
    
	@inproceedings{peronato_integrating_2017,
		address = {Edinburgh},
		title = {Integrating urban energy simulation in a parametric environment:
		a {Grasshopper} interface for {CitySim}},
		url = {https://infoscience.epfl.ch/record/228832?ln=en},
		booktitle = {Proceedings of {PLEA} 2017},
		author = {Peronato, Giuseppe and Kämpf, Jérôme and Rey, Emmanuel and Andersen, Marilyne},
		year = {2017}
	}


License
---------------------
GHCitySim: set of Grasshopper components for interfacing with CitySim, started by Giuseppe Peronato  
Copyright (c) 2016-2018, Ecole polytechnique fédérale de Lausanne (EPFL)  
Laboratory of Integrated Performance in Design (LIPID)  

Further development conducted at Uppsala University, Sweden  
Division of Construction Engineering, 2019  
Developer: Giuseppe Peronato, giuseppe.peronato[at]angstrom.uu.se  

GHCitySim is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version. 
 
GHCitySim is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License along with GHCitySim; If not, see <http://www.gnu.org/licenses/>.
 
@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


Useful links
---------------------
[CitySim webpage ](http://citysim.epfl.ch)


Contributors(a-z):
---------------------
[Aymeric Delmas](https://github.com/AymericDelmas)

[Giuseppe Peronato](https://github.com/gperonato)


Acknowledgments
---------------------
These components have been developed in the framework of the [ACTIVE INTERFACES](http://www.activeinterfaces.ch) research project, which is part of the National Research Programme "Energy Turnaround" (NRP 70) of the Swiss National Science Foundation (SNSF). Further information on the National Research Programme can be found at www.nrp70.ch.
