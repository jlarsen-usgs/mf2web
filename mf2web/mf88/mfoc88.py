from flopy.pakbase import Package
import sys


class Modflow88Oc(Package):
    """
    Class to read modflow88 output control

    see modflow 88 documentation...
    """
    def __init__(self, model, ihedfm="(10G11.4)", iddnfm="(10G11.4)",
                 ihedun=70, iddnun=80, incode=(0,), ihddfl=(0,),
                 ibudfl=(0,), icbcfl=(0,), hdpr=([1],), ddpr=([1],),
                 hdsv=([1],), ddsv=([1],)):

        unitnumber = [12, ihedun, iddnun]
        filenames = [None, None, None]
        extension = ['oc']
        name = [Modflow88Oc.ftype()]
        extra = [""]

        super(Modflow88Oc, self).__init__(model, extension=extension,
                                          name=name, unit_number=unitnumber,
                                          extra=extra, filenames=filenames)

        self.ihedfm = ihedfm
        self.iddnfm = iddnfm
        self.ihedun = ihedun
        self.iddnun = iddnun
        self.incode = incode
        self.ihddfl = ihddfl
        self.ibudfl = ibudfl
        self.icbcfl = icbcfl
        self.hdpr = hdpr
        self.ddpr = ddpr
        self.hdsv = hdsv
        self.ddsv = ddsv
        self.parent.add_package(self)

    @staticmethod
    def load(f, model, ntsp=1, nlay=1, ext_unit_dict=None):
        """
        Load an existing package

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        ntsp : int
            number of model time steps
        nlay : int
            number of model layers
        ext_unit_dict : dict
            Dictionary of unit and file names

        Returns
        -------
        oc : Modflow88Oc object
            Modflow88Oc object (of type :class:`mf2web.mf88.Modflow88Oc`)
        """
        if model.verbose:
            sys.stdout.write('loading oc package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        if model.nrow_ncol_nlay_nper != (0, 0, 0, 0):
            nrow, ncol, nlay, nper = model.nrow_ncol_nlay_nper

        t = f.readline()[0:40].split()
        ihedfm, iddnfm, ihedun, iddnun = t[0], t[1], int(t[2]), int(t[3])

        incode = []
        ihddfl = []
        ibudfl = []
        icbcfl = []
        hdpr = []
        ddpr = []
        hdsv = []
        ddsv = []

        for _ in range(ntsp):
            t = f.readline().split()
            incode0 = int(t[0])
            ihddfl0 = int(t[1])
            ibudfl0 = int(t[2])
            if incode0 >= 0:
                icbcfl0 = int(t[3])
            else:
                icbcfl0 = 0

            incode.append(incode0)
            ihddfl.append(ihddfl0)
            ibudfl.append(ibudfl0)
            icbcfl.append(icbcfl0)

            if incode0 < 0:
                hdpr.append(hdpr[-1])
                ddpr.append(ddpr[-1])
                hdsv.append(hdsv[-1])
                ddsv.append(ddsv[-1])

            elif incode0 == 0:
                t = f.readline().split()
                hdpr.append([int(t[0])])
                ddpr.append([int(t[1])])
                hdsv.append([int(t[2])])
                ddsv.append([int(t[3])])

            else:
                hdpr0 = []
                ddpr0 = []
                hdsv0 = []
                ddsv0 = []
                for lay in range(nlay):
                    t = f.readline().split()
                    hdpr0.append(int(t[0]))
                    ddpr0.append(int(t[1]))
                    hdsv0.append(int(t[2]))
                    ddsv0.append(int(t[3]))
                hdpr.append(hdpr0)
                ddpr.append(ddpr0)
                hdsv.append(hdsv0)
                ddsv.append(ddsv0)

        return Modflow88Oc(model, ihedfm, iddnfm, ihedun, iddnun,
                           incode, ihddfl, ibudfl, icbcfl,
                           hdpr, ddpr, hdsv, ddsv)

    @staticmethod
    def ftype():
        return "OC"