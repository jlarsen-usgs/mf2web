from flopy.mbase import BaseModel
from flopy.discretization.modeltime import ModelTime
from flopy.discretization import StructuredGrid
import mf2web
from ..utils import parse_scriptfile
import os


class Modflow88(BaseModel):
    """
    MODFLOW 88 model object

    Parameters
    ----------

    modelname : str
        name of the model

    scriptfile_ext : str
        extension of the scriptfile

    exe_name : basestring
        name of the modflow executable

    model_ws : str
        path to the model workspace

    verbose : bool
        is mf88 going to be verbose?
    """
    def __init__(self, modelname="modflowtest", scriptfile_ext=".sh",
                 exe_name="mf88.exe", model_ws=".", verbose=False,
                 lenuni=0, **kwargs):

        super(Modflow88, self).__init__(modelname, scriptfile_ext,
                                        exe_name, model_ws, structured=True,
                                        verbose=verbose, **kwargs)

        self.__LENUNI = {'u': 0, "f": 1, "m": 2, "c": 3}
        self.array_format = "modflow"
        self.load_fail = False
        self._next_ext_unit = 91

        self.external_path = "."
        self.verbose = verbose

        self.hext = 'hds'
        self.cext = 'cbc'

        self.hpth = None
        self.cpath = None

        self._lenuni = lenuni
        if isinstance(lenuni, str):
            self._lenuni = self.__LENUNI[lenuni.lower()[0]]

        # Create a dictionary to map package with the iunit location.
        # This is used for loading models.
        self.mfnam_packages = {
            "BAS": mf2web.mf88.Modflow88Bas,
            0: mf2web.mf88.Modflow88Bcf,
            1: mf2web.mf88.Modflow88Wel,
            2: mf2web.mf88.Modflow88Drn,
            3: mf2web.mf88.Modflow88Riv,
            4: mf2web.mf88.Modflow88Evt,
            5: mf2web.mf88.Modflow88Hfb,
            6: mf2web.mf88.Modflow88Ghb,
            7: mf2web.mf88.Modflow88Rch,
            8: mf2web.mf88.Modflow88Sip,
            9: None,
            10: mf2web.mf88.Modflow88Sor,
            11: mf2web.mf88.Modflow88Oc,
            12: None,
            13: None,
            14: None,
            15: None,
            16: None,
            17: None,
            18: None,
            19: None,
            20: None,
            21: None,
            22: None,
            23: None
        }

    def __repr__(self):
        nrow, ncol, nlay, nper = self.get_nrow_ncol_nlay_nper()
        s = ""
        if nrow is not None:
            # structured case
            s = ('MODFLOW-88 {} layer(s) {} row(s) {} column(s) '
                 '{} stress period(s)'.format(nlay, nrow, ncol, nper))
        return s

    @property
    def lenuni(self):
        return self._lenuni

    @lenuni.setter
    def lenuni(self, lenuni):
        if isinstance(lenuni, str):
            self._lenuni = self.__LENUNI[lenuni.lower()[0]]
        else:
            self._lenuni = lenuni

        if self.bas is not None:
            self.bas.lenuni = self._lenuni

    @property
    def modeltime(self):
        # build model time
        data_frame = {'perlen': self.bas.perlen.array,
                      'nstp': self.bas.nstp.array,
                      'tsmult': self.bas.tsmult.array}
        self._model_time = ModelTime(data_frame,
                                     self.bas.itmuni_dict[self.dis.itmuni],
                                     self.bas.start_datetime)
        return self._model_time

    @property
    def modelgrid(self):
        if not self._mg_resync:
            return self._modelgrid

        if self.bas is not None:
            ibound = self.bas.ibound.array
        else:
            ibound = None

        self._modelgrid = StructuredGrid(self.bcf.delc.array,
                                         self.bcf.delr.array,
                                         None,
                                         None, ibound,
                                         self.bas.lenuni,
                                         proj4=self._modelgrid.proj4,
                                         epsg=self._modelgrid.epsg,
                                         xoff=self._modelgrid.xoffset,
                                         yoff=self._modelgrid.yoffset,
                                         angrot=self._modelgrid.angrot)
        # resolve offsets
        xoff = self._modelgrid.xoffset
        if xoff is None:
            if self._xul is not None:
                xoff = self._modelgrid._xul_to_xll(self._xul)
            else:
                xoff = 0.0
        yoff = self._modelgrid.yoffset
        if yoff is None:
            if self._yul is not None:
                yoff = self._modelgrid._yul_to_yll(self._yul)
            else:
                yoff = 0.0
        self._modelgrid.set_coord_info(xoff, yoff, self._modelgrid.angrot,
                                       self._modelgrid.epsg,
                                       self._modelgrid.proj4)
        return self._modelgrid

    @modelgrid.setter
    def modelgrid(self, value):
        self._modelgrid = value

    @property
    def solver_tols(self):
        if self.sor is not None:
            return self.sor.hclose,-999
        elif self.sip is not None:
            return self.sip.hclose, -999
        return None

    @property
    def nlay(self):
        if (self.bas):
            return self.bas.nlay
        else:
            return 0

    @property
    def nrow(self):
        if (self.bas):
            return self.bas.nrow
        else:
            return 0

    @property
    def ncol(self):
        if (self.bas):
            return self.bas.ncol
        else:
            return 0

    @property
    def nper(self):
        if (self.bas):
            return self.bas.nper
        else:
            return 0

    @property
    def ncpl(self):
        if (self.bas):
            return self.bas.nrow * self.bas.ncol
        else:
            return 0

    @property
    def nrow_ncol_nlay_nper(self):
        return self.nrow, self.ncol, self.nlay, self.nper

    def _set_name(self, value):
        pass

    def write_name_file(self):
        pass

    def set_model_units(self, iunit0=None):
        pass

    def load_results(self, **kwargs):
        pass

    @staticmethod
    def load(f, exe_name='mf88.exe', verbose=False,
             model_ws='.', forgive=True, lenuni=0):
        """
        Load an existing MODFLOW model.

        Parameters
        ----------
        f : str
            Path to MODFLOW script file to load.
        exe_name : str, optional
            MODFLOW executable name. Default 'mf2005.exe'.
        verbose : bool, optional
            Show messages that can be useful for debugging. Default False.
        model_ws : str
            Model workspace path. Default '.' or current directory.
        forgive : bool, optional
            Option to raise exceptions on package load failure, which can be
            useful for debugging. Default False.
        lenuni : int, str
            length unit for model. Not in mf88 but useful for exporting


        Returns
        -------
        ml : Modflow object

        Examples
        --------

        >>> import mf2web
        >>> ml = mf2web.mf88.Modflow88.load('model.sh')

        """
        scriptfile_path = os.path.join(model_ws, f)
        modelname = os.path.splitext(os.path.basename(f))[0]

        if verbose:
            print('\nCreating new model with name: {}\n{}\n'
                  .format(modelname, 50 * '-'))

        ml = Modflow88(modelname, exe_name=exe_name, verbose=verbose,
                       model_ws=model_ws)

        # create utility to parse the script file!
        ext_unit_dict = parse_scriptfile(scriptfile_path, model_ws)

        basfile = ext_unit_dict.pop("BAS")
        pak = ml.mfnam_packages["BAS"]
        bas = pak.load(os.path.join(model_ws, basfile.filename), ml,
                       ext_unit_dict=ext_unit_dict)

        # get active packages!
        ml.lenuni = lenuni
        iunit = bas.iunit

        for pos, unit in enumerate(iunit):

            if unit > 0:
                if forgive:
                    try:
                        pak = ml.mfnam_packages[pos]
                        fname = ext_unit_dict.pop(unit)
                        pak.load(os.path.join(model_ws, fname.filename), ml,
                                 ext_unit_dict=ext_unit_dict)
                    except Exception as e:
                        print("Package load error: iunit position {}".format(pos + 1))

                else:
                    pak = ml.mfnam_packages[pos]
                    if pak is None:
                        print("iunit position not implemented {}".format(pos + 1))
                        continue
                    fname = ext_unit_dict.pop(unit)
                    pak.load(os.path.join(model_ws, fname.filename), ml,
                             ext_unit_dict=ext_unit_dict)

            else:
                pass

        ml._modelgrid = StructuredGrid(ml.bcf.delc.array,
                                       ml.bcf.delr.array,
                                       None,
                                       None, ml.bas.ibound,
                                       ml.bas.lenuni)

        return ml
