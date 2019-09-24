import os
import flopy as fp
import numpy as np
from .seawat import Seawat
from .mf88 import Modflow88
try:
    import gsflow
except ImportError:
    gsflow = None
    print("Install pyGSFLOW for gsflow capabilities")
    print("https://github.com/usgs-pygsflow/pygsflow")


class GwWebFlow(object):
    """
    Class object to create input and output from
    modflow models using flopy

    Parameters
    ----------
        namfile : str
            modflow name file name or gsflow control file
        reference_file : str
            usgs model refence file for archiving
        report_id : str
            usgs ipds number
        output_files : dict
            dictionary of model output files, valid keys
            are "hds", "cbc", and "ucn"

            example
            >>> output_files = {"hds" : "Lucerne_head.out",
            >>>                 "cbc" : "Lucerne_cbc.out"}

        model_ws : str
            optional model workspace parameter, useful if
            all model files are in the same directory

        length_multiplier : float
            optional model length conversion factor
    Notes
    -----
    usage
    >>> from mf2web import GwWebFlow
    >>> gwweb = GwWebFlow("mojave.nam", "mojave.ref.txt", "01-4002")
    >>> gwweb.create_netcdf_input_file()

    """
    LENUNI = {}
    ITEMUNI = {}
    VERSION = {}

    def __init__(self, namfile, reference_file, report_id, scenario="0",
                 output_files=None, model_ws="", length_multiplier=None):

        self.namefile = os.path.split(namfile)[-1]
        self.reference = reference_file
        self.output_files = output_files
        self.report_id = report_id
        self.scenario = scenario
        self.model_ws = model_ws
        self.xll = None
        self.yll = None
        self.xul = None
        self.yul = None
        self.rotation = None
        self.length_multiplier = length_multiplier
        self.length_unit = None
        self.time_unit = None
        self.start_date = None
        self.start_time = None
        self.version = 'mf2005'
        self.proj4 = None
        self.epsg = None
        self._read_usgs_model_reference_file()

        if self.version == "seawat":
            # call mf2web.seawat.Seawat b/c modelgrid.idomain broken in flopy seawat
            self.model = Seawat.load(os.path.join(self.model_ws,
                                                  self.namefile),
                                      model_ws=self.model_ws,
                                      version=self.version)

        elif self.version == "mf6":
            raise NotImplementedError()

        elif self.version == "mf88":
            self.model = Modflow88.load(os.path.join(self.model_ws,
                                                     self.namefile),
                                        model_ws=model_ws,
                                        lenuni=self.length_unit)

        elif self.version in ("mfowhm", "mf96"):
            err = "{} is not yet supported".format(self.version)
            raise NotImplementedError(err)

        elif self.version == "gsflow":
            if gsflow is None:
                raise ImportError("pygsflow must be installed for GSFLOW models")

            self.model = gsflow.GsflowModel.load_from_file(os.path.join(model_ws,
                                                                        self.namefile))

        else:
            # method for modflow-2000, 2005, and nwt models
            self.model = fp.modflow.Modflow.load(os.path.join(model_ws,
                                                              self.namefile),
                                                 model_ws=self.model_ws,
                                                 version=self.version,
                                                 check=False)

        if self.version == "mf88":
            self.model.bas.start_datetime = self.start_date + " " + self.start_time

        elif self.version == "gsflow":
            self.model.mf.dis.start_datetime = self.start_date + " " + self.start_time
        else:
            self.model.dis.start_datetime = self.start_date + ' ' + self.start_time

        if self.length_multiplier is not None:
            if self.version == "mf88":
                delr = self.model.bcf.delr.array * length_multiplier
                delc = self.model.bcf.delc.array * length_multiplier
                nrow, ncol, nlay, nper = self.model.nrow_ncol_nlay_nper

                self.model.bcf.delr = fp.utils.Util2d(self.model, (ncol,), np.float32,
                                                      delr, name="delr", locat=self.model.dis.unit_number[0])

                self.model.bcf.delc = fp.utils.Util2d(self.model, (nrow,), np.float32,
                                                      delc, name="delr", locat=self.model.dis.unit_number[0])

            elif self.version == "gsflow":
                delr = self.model.mf.dis.delr.array * length_multiplier
                delc = self.model.mf.dis.delc.array * length_multiplier

                self.model.mf.dis.delr = fp.utils.Util2d(self.model.mf, (self.model.mf.dis.ncol,),
                                                         np.float32, delr, name="delr",
                                                         locat=self.model.mf.dis.unit_number[0])

                self.model.mf.dis.delc = fp.utils.Util2d(self.model.mf, (self.model.mf.dis.nrow,),
                                                         np.float32, delc, name="delr",
                                                         locat=self.model.mf.dis.unit_number[0])

            else:
                delr = self.model.dis.delr.array * length_multiplier
                delc = self.model.dis.delc.array * length_multiplier

                self.model.dis.delr = fp.utils.Util2d(self.model, (self.model.dis.ncol,), np.float32,
                                                      delr, name="delr", locat=self.model.dis.unit_number[0])

                self.model.dis.delc = fp.utils.Util2d(self.model, (self.model.dis.nrow,), np.float32,
                                                      delc, name="delr", locat=self.model.dis.unit_number[0])

        if (self.xll, self.yll) != (None, None):
            if self.version == "gsflow":
                self.model.mf.modelgrid.set_coord_info(self.xll, self.yll,
                                                       self.rotation,
                                                       self.epsg,
                                                       self.proj4)
            else:
                self.model.modelgrid.set_coord_info(self.xll, self.yll,
                                                    self.rotation,
                                                    self.epsg, self.proj4)

            if self.version == "seawat":
                self.model.modelgrid.set_coord_info(self.xll, self.yll,
                                                    self.rotation,
                                                    self.epsg, self.proj4)
                if self.model._mf is not None:
                    self.model._mf.modelgrid.set_coord_info(self.xll, self.yll,
                                                            self.rotation,
                                                            self.epsg,
                                                            self.proj4)

                if self.model._mt is not None:
                    self.model._mt.modelgrid.set_coord_info(self.xll, self.yll,
                                                            self.rotation,
                                                            self.epsg,
                                                            self.proj4)

        if (self.xul, self.yul) != (None, None):
            if self.rotation is not None:
                if self.version == "gsflow":
                    self.model.mf.modelgrid._angrot = self.rotation
                else:
                    self.model.modelgrid._angrot = self.rotation

            if self.version == "seawat":
                if self.model._mf is not None:
                    if self.rotation is not None:
                        self.model._mf.modelgrid._angrot = self.rotation

                    self.model._modelgrid._xoff = self.model._modelgrid._xul_to_xll(self.xul)
                    self.model._modelgrid._yoff = self.model._modelgrid._yul_to_yll(self.yul)
                    self.model._modelgrid.epsg = self.epsg
                    self.model._modelgrid.proj4 = self.proj4
                    self.model._modelgrid._require_cache_updates()

                    self.model._mf.modelgrid._xoff = self.model.modelgrid._xul_to_xll(self.xul)
                    self.model._mf.modelgrid._yoff = self.model.modelgrid._yul_to_yll(self.yul)
                    self.model._mf.modelgrid.epsg = self.epsg
                    self.model._mf.modelgrid.proj4 = self.proj4
                    self.model._mf.modelgrid._require_cache_updates()

                if self.model._mt is not None:
                    if self.rotation is not None:
                        self.model._mt.modelgrid._angrot = self.rotation

                    self.model._mt.modelgrid._xoff = self.model.modelgrid._xul_to_xll(self.xul)
                    self.model._mt.modelgrid._yoff = self.model.modelgrid._yul_to_yll(self.yul)
                    self.model._mt.modelgrid.epsg = self.epsg
                    self.model._mt.modelgrid.proj4 = self.proj4
                    self.model._mt.modelgrid._require_cache_updates()

            elif self.version == "gsflow":
                self.model.mf.modelgrid._xoff = self.model.mf.modelgrid._xul_to_xll(self.xul)
                self.model.mf.modelgrid._yoff = self.model.mf.modelgrid._yul_to_yll(self.yul)
                self.model.mf.modelgrid.epsg = self.epsg
                self.model.mf.modelgrid.proj4 = self.proj4
                self.model.mf.modelgrid._require_cache_updates()

    def create_netcdf_input_file(self):
        """
        Method that writes a netcdf input file from
        modflow model files
        """
        ncf_name = ".".join([self.report_id, self.scenario, "in", "nc"])
        if self.version == "gsflow":
            self.model.export_nc(ncf_name)
        else:
            self.model.export(ncf_name)

    def create_netcdf_output_file(self, masked_vals=[]):
        """
        Method that writes a netcdf output file from
        modflow model output files. Currently supports
        Seawat binary concentration files and modflow
        binary head files
        """
        if self.output_files is None:
            return

        if self.version == "mf88":
            raise NotImplementedError("output not yet implemented for mf88")

        ncf_name = ".".join([self.report_id, self.scenario, "out", "nc"])

        export_dict = {}
        for key, value in self.output_files.items():
            if key.upper() == "UCN":
                out = fp.utils.UcnFile(os.path.join(self.model_ws, value))
            elif key.upper() == "HDS":
                out = fp.utils.HeadFile(os.path.join(self.model_ws, value))
            elif key.upper() == "FHD":
                out = fp.utils.FormattedHeadFile(os.path.join(self.model_ws, value))
            elif key.upper() == "CBC":
                out = fp.utils.CellBudgetFile(os.path.join(self.model_ws, value))
            else:
                raise KeyError("Invalid output key: {}".format(key))

            export_dict[key.lower()] = out

        if self.version == "gsflow":
            fp.export.utils.output_helper(ncf_name, self.model.mf, export_dict,
                                          masked_vals=masked_vals)
        else:
            fp.export.utils.output_helper(ncf_name, self.model, export_dict,
                                          masked_vals=masked_vals)

    def _read_usgs_model_reference_file(self):
        """
        Method to parse data from a usgs model reference file
        and set it to the modflow model for netcdf creation
        """
        if os.path.exists(os.path.join(self.model_ws, self.reference)):
            with open(os.path.join(self.model_ws, self.reference)) as input:
                for line in input:
                    if len(line) > 1:
                        if line.strip()[0] != "#":
                            info = line.strip().split("#")[0].split()
                            if len(info) > 1:
                                data = ' '.join(info[1:])
                                if info[0].lower() == 'xll':
                                    self.xll = float(data)
                                elif info[0].lower() == 'yll':
                                    self.yll = float(data)
                                elif info[0].lower() == 'xul':
                                    self.xul = float(data)
                                elif info[0].lower() == 'yul':
                                    self.yul = float(data)
                                elif 'length' in info[0].lower():
                                    self.length_unit = data
                                elif 'time_unit' in info[0].lower():
                                    self.time_unit = data
                                elif info[0].lower() == 'rotation':
                                    self.rotation = float(data)
                                elif info[0].lower() == 'epsg':
                                    self.epsg = int(data)
                                elif info[0].lower() == 'proj4':
                                    self.proj4 = data
                                elif info[0].lower() == 'start_date':
                                    self.start_date = data
                                elif info[0].lower() == 'start_time':
                                    self.start_time = data
                                elif info[0].lower() == 'model':
                                    if "2005" in data.lower():
                                        self.version = "mf2005"
                                    elif "nwt" in data.lower():
                                        self.version = "mfnwt"
                                    elif "sea" in data.lower():
                                        self.version = "seawat"
                                    elif "6" in data.lower():
                                        self.version = "mf6"
                                    elif "2000" in data.lower():
                                        self.version = "mf2k"
                                    elif "88" in data.lower():
                                        self.version = "mf88"
                                    elif "gs" in data.lower():
                                        self.version = "gsflow"
                                    else:
                                        print("Warning, Unrecognised version: {}".format(data))
                                        print("Setting version to modflow-2005")
                                else:
                                    pass

            if (self.xll, self.yll, self.xul, self.yul) == (None, None, None, None):
                err = "Model xul and yul need to be supplied in reference file"
                raise AssertionError(err)

            if (self.epsg, self.proj4) == (None, None):
                err = "Model projection must be supplied via epsg code or proj4 string"
                raise AssertionError(err)

            if self.rotation is None:
                self.rotation = 0.

            if self.start_date is None:
                self.start_date = '1-1-1970'

            if self.start_time is None:
                self.start_time = "00:00:00"
