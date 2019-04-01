from flopy.pakbase import Package
from flopy.utils import Util2d, Transient2d
import numpy as np
import sys


class Modflow88Rch(Package):
    """
    Class to read modflow 88 recharge
    package

    see modflow 88 manual for documentation...
    """
    def __init__(self, model, nrchop=1, irchcb=90,
                 rech=0., irch=0.):

        unitnumber = 8
        filenames = [None, None]
        name = [Modflow88Rch.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "rch"

        super(Modflow88Rch, self).__init__(self, model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper

        self.nrchop = nrchop

        self.rech = Transient2d(model, (nrow, ncol), np.float,
                                rech, name='rech')

        self.irch = None
        if self.nrchop == 2:
            self.irch = Transient2d(model, (nrow, ncol), np.int,
                                    irch, name='irch')
        self.parent.add_package(self)

    @staticmethod
    def load(f, model, nper=1, nrow=1, ncol=1, ext_unit_dict=None):
        """

        Parameters
        ----------
        f : str
            filename
        model : mf88 object
        nper : int
            number of stress periods
        nrow : int
            number of model rows
        ncol : int
            number of model columns
        ext_unit_dict : dict
            Dictionary of unit and file names

        Returns
        -------
            Modflow88Rch object
        """

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        t = f.readline().strip().split()
        nrchop, irchcb = int(t[0]), int(t[1])

        rech = {}
        irch = {}

        for per in range(nper):
            t = f.readline().strip().split()
            inrech, inirech = int(t[0]), int(t[1])

            if inrech < 0:
                rech[per] = rech[per - 1]

            else:
                arr = Util2d.load(f, model, (nrow, ncol), np.float, 'rech',
                                  ext_unit_dict)

                rech[per] = arr

            if nrchop == 2:
                if inirech < 0:
                    irch[per] = irch[per - 1]

                else:
                    arr = Util2d.load(f, model, (nrow, ncol), np.int, "irch",
                                      ext_unit_dict)

                    irch[per] = arr

        return Modflow88Rch(model, nrchop, irchcb, rech, irch)

    @staticmethod
    def ftype():
        return "RCH"