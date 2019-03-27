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
        model_start_date : str
            date of beginning of model fmt: mm-dd-yyyy
        output_files : dict
            dictionary of model output files, valid keys
            are "hds", "cbc", and "ucn"

            example
            >>> output_files = {"hds" : "Lucerne_head.out",
            >>>                 "cbc" : "Lucerne_cbc.out"}

        model_ws : str
            optional model workspace parameter, useful if
            all model files are in the same directory
        version : str
            modflow version ex. "mf2005", "mf6", "mfnwt"

    Notes
    -----
    usage
    >>> from gwwebflow import GwWebFlow
    >>> gwweb = GwWebFlow("mojave.nam", "mojave.ref.txt", "01-4002", "01-01-1931")
    >>> gwweb.create_netcdf_input_file()

    """
    def __init__(self, namfile, reference_file, report_id,
                 model_start_date, output_files=None, model_ws="",
                 version='mf2005'):

        self.namefile = os.path.split(namfile)[-1]
        self.reference = reference_file
        self.output_files = output_files
        self.report_id = report_id
        self.start_date = model_start_date
        self.model_ws = model_ws

        self.model = fp.modflow.Modflow.load(os.path.join(model_ws,
                                                          self.namefile),
                                             model_ws=self.model_ws,
                                             version=version,
                                             check=False)

        self.model.dis.start_datetime = model_start_date
        self.model.modelgrid.read_usgs_model_reference_file(
                os.path.join(self.model_ws,
                             self.reference))

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


if __name__ == "__main__":
    pass
