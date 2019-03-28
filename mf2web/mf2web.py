import os
import flopy as fp


class GwWebFlow(object):
    """
    Class object to create input and output from
    modflow models using flopy

    Parameters
    ----------
        namfile : str
            modflow name file name
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

    def __init__(self, namfile, reference_file, report_id,
                 output_files=None, model_ws=""):

        self.namefile = os.path.split(namfile)[-1]
        self.reference = reference_file
        self.output_files = output_files
        self.report_id = report_id
        self.model_ws = model_ws
        self.xll = None
        self.yll = None
        self.xul = None
        self.yul = None
        self.rotation = None
        self.length_unit = None
        self.time_unit = None
        self.start_date = None
        self.start_time = None
        self.version = 'mf2005'
        self.proj4 = None
        self.epsg = None
        self._read_usgs_model_reference_file()

        if self.version == "swtv4":
            pass

        elif self.version == "mf6":
            pass

        elif self.version in ("gsflow", "mfowhm"):
            err = "Gsflow and OWHM are not yet supported"
            raise NotImplementedError(err)

        else:
            self.model = fp.modflow.Modflow.load(os.path.join(model_ws,
                                                              self.namefile),
                                                 model_ws=self.model_ws,
                                                 version=self.version,
                                                 check=False)

        self.model.dis.start_datetime = self.start_date + ' ' + self.start_time

        if (self.xll, self.yll) != (None, None):
            self.model.modelgrid.set_coord_info(self.xll, self.yll, self.rotation,
                                                self.epsg, self.proj4)

        if (self.xul, self.yul) != (None, None):
            if self.rotation is not None:
                self.model.modelgrid._angrot = self.rotation

            self.model.modelgrid.set_coord_info(self.model.modelgrid._xul_to_xll(self.xul),
                                                self.model.modelgrid._yul_to_yll(self.yul),
                                                self.rotation,
                                                self.epsg,
                                                self.proj4)

    def create_netcdf_input_file(self):
        """
        Method that writes a netcdf input file from
        modflow model files
        """
        ncf_name = self.report_id + ".in.nc"
        self.model.export(ncf_name)

    def create_netcdf_output_file(self):
        """
        Method that writes a netcdf output file from
        modflow model output files. Currently supports
        Seawat binary concentration files and modflow
        binary head files
        """
        if self.output_files is None:
            return

        ncf_name = self.report_id + ".out.nc"

        export_dict = {}
        for key, value in self.output_files.items():
            if key.upper() == "UCN":
                out = fp.utils.UcnFile(os.path.join(self.model_ws, value))
            elif key.upper() == "HDS":
                out = fp.utils.HeadFile(os.path.join(self.model_ws, value))
            elif key.upper() == "CBC":
                out = fp.utils.CellBudgetFile(os.path.join(self.model_ws, value))
            else:
                raise KeyError("Invalid output key: {}".format(key))

            export_dict[key.lower()] = out

        fp.export.utils.output_helper(ncf_name, self.model, export_dict)

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
                                        self.version = "swtv4"
                                    elif "6" in data.lower():
                                        self.version = "mf6"
                                    else:
                                        print("Warning, Unrecognised version: {}".format(data))
                                        print("Setting version to mf2005")
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




if __name__ == "__main__":
    pass
