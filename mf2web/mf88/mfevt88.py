from flopy.pakbase import Package
from flopy.utils import Util2d, Transient2d
import numpy as np
import sys


class Modflow88Evt(Package):
    """
    lass to read modflow 88 evapotranspiration
    package

    see modflow 88 manual for documentation...
    """
    def __init__(self, model, nevtop=1, ievtcb=90, surf=1.,
                 evtr=1., exdp=1., ievt=1.):

        unitnumber = 5
        filenames = [None, None]
        name = [Modflow88Evt.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "rch"

        super(Modflow88Evt, self).__init__(self, model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper

        self.nevtop = nevtop
        self.surf = Transient2d(model, (nrow, ncol), np.float,
                                surf, name='surf')

        self.evtr = Transient2d(model, (nrow, ncol), np.float,
                                evtr, name='evtr')

        self.exdp = Transient2d(model, (nrow, ncol), np.float,
                                exdp, name='exdp')

        self.ievt = None
        if nevtop == 2:
            self.ievt = Transient2d(model, (nrow, ncol), np.float,
                                    ievt, name='ievt')
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
        nevtop, ievtcb = int(t[0]), int(t[1])

        surf = {}
        evtr = {}
        exdp = {}
        ievt = {}
        for per in range(nper):

            t = f.readline().strip().split()

            insurf, inevtr, inexdp = int(t[0]), int(t[1]), int(t[2])

            inievt = -999
            if nevtop == 2:
                inievt = int(t[3])

            if insurf < 0:
                surf[per] = surf[per - 1]
            else:
                surf[per] = Util2d.load(f, model, (nrow, ncol), np.float, 'surf',
                                        ext_unit_dict)

            if inevtr < 0:
                evtr[per] = evtr[per - 1]
            else:
                evtr[per] = Util2d.load(f, model, (nrow, ncol), np.float, 'evtr',
                                        ext_unit_dict)

            if inexdp < 0:
                exdp[per] = exdp[per - 1]
            else:
                exdp[per] = Util2d.load(f, model, (nrow, ncol), np.float, 'exdp',
                                        ext_unit_dict)

            if nevtop == 2:
                if inievt < 0:
                    ievt[per] = ievt[per - 1]
                else:
                    ievt[per] = Util2d.load(f, model, (nrow, ncol), np.float, 'ievt',
                                            ext_unit_dict)

        return Modflow88Evt(model, nevtop, ievtcb, surf, evtr, exdp, ievt)

    @staticmethod
    def ftype():
        return "EVT"