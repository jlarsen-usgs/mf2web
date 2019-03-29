from flopy.pakbase import Package
from flopy.utils import Util3d, Util2d, create_empty_recarray
import numpy as np
import sys


class Modflow88Riv(Package):
    """
    Modflow88Riv package class for River package

    see modflow 88 manual for documentation
    """
    def __init__(self, model, ipakcb=None, stress_period_data=None):

        unitnumber = [4]
        filenames = [None]
        name = [Modflow88Riv.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "riv"

        super(Modflow88Riv, self).__init__(self, model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

    @staticmethod
    def get_empty(ncells=0, aux_names=None, structured=True):
        # get an empty recarray that corresponds to dtype
        dtype = Modflow88Riv.get_default_dtype(structured=structured)
        if aux_names is not None:
            dtype = Package.add_to_dtype(dtype, aux_names, np.float32)
        return create_empty_recarray(ncells, dtype, default_value=-1.0E+10)

    @staticmethod
    def get_default_dtype(structured=True):

        return np.dtype([("k", np.int), ("i", np.int),
                         ("j", np.int), ("stage", np.float32),
                         ("cond", np.float32), ("rbot", np.float32)])

    @staticmethod
    def load(f, model, nper=1):
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
            Modflow88Riv object
        """
        ext_unit_dict = None

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        t = f.readline().strip()
        maxrivr = int(t[0])
        irivcb = int(t[1])

        stress_period_data = {}

        for per in range(nper):
            t = f.readline().split()
            itmp = int(t[0])

            if itmp < 0:
                recarray = stress_period_data[per - 1]
            else:
                recarray = Modflow88Riv.get_empty(itmp)
                for rec in range(itmp):
                    t = f.readline().split()
                    k = int(t[0]) - 1
                    i = int(t[1]) - 1
                    j = int(t[2]) - 1
                    stage = float(t[3])
                    cond = float(t[4])
                    rbot = float(t[5])

                    recarray[rec] = (k, i, j, stage, cond, rbot)

            stress_period_data[per] = recarray

        return Modflow88Riv(model, irivcb, stress_period_data)

    @staticmethod
    def ftype():
        return "RIV"