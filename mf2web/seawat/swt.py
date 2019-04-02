import flopy as fp
from ..mt3d import Mt3dms
import os


# This class can be removed when Seawat is fixed!
class Seawat(fp.seawat.Seawat):
    """
    Override of the flopy seawat class until it is
    fixed.
    """
    def __init__(self, modelname='swttest', namefile_ext='nam',
                 modflowmodel=None, mt3dmodel=None,
                 version='seawat', exe_name='swtv4',
                 structured=True, listunit=2, model_ws='.', external_path=None,
                 verbose=False, load=True, silent=0):

        super(Seawat, self).__init__(modelname, namefile_ext,
                                     modflowmodel, mt3dmodel,
                                     version, exe_name,
                                     structured, listunit, model_ws,
                                     external_path, verbose, load, silent)

        self._mg_resync = True

    @property
    def modelgrid(self):
        if not self._mg_resync:
            return self._modelgrid

        bas = self.get_package("BAS6")
        if bas is not None:
            ibound = bas.ibound.array
        else:
            ibound = None
        # build grid
        modelgrid = fp.discretization.StructuredGrid(self.dis.delc.array,
                                                     self.dis.delr.array,
                                                     self.dis.top.array,
                                                     self.dis.botm.array, ibound,
                                                     lenuni=self.dis.lenuni,
                                                     proj4=self._modelgrid.proj4,
                                                     epsg=self._modelgrid.epsg,
                                                     xoff=self._modelgrid.xoffset,
                                                     yoff=self._modelgrid.yoffset,
                                                     angrot=self._modelgrid.angrot)

        self._modelgrid = modelgrid

        # resolve offsets
        xoff = self._modelgrid.xoffset
        if xoff is None:
            if self._xul is not None:
                xoff = self._modelgrid._xul_to_xll(self._xul)
            else:
                xoff = 0.0
        yoff = self._modelgrid.yoffset
        if yoff is None:
            if self._yul is not None:
                yoff = self._modelgrid._yul_to_yll(self._yul)
            else:
                yoff = 0.0
        self._modelgrid.set_coord_info(xoff, yoff, self._modelgrid.angrot,
                                       self._modelgrid.epsg,
                                       self._modelgrid.proj4)
        return self._modelgrid


    @staticmethod
    def load(f, version='seawat', exe_name='swtv4', verbose=False,
             model_ws='.', load_only=None):
        """
        Load an existing model.

        Parameters
        ----------
        f : string
            Full path and name of SEAWAT name file.

        version : string
            The version of SEAWAT (seawat)
            (default is seawat)

        exe_name : string
            The name of the executable to use if this loaded model is run.
            (default is swtv4.exe)

        verbose : bool
            Write information on the load process if True.
            (default is False)

        model_ws : string
            The path for the model workspace.
            (default is the current working directory '.')

        load_only : list of strings
            Filetype(s) to load (e.g. ['lpf', 'adv'])
            (default is None, which means that all will be loaded)

        Returns
        -------
        m : flopy.seawat.swt.Seawat
            flopy Seawat model object

        Examples
        --------

        >>> import mf2py
        >>> m = mf2py.seawat.Seawat.load(f)

        """
        # test if name file is passed with extension (i.e., is a valid file)
        if os.path.isfile(os.path.join(model_ws, f)):
            modelname = f.rpartition('.')[0]
        else:
            modelname = f

        # create instance of a seawat model and load modflow and mt3dms models
        ms = Seawat(modelname=modelname, namefile_ext='nam',
                    modflowmodel=None, mt3dmodel=None,
                    version=version, exe_name=exe_name, model_ws=model_ws,
                    verbose=verbose)

        mf = fp.modflow.Modflow.load(f, version='mf2k', exe_name=None, verbose=verbose,
                                     model_ws=model_ws, load_only=load_only, forgive=True,
                                     check=False)

        mt = Mt3dms.load(f, version='mt3dms', exe_name=None, verbose=verbose,
                         model_ws=model_ws, forgive=True, modflowmodel=mf)

        # set listing and global files using mf objects
        ms.lst = mf.lst
        ms.glo = mf.glo

        for p in mf.packagelist:
            p.parent = ms
            ms.add_package(p)
        ms._mt = None
        if mt is not None:
            for p in mt.packagelist:
                p.parent = ms
                ms.add_package(p)
            mt.external_units = []
            mt.external_binflag = []
            mt.external_fnames = []
            ms._mt = mt
        ms._mf = mf

        # potentially drop _mf and _mt not sure why we need them, may cuase issues...

        # return model object
        return ms