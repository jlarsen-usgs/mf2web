from flopy.pakbase import Package
import sys


class Modflow88Sip(Package):
    """
    Class to read modflow88 Strongly implicit proceedure
     package input.

    See modflow 88 documentation....
    """

    def __init__(self, model, mxiter=50, nparm=5, accl=1.,
                 hclose=0.01, ipcalc=1, wseed=0.98, iprsip=10):

        unitnumber = 9
        filenames = [None]
        name = [Modflow88Sip.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "sip"

        super(Modflow88Sip, self).__init__(model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        self.mxiter = mxiter
        self.nparm = nparm
        self.accl = accl
        self.hclose = hclose
        self.ipcalc = ipcalc
        self.wseed = wseed
        self.iprsip = iprsip
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
        bas : Modflow88Sip object
            Modflow88Sip object (of type :class:`mf2web.mf88.Modflow88Sip`)
        """

        if model.verbose:
            sys.stdout.write('loading bas6 package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        t = f.readline().strip().split()
        mxiter, nparm = int(t[0]), int(t[1])

        t = f.readline().strip().split()
        accl, hclose, ipcalc = float(t[0]), float(t[1]), int(t[2])

        wseed = 0.98
        iprsip = 10
        if ipcalc == 0:
            wseed, iprsip = float(t[3]), int(t[4])

        return Modflow88Sip(model, mxiter, nparm, accl, hclose,
                            ipcalc, wseed, iprsip)

    @staticmethod
    def ftype():
        return "SIP"