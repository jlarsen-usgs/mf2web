from flopy.pakbase import Package
from flopy.utils import MfList, create_empty_recarray
from ..utils import mflist_reader
import numpy as np
import sys


class Modflow88Hfb(Package):
    """
    Modflow88Hfb package class for HFB package

    see modflow 88 manual for documentation
    """

    def __init__(self, model, hfb_data=None):

        unitnumber = 6
        filenames = [None]
        name = [Modflow88Hfb.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "drn"

        super(Modflow88Hfb, self).__init__(model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        self.dtype = self.get_default_dtype()

        self.hfb_data = Modflow88Hfb.get_empty(len(hfb_data))
        for ibnd, t in enumerate(hfb_data):
            self.hfb_data[ibnd] = tuple(t)

        self.parent.add_package(self)

    @staticmethod
    def get_empty(ncells=0, aux_names=None, structured=True):
        # get an empty recarray that corresponds to dtype
        dtype = Modflow88Hfb.get_default_dtype(structured=structured)
        if aux_names is not None:
            dtype = Package.add_to_dtype(dtype, aux_names, np.float32)
        return create_empty_recarray(ncells, dtype, default_value=-1.0E+10)

    @staticmethod
    def get_default_dtype(structured=True):

        return np.dtype([("k", np.int), ("i0", np.int),
                         ("j0", np.int), ("i1", np.int),
                         ("j1", np.int), ("hydchr", np.float32)])

    @staticmethod
    def load(f, model, nlay=1, ext_unit_dict=None):
        """
        Method to load a modflow Drain package

        Parameters
        ----------
        f : str
            filename
        model : mf88 object
        nlay : int
            number of layers
        ext_unit_dict : dict
            Dictionary of unit and file names

        Returns
        -------
            Modflow88Drn object
        """

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        t = f.readline().strip().split()
        nhfb = int(t[0])

        data = []
        for k in range(nlay):
            t = f.readline().strip().split()
            nbrlay = int(t[0])
            for rec in range(nbrlay):
                t = f.readline().strip().split()
                i0, j0, i1, j1 = [int(i) for i in t[0:4]]
                hydchr = float(t[4])
                data.append((k, i0 - 1, j0 - 1,
                             i1 - 1, j1 - 1, hydchr))

        recarray = Modflow88Hfb.get_empty(nhfb)
        for ix, rec in enumerate(data):
            recarray[ix] = rec

        return Modflow88Hfb(model, recarray)

    @staticmethod
    def ftype():
        return "HFB"