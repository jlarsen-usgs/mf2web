from flopy.pakbase import Package
import sys


class Modflow88Sor(Package):
    """
    Class to read modflow88 Strongly implicit proceedure
     package input.

    See modflow 88 documentation....
    """

    def __init__(self, model, mxiter=50, accl=1.,
                 hclose=0.01, iprsor=0):

        unitnumber = 11
        filenames = [None]
        name = [Modflow88Sor.ftype()]
        units = [unitnumber]
        extra = [""]
        fname = [filenames[0]]
        extension = "sor"

        super(Modflow88Sor, self).__init__(self, model, extension=extension,
                                           name=name, unit_number=units, extra=extra,
                                           filenames=fname)

        self.mxiter = mxiter
        self.accl = accl
        self.hclose = hclose
        self.iprsor = iprsor
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
            sys.stdout.write('loading sor package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        t = f.readline().strip().split()
        mxiter= int(t[0])

        t = f.readline().strip().split()
        accl, hclose, iprsor = float(t[0]), float(t[1]), int(t[2])

        return Modflow88Sor(model, mxiter, accl, hclose, iprsor)

    @staticmethod
    def ftype():
        return "SOR"