import os
import sys
import numpy as np
import flopy as fp
from flopy.utils import mfreadnam
from flopy.discretization import StructuredGrid


class Mt3dms(fp.mt3d.Mt3dms):
    """
    Override of the flopy mt3ms class until the modelgrid issues
    are fixed
    """
    def __init__(self, modelname='mt3dtest', namefile_ext='nam',
                 modflowmodel=None, ftlfilename="mt3d_link.ftl", ftlfree=False,
                 version='mt3dms', exe_name='mt3dms.exe',
                 structured=True, listunit=None, ftlunit=None,
                 model_ws='.', external_path=None,
                 verbose=False, load=True, silent=0):

        super(Mt3dms, self).__init__(modelname=modelname, namefile_ext=namefile_ext,
                                     modflowmodel=modflowmodel, ftlfilename=ftlfilename, ftlfree=ftlfree,
                                     version=version, exe_name=exe_name,
                                     structured=structured, listunit=listunit, ftlunit=ftlunit,
                                     model_ws=model_ws, external_path=external_path,
                                     verbose=verbose, load=load, silent=silent)

        self._mg_resync = True

    @property
    def modelgrid(self):
        if not self._mg_resync:
            return self._modelgrid

        bas = self.mf.get_package("BAS6")
        if bas is not None:
            ibound = self.btn.icbund.array
        else:
            ibound = None
        # build grid
        self._modelgrid = StructuredGrid(delc=self.mf.dis.delc.array,
                                         delr=self.mf.dis.delr.array,
                                         top=self.mf.dis.top.array,
                                         botm=self.mf.dis.botm.array,
                                         idomain=ibound,
                                         proj4=self._modelgrid.proj4,
                                         epsg=self._modelgrid.epsg,
                                         xoff=self._modelgrid.xoffset,
                                         yoff=self._modelgrid.yoffset,
                                         angrot=self._modelgrid.angrot)

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
    def load(f, version='mt3dms', exe_name='mt3dms.exe', verbose=False,
             model_ws='.', load_only=None, forgive=False, modflowmodel=None):
        """
        Load an existing model.

        Parameters
        ----------
        f : string
            Full path and name of MT3D name file.

        version : string
            The version of MT3D (mt3dms, or mt3d-usgs)
            (default is mt3dms)

        exe_name : string
            The name of the executable to use if this loaded model is run.
            (default is mt3dms.exe)

        verbose : bool
            Write information on the load process if True.
            (default is False)

        model_ws : string
            The path for the model workspace.
            (default is the current working directory '.')

        load_only : list of strings
            Filetype(s) to load (e.g. ['btn', 'adv'])
            (default is None, which means that all will be loaded)

        modflowmodel : flopy.modflow.mf.Modflow
            This is a flopy Modflow model object upon which this Mt3dms
            model is based. (the default is None)

        Returns
        -------
        mt : flopy.mt3d.mt.Mt3dms
            flopy Mt3d model object

        Notes
        -----
        The load method does not retain the name for the MODFLOW-generated
        FTL file.  This can be added manually after the MT3D model has been
        loaded.  The syntax for doing this manually is
        mt.ftlfilename = 'example.ftl'

        Examples
        --------

        >>> import mf2web
        >>> f = 'example.nam'
        >>> mt = mf2web.mt3d.Mt3dms.load(f)
        >>> mt.ftlfilename = 'example.ftl'

        """
        # test if name file is passed with extension (i.e., is a valid file)
        modelname_extension = None
        if os.path.isfile(os.path.join(model_ws, f)):
            modelname = f.rpartition('.')[0]
            modelname_extension = f.rpartition('.')[2]
        else:
            modelname = f

        if verbose:
            sys.stdout.write('\nCreating new model with name: {}\n{}\n\n'.
                             format(modelname, 50 * '-'))
        mt = Mt3dms(modelname=modelname, namefile_ext=modelname_extension,
                    version=version, exe_name=exe_name,
                    verbose=verbose, model_ws=model_ws,
                    modflowmodel=modflowmodel)

        files_successfully_loaded = []
        files_not_loaded = []

        # read name file
        try:
            # namefile_path = os.path.join(mt.model_ws, mt.namefile)
            # namefile_path = f
            namefile_path = os.path.join(mt.model_ws, f)
            ext_unit_dict = mfreadnam.parsenamefile(namefile_path,
                                                    mt.mfnam_packages,
                                                    verbose=verbose)
        except Exception as e:
            # print("error loading name file entries from file")
            # print(str(e))
            # return None
            raise Exception(
                "error loading name file entries from file:\n" + str(e))

        if mt.verbose:
            print('\n{}\nExternal unit dictionary:\n{}\n{}\n'.
                  format(50 * '-', ext_unit_dict, 50 * '-'))

        # reset unit number for list file
        unitnumber = None
        for key, value in ext_unit_dict.items():
            if value.filetype == 'LIST':
                unitnumber = key
                filepth = os.path.basename(value.filename)
        if unitnumber == 'LIST':
            unitnumber = 16
        if unitnumber is not None:
            mt.lst.unit_number = [unitnumber]
            mt.lst.file_name = [filepth]

        # set ftl information
        unitnumber = None
        for key, value in ext_unit_dict.items():
            if value.filetype == 'FTL':
                unitnumber = key
                filepth = os.path.basename(value.filename)
        if unitnumber == 'FTL':
            unitnumber = 10
        if unitnumber is not None:
            mt.ftlunit = unitnumber
            mt.ftlfilename = filepth

        # load btn
        btn = None
        btn_key = None
        for key, item in ext_unit_dict.items():
            if item.filetype.lower() == "btn":
                btn = item
                btn_key = key
                break

        if btn is None:
            return None

        try:
            pck = btn.package.load(btn.filename, mt,
                                   ext_unit_dict=ext_unit_dict)
        except Exception as e:
            raise Exception('error loading BTN: {0}'.format(str(e)))
        files_successfully_loaded.append(btn.filename)
        if mt.verbose:
            sys.stdout.write('   {:4s} package load...success\n'
                             .format(pck.name[0]))
        ext_unit_dict.pop(btn_key)

        if load_only is None:
            load_only = []
            for key, item in ext_unit_dict.items():
                load_only.append(item.filetype)
        else:
            if not isinstance(load_only, list):
                load_only = [load_only]
            not_found = []
            for i, filetype in enumerate(load_only):
                filetype = filetype.upper()
                if filetype != 'BTN':
                    load_only[i] = filetype
                    found = False
                    for key, item in ext_unit_dict.items():
                        if item.filetype == filetype:
                            found = True
                            break
                    if not found:
                        not_found.append(filetype)
            if len(not_found) > 0:
                raise Exception(
                    "the following load_only entries were not found "
                    "in the ext_unit_dict: " + ','.join(not_found))

        # try loading packages in ext_unit_dict
        for key, item in ext_unit_dict.items():
            if item.package is not None:
                if item.filetype in load_only:
                    if forgive:
                        try:
                            pck = item.package.load(item.filename, mt,
                                                    ext_unit_dict=ext_unit_dict)
                            files_successfully_loaded.append(item.filename)
                            if mt.verbose:
                                sys.stdout.write(
                                    '   {:4s} package load...success\n'
                                        .format(pck.name[0]))
                        except BaseException as o:
                            if mt.verbose:
                                sys.stdout.write(
                                    '   {:4s} package load...failed\n   {!s}\n'
                                        .format(item.filetype, o))
                            files_not_loaded.append(item.filename)
                    else:
                        pck = item.package.load(item.filename, mt,
                                                ext_unit_dict=ext_unit_dict)
                        files_successfully_loaded.append(item.filename)
                        if mt.verbose:
                            sys.stdout.write(
                                '   {:4s} package load...success\n'
                                    .format(pck.name[0]))
                else:
                    if mt.verbose:
                        sys.stdout.write('   {:4s} package load...skipped\n'
                                         .format(item.filetype))
                    files_not_loaded.append(item.filename)
            elif "data" not in item.filetype.lower():
                files_not_loaded.append(item.filename)
                if mt.verbose:
                    sys.stdout.write('   {:4s} package load...skipped\n'
                                     .format(item.filetype))
            elif "data" in item.filetype.lower():
                if mt.verbose:
                    sys.stdout.write('   {} file load...skipped\n      {}\n'
                                     .format(item.filetype,
                                             os.path.basename(item.filename)))
                if key not in mt.pop_key_list:
                    mt.external_fnames.append(item.filename)
                    mt.external_units.append(key)
                    mt.external_binflag.append("binary"
                                               in item.filetype.lower())
                    mt.external_output.append(False)

        # pop binary output keys and any external file units that are now
        # internal
        for key in mt.pop_key_list:
            try:
                mt.remove_external(unit=key)
                ext_unit_dict.pop(key)
            except:
                if mt.verbose:
                    sys.stdout.write('Warning: external file unit " +\
                        "{} does not exist in ext_unit_dict.\n'.format(key))

        # write message indicating packages that were successfully loaded
        if mt.verbose:
            print(1 * '\n')
            s = '   The following {0} packages were successfully loaded.' \
                .format(len(files_successfully_loaded))
            print(s)
            for fname in files_successfully_loaded:
                print('      ' + os.path.basename(fname))
            if len(files_not_loaded) > 0:
                s = '   The following {0} packages were not loaded.'.format(
                    len(files_not_loaded))
                print(s)
                for fname in files_not_loaded:
                    print('      ' + os.path.basename(fname))
                print('\n')

        # return model object
        return mt