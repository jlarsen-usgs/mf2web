# mf2web
A collection of tools to export MODFLOW models for web display using netcdf


## Dependancies
mf2web uses FloPy and pyGSFLOW to export models to netcdf, please install these packages before installing mf2web

flopy: https://github.com/modflowpy/flopy/tree/master

pyGSFLOW: https://github.com/pygsflow/pygsflow

## Usage

An example script:

```
from mf2web import GwWebFlow
import os

iws = r".\SIR2014-5052\input\GSFLOW COUPLED MODEL\

# this can be a modflow nam file or gsflow control file
nam = os.path.join(iws, "SRPgsf_withAni.control")

# usgs model reference file relative to input workspace
reference = r"..\..\SRP.usgs.model.reference"

# output file directory relative to input workspace
ows = r"..\..\output\GSFLOW COUPLED MODEL"
cbc = os.path.join(ows, "SRPgsf.bud")
hed = os.path.join(ows, "SRPgsf.fhd")

ipds = "2015-5052"

gwweb = GwWebFlow(nam, reference, ipds,
                  scenario="0",
                  output_files=("FHD": hed,
                                "CBC": cbc},
                  model_ws=iws,
                  length_multiplier=0.3048)
                  
gwweb.create_netcdf_input_file()
gwweb.create_netcdf_output_file()
```

### Note:
The USGS model refence file must include these parameters:

xll          509549.09    # can be xul in lieu of xll
yll          4238865.14   # can be yul in lieu of yll
rotation     0
length_unit  feet
time_units   days
start_date   10/1/1974
start_time   00:00:00
model        gsflow
epsg 26910                # epsg is optional 
proj4 +proj=utm +zone=10 +ellps=GRS80 +datum=NAD83 +units=m +no_defs  


