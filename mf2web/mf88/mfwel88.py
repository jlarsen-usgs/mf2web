from flopy.pakbase import Package
from flopy.utils import MfList, create_empty_recarray
from ..utils import mflist_reader
import numpy as np
import sys


class Modflow88Wel(Package):
    """
    Modflow88Wel package class for River package

    see modflow 88 manual for documentation
    """

    def __init__(self, model, iwelcb=None, stress_period_data=None):

        unitnumber = 2
        filenames = [None]
        name = [Modflow88Wel.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "wel"

        super(Modflow88Wel, self).__init__(model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        self.dtype = self.get_default_dtype()
        self.stress_period_data = MfList(self, stress_period_data)
        self.parent.add_package(self)

    @staticmethod
    def get_empty(ncells=0, aux_names=None, structured=True):
        # get an empty recarray that corresponds to dtype
        dtype = Modflow88Wel.get_default_dtype(structured=structured)
        if aux_names is not None:
            dtype = Package.add_to_dtype(dtype, aux_names, np.float32)
        return create_empty_recarray(ncells, dtype, default_value=-1.0E+10)

    @staticmethod
    def get_default_dtype(structured=True):

        return np.dtype([("k", np.int), ("i", np.int),
                         ("j", np.int), ("flux", np.float32)])

    @staticmethod
    def load(f, model, nper=1, ext_unit_dict=None):
        """
        Method to load a modflow River package

        Parameters
        ----------
        f : str
            filename
        model : mf88 object
        nper : int
            number of stress periods

        Returns
        -------
            Modflow88Wel object
        """

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        t = f.readline().strip().split()
        mxwel, iwelcb = int(t[0]), int(t[1])

        stress_period_data = mflist_reader(f, Modflow88Wel, nper)

        return Modflow88Wel(model, iwelcb, stress_period_data)

    @staticmethod
    def ftype():
        return "WEL"
