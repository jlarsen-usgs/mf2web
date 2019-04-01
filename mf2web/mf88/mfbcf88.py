from flopy.pakbase import Package
from flopy.utils import Util3d, Util2d
import numpy as np
import sys


class Modflow88Bcf(Package):
    """
    Class to read modflow 88 block centerd flow
    package

    see modflow 88 manual for documentation...
    """
    def __init__(self, model, iss=1, ibcfcb=90, laycon=(0,),
                 trpy=(1.,), delr=(1.,), delc=(1.,), sf1=1.,
                 tran=1., hy=1., bot=1., vcont=1., sf2=1.,
                 top=1.):

        unitnumber = [1, ibcfcb]
        filenames = [None, None]
        name = [Modflow88Bcf.ftype()]
        units = [unitnumber[0]]
        extra = [""]
        fname = [filenames[0]]
        extension = "bas"

        super(Modflow88Bcf, self).__init__(self, model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        self.iss = iss
        self.ibcfcb = ibcfcb
        self.laycon = laycon
        self.trpy = trpy
        self.delr = delr
        self.delc = delc
        self.sf1 = sf1
        self.tran = tran
        self.hy = hy
        self.bot = bot
        self.vcont = vcont
        self.sf2 = sf2
        self.top = top

        self.parent.add_package(self)

    @staticmethod
    def load(f, model, nlay=1, nrow=1, ncol=1, ext_unit_dict=None):
        """
        Load an existing package

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        nlay : int
            number of model layers
        nrow : int
            number of model rows
        ncol : int
            number of model columns
        ext_unit_dict : dict
            Dictionary of unit and file names

        Returns
        -------
        bcf : Modflow88Bas object
            Modflow88Bcf object (of type :class:`mf2web.mf88.Modflow88Bcf`)
        """

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        iss, ibcfcb = [int(i) for i in f.readline()[0:20].split()]

        line = f.readline()
        t = []
        istart = 0
        for k in range(nlay):
            lcode = line[istart:istart + 2]
            lcode = lcode.replace(' ', '0')
            t.append(lcode)
            istart += 2
        laycon = np.zeros(nlay, dtype=np.int32)
        for k in range(nlay):
            laycon[k] = int(t[k][1])

        trpy = Util2d.load(f, model, (nlay,), np.float32, 'trpy',
                           ext_unit_dict)

        delr = Util2d.load(f, model, (ncol,), np.float32, 'delr',
                           ext_unit_dict)

        delc = Util2d.load(f, model, (nrow,), np.float32, 'delc',
                           ext_unit_dict)

        sf1 = np.zeros((nlay, nrow, ncol))
        tran = np.zeros((nlay, nrow, ncol))
        hy = np.zeros((nlay, nrow, ncol))
        bot = np.zeros((nlay, nrow, ncol))
        top = np.zeros((nlay, nrow, ncol))

        if nlay > 1:
            vcont = np.zeros((nlay - 1, nrow, ncol))
        else:
            vcont = np.zeros((nlay, nrow, ncol))

        sf2 = np.zeros((nlay, nrow, ncol))

        for k in range(nlay):

            # sf1
            if iss != 0:
                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'sf1',
                                ext_unit_dict)
                sf1[k] = t

            # tran or hy and bot
            if ((laycon[k] == 0) or (laycon[k] == 2)):
                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'tran',
                                ext_unit_dict)
                tran[k] = t
            else:
                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'hy',
                                ext_unit_dict)
                hy[k] = t

                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'bot',
                                ext_unit_dict)
                bot[k] = t

            # vcont
            if k < (nlay - 1):
                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'vcont',
                                ext_unit_dict)
                vcont[k] = t

            # sf2
            if (iss != 0 and ((laycon[k] == 2) or (laycon[k] == 3))):
                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'sf2',
                                ext_unit_dict)
                sf2[k] = t

            if laycon[k] == 2 or laycon[k] == 3:
                t = Util2d.load(f, model, (nrow, ncol), np.float32, 'top',
                                ext_unit_dict)
                top[k] = t

        return Modflow88Bcf(model, iss, ibcfcb, laycon, trpy, delr, delc,
                            sf1, tran, hy, bot, vcont, sf2, top)

    @staticmethod
    def ftype():
        return "BCF"