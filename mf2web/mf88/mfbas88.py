from flopy.pakbase import Package
from flopy.utils import Util3d, Util2d
import numpy as np
import sys


class Modflow88Bas(Package):
    """
    Class to read modflow88 Basic package input.

    See modflow 88 documentation....
    """

    def __init__(self, model, nlay=1, nrow=1, ncol=1, nper=1,
                 itemuni=0, iunit=(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                 iapart=0, istrt=0, ibound=1, hnoflo=-9999.,
                 shead=1., perlen=1., nstp=1, tsmult=1.,
                 start_datetime="1-1-1970"):

        unitnumber = 99
        filenames = [None]
        name = [Modflow88Bas.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "bas"

        super(Modflow88Bas, self).__init__(model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        self.url = 'bas.htm'
        self.nlay = nlay
        self.nrow = nrow
        self.ncol = ncol
        self.nper = nper
        self.itemuni = itemuni
        self.lenuni = 0
        self.iunit = iunit
        self.iapart = iapart
        self.istrt = istrt
        self.ibound = Util3d(model, (nlay, nrow, ncol), np.int32, ibound,
                             name='ibound', locat=self.unit_number[0])
        self.hnoflo = hnoflo
        self.shead = Util3d(model, (nlay, nrow, ncol), np.float32, shead,
                            name='shead', locat=self.unit_number[0])

        self.perlen = Util2d(model, (self.nper,), np.float32, perlen,
                             name="perlen")
        self.nstp = Util2d(model, (self.nper,), np.int32, nstp,
                           name='nstp')

        self.tsmult = Util2d(model, (self.nper,), np.float32, tsmult,
                             name='tsmult')

        self.start_datetime = start_datetime
        self.itmuni_dict = {0: "undefined", 1: "seconds", 2: "minutes",
                            3: "hours", 4: "days", 5: "years"}

        self.parent.add_package(self)

    @staticmethod
    def load(f, model, ext_unit_dict=None):
        """
        Load an existing package

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        ext_unit_dict : dict
            Dictionary of unit and file names

        Returns
        -------
        bas : Modflow88Bas object
            Modflow88Bas object (of type :class:`mf2web.mf88.Modflow88Bas`)
        """

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        heading = f.readline()
        heading += f.readline()

        line = f.readline()[0:50]
        nlay, nrow, ncol, nper, itemuni = [int(i) for i in line.split()]

        line = f.readline()[0:72]
        i0 = 0
        i1 = 3
        iunit = []
        while True:
            try:
                unit = int(line[i0:i1])
                if unit < 0:
                    unit = 0
                iunit.append(unit)
                i0 += 3
                i1 += 3
            except ValueError:
                break

        iunit = tuple(iunit)

        line = f.readline()[0:20]
        iapart, istrt = [int(i) for i in line.split()]

        ibound = Util3d.load(f, model, (nlay, nrow, ncol), np.int32, "ibound",
                             ext_unit_dict)

        hnoflo = float(f.readline()[0:10])


        shead = Util3d.load(f, model, (nlay, nrow, ncol), np.float32, "shead",
                            ext_unit_dict)

        perlen = []
        nstp = []
        tsmult = []
        for k in range(nper):
            line = f.readline()[0:30]
            a1, a2, a3 = line.split()
            a1 = float(a1)
            a2 = int(a2)
            a3 = float(a3)
            perlen.append(a1)
            nstp.append(a2)
            tsmult.append(a3)

        return Modflow88Bas(model, nlay, nrow, ncol, nper, itemuni,
                            iunit, iapart, istrt, ibound, hnoflo,
                            shead, perlen, nstp, tsmult)

    @staticmethod
    def ftype():
        return "BAS"