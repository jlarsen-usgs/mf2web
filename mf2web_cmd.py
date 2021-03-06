import argparse
from mf2web import GwWebFlow


desc = "Create netcdf files for GwWebFlow from MODFLOW models"

parser = argparse.ArgumentParser(prog="gwwebflow.py", description=desc)
parser.add_argument("-n", "--nam", nargs=1, type=str, required=True,
                    help="Modflow name file")
parser.add_argument("-r", "--ref", nargs=1, type=str, required=True,
                    help="USGS reference file for model archival")
parser.add_argument("-i", "--ipds", nargs=1, type=str, required=True,
                    help="USGS IPDS ID number")
parser.add_argument("-s", "--scenario", nargs=1, type=str,
                    help="Model Scenario")
parser.add_argument("-m", "--mult", nargs=1, type=float,
                    help="model grid length multiplier")
parser.add_argument("--hds", nargs=1, type=str,
                    help="Model binary head file")
parser.add_argument("--fhd", nargs=1, type=str,
                    help="ASCII formatted head file")
parser.add_argument("--ucn", nargs=1, type=str,
                    help="Seawat binary ucn output file")
parser.add_argument("--cbc", nargs=1, type=str,
                    help="Model binary cell budget file")
parser.add_argument("--ws", nargs=1, type=str,
                    help="Model directory path")

args = parser.parse_args()

output_dict = {}
if args.ucn is not None:
    output_dict["UCN"] = args.ucn[0]
if args.hds is not None:
    output_dict["HDS"] = args.hds[0]
if args.cbc is not None:
    output_dict["CBC"] = args.cbc[0]
if args.fhd is not None:
    output_dict["FHD"] = args.fhd[0]

if not output_dict:
    output_dict = None

ws = ""
if args.ws is not None:
    ws = args.ws[0]

scenario = "0"
if args.scenario is not None:
    scenario = args.scenario[0]

length_multiplier = 1
if args.mult is not None:
    length_multiplier = args.mult[0]

nam = args.nam[0]
ref = args.ref[0]
ipds = args.ipds[0]

version = 'mf2005'
if version is not None:
    version = args.version[0]

gwweb = GwWebFlow(nam, ref, ipds, scenario=scenario,
                  output_files=output_dict,
                  model_ws=ws,
                  length_multiplier=length_multiplier)

gwweb.create_netcdf_input_file()
gwweb.create_netcdf_output_file()