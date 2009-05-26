################################################################################
# _metapatternmanager.py
#
# $Id: _metapatternmanager.py,v 1.5 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.5 $
#
# Implementation of class MetapatternManager (see below).
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

# Imports.
from App.Common import package_home
from Globals import HTML, HTMLFile
import urllib
import copy
import time
import tempfile
import os
# Product Imports.
import _globals
import _fileutil


################################################################################
################################################################################
###
###   class MetapatternObject
###
################################################################################
################################################################################
class MetapatternObject: 

    # --------------------------------------------------------------------------
    #  MetapatternObject._normalize_ids_after_instantiate:
    # --------------------------------------------------------------------------
    def _normalize_ids_after_instantiate(self, REQUEST):
      #++ _globals.writeLog("[%s._normalize_ids_after_instantiate]"%(self.meta_type))
      for obj_ver in self.getObjVersions():
        obj_ver.attr_dc_coverage = 'global.'+REQUEST['lang']
        for lang in self.getLangIds():
          obj_ver.setObjProperty('created_uid',str(REQUEST['AUTHENTICATED_USER']),lang)
          obj_ver.setObjProperty('created_dt',time.time(),lang)
          obj_ver.setObjProperty('change_uid',str(REQUEST['AUTHENTICATED_USER']),lang)
          obj_ver.setObjProperty('change_dt',time.time(),lang)
      for ob in self.getChildNodes():
        id = ob.id
        id_prefix = _globals.id_prefix(id)
        if id_prefix != id:
          done = False
          while not done:
            try:
              new_id = self.getNewId(id_prefix)
              self.manage_renameObject(id=id,new_id=new_id)
              done = True
            except:
              pass
        ob._normalize_ids_after_instantiate(REQUEST)


    # Management Interface to add Meta-Objects.
    manage_addMetapatternForm = HTMLFile('dtml/metapattern/manage_addform', globals()) 
        
        
    ############################################################################
    #  MetapatternObject.manage_addMetapattern:
    #
    #  Add Meta-Pattern.
    ############################################################################
    def manage_addMetapattern(self, btn, lang, manage_lang, REQUEST, RESPONSE):
        """ MetapatternObject.manage_addMetapattern """
        message = ""
        id = ""
        
        parent = self.getParentNode()
        folder = self.getMetapatternHome()
          
        # Overwrite.
        # ----------
        if btn == self.getLangStr('BTN_OVERWRITE',manage_lang):
          id = REQUEST['overwrite_id']
          folder.manage_delObjects([id])
        
        # Insert.
        # -------
        if btn == self.getLangStr('BTN_INSERT',manage_lang):
          id = REQUEST['id']
          
        ##### Register Meta-Pattern ####
        if len(id) > 0:
          file = parent.manage_exportObject(id=self.id,download=1)
          title = REQUEST['title']
          folder.manage_addFile(id,file,title)
          obj = getattr(folder,id)
          obj.manage_addProperty('type',self.meta_type,'string')
          obj.manage_addProperty('path',self.relative_obj_path(),'string')
          
          # Return with message.
          message = urllib.quote(self.getLangStr('MSG_INSERTED',manage_lang)%title)
          return RESPONSE.redirect('%s/manage_customizeMetapatternForm?lang=%s&manage_lang=%s&manage_tabs_message=%s&id=%s'%(self.getDocumentElement().absolute_url(),lang,manage_lang,message,id))
        
        # Return with message.
        return RESPONSE.redirect('../manage_main?lang=%s&manage_lang=%s#_%s'%(lang,manage_lang,self.id))


    ############################################################################
    #  MetapatternObject.manage_instantiateMetapattern:
    #
    #  Instantiate new Meta-Pattern.
    ############################################################################
    def manage_instantiateMetapattern(self, lang, manage_lang, _sort_id, custom, REQUEST, RESPONSE=None):
      """ MetapatternObject.manage_instantiateMetapattern """
      
      ob = None
      for id in self.getMetapatternIds(REQUEST):
        metapattern = self.getMetapattern(id,REQUEST)
        if metapattern['title'] == custom:
          ob = metapattern
      
      # Create temp folder.
      folder_id = "~" + str(time.time())
      self.manage_addFolder(folder_id)
      folder = getattr(self,folder_id)
      
      # Import zexp to temp folder.
      path = INSTANCE_HOME + '/import/'
      filename = '%s.zexp'%ob['id']
      data = str(ob['ob'])
      f = open(path+filename,'wb')
      f.write(data)
      f.close()
      _fileutil.importZexp(folder,path,filename)
      
      # Copy to current container with new id.
      obj = folder.objectValues()[0]
      old_id = obj.id
      new_id = self.getNewId()
      cb_copy_data = folder.manage_copyObjects(ids=[old_id])
      self.manage_pasteObjects(cb_copy_data)
      if 'copy_of_%s'%old_id in self.objectIds(self.dGlobalAttrs.keys()):
        old_id = 'copy_of_%s'%old_id
      self.manage_renameObject(id=old_id,new_id=new_id)
      
      obj = getattr(self,new_id)
      obj._normalize_ids_after_instantiate(REQUEST)
      
      ##### Object State ####
      obj.setObjStateNew(REQUEST,reset=0)
      
      ##### Init Properties ####
      for obj_ver in self.getObjVersions():
        obj_ver.sort_id = _globals.format_sort_id(_sort_id+1)
      
      ##### VersionManager ####
      obj.onChangeObj(REQUEST)
      
      ##### Normalize Sort-IDs ####
      self.normalizeSortIds()
      
      # Remove temp folder.
      self.manage_delObjects(ids=[folder_id],REQUEST=None)
      
      # Return with message.
      if RESPONSE:
        message = urllib.quote(self.getLangStr('MSG_INSERTED',manage_lang)%ob['title'])
        if obj.meta_type in ['ZMS','ZMSFolder','ZMSDocument','ZMSSysFolder']:
          return RESPONSE.redirect('%s/manage_properties?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(obj.id,lang,manage_lang,message))
        else:
          return RESPONSE.redirect('%s/manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(obj.id,lang,manage_lang,message))


################################################################################
################################################################################
###
###   class MetapatternManager
###
################################################################################
################################################################################
class MetapatternManager(MetapatternObject): 

    # Management Interface.
    # ---------------------
    manage_customizeMetapatternForm = HTMLFile('dtml/metapattern/manage_customizeform', globals()) 


    # --------------------------------------------------------------------------
    #  MetapatternManager.getMetapatternHome
    # --------------------------------------------------------------------------
    def getMetapatternHome(self):
      id = 'acl_metapatterns'
      docElmnt = self.getDocumentElement()
      if not id in docElmnt.objectIds(['Folder']):
        docElmnt.manage_addFolder(id=id,title='*** DO NOT DELETE OR MODIFY ***')
      return getattr(docElmnt,id)

    # --------------------------------------------------------------------------
    #  MetapatternManager.initMetapattern
    # --------------------------------------------------------------------------
    def initMetapattern(self, id):
      folder = self.getMetapatternHome()
      if not id in folder.objectIds(['File']):
        _fileutil.importZexp(folder,package_home(globals())+'/import/',id+'.zpat')
        #-- Reset path.
        ob = getattr(folder,id)
        ob.manage_changeProperties({'path':''})

    # --------------------------------------------------------------------------
    # MetapatternManager.getMetapatternIds:
    # 
    # Returns list of IDs of Meta-Patterns.
    # --------------------------------------------------------------------------
    def getMetapatternIds(self, REQUEST, meta_type=None):
      folder = self.getMetapatternHome()
      ids = []
      for id in folder.objectIds(['File']):
        if meta_type is None or self.getMetapattern(id,REQUEST)['type']==meta_type:
          ids.append(id)
      return ids

    # --------------------------------------------------------------------------
    # MetapatternManager.getMetapatternTitle:
    # 
    # Returns title of Meta-Pattern identified by ID.
    # --------------------------------------------------------------------------
    def getMetapatternTitle(self, id, REQUEST):
      folder = self.getMetapatternHome()
      ob = getattr(folder,id)
      return ob.title

    # --------------------------------------------------------------------------
    # MetapatternManager.getMetapattern:
    # 
    # Returns Meta-Pattern identified by ID.
    # --------------------------------------------------------------------------
    def getMetapattern(self, id, REQUEST):
      folder = self.getMetapatternHome()
      ob = getattr(folder,id)
      ob_title = ob.title_or_id()
      ob_type = ob.getProperty('type')
      ob_path = ob.getProperty('path')
      ob_src = None
      if ob_path:
        ob_src = ob.getLinkObj('{$' + ob_path + '}',REQUEST)
      return {'id':id,'title':ob_title,'type':ob_type,'path':ob_path,'src':ob_src,'ob':ob}


    # --------------------------------------------------------------------------
    # MetapatternManager.delMetapattern:
    # 
    # Delete Meta-Pattern specified by ID.
    # --------------------------------------------------------------------------
    def delMetapattern(self, id):
      folder = self.getMetapatternHome()
      folder.manage_delObjects(ids=[id])


    ############################################################################
    # MetapatternManager.manage_changeMetapattern:
    #
    # Change Meta-Patterns.
    ############################################################################
    def manage_changeMetapattern(self, btn, lang, manage_lang, REQUEST, RESPONSE):
        """ MetapatternManager.manage_changeMetapattern """
        message = ''
        id = ''
        
        # Delete.
        # -------
        if btn == self.getLangStr('BTN_DELETE',manage_lang):
          id = REQUEST['id']
          self.delMetapattern(id)
          id = ''
          message = urllib.quote(self.getLangStr('MSG_CHANGED',manage_lang))
        
        # Change.
        # -------
        elif btn == self.getLangStr('BTN_CHANGE',manage_lang):
          id = REQUEST['id']
          new_id = REQUEST['new_id'].strip()
          new_title = REQUEST['new_title'].strip()
          folder = self.getMetapatternHome()
          if id != new_id:
            folder.manage_renameObject(id=id,new_id=new_id)
          obj = getattr(folder,new_id)
          obj.title = new_title
          id = new_id
          message = urllib.quote(self.getLangStr('MSG_CHANGED',manage_lang))        
        
        # Export.
        # -------
        elif btn == self.getLangStr('BTN_EXPORT',manage_lang):
          id = REQUEST['id']
          folder = self.getMetapatternHome()
          content_type = 'application/zip'
          export = folder.manage_exportObject(id=id,download=1)
          filename = id + '.zpat'
          RESPONSE.setHeader('Content-Type',content_type)
          RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
          return export
        
        # Import.
        # -------
        elif btn == self.getLangStr('BTN_IMPORT',manage_lang):
          folder = self.getMetapatternHome()
          idsBefore = self.getMetapatternIds(REQUEST)
          #-- Create temporary folder.
          path = tempfile.mktemp() + os.sep
          filename = 'metapattern.zexp'
          #-- Save file to temporary folder.
          _fileutil.exportObj(REQUEST['file'],'%s/%s'%(path,filename))
          #-- Import zexp
          _fileutil.importZexp(folder,path,filename)
          #-- Remove temporary folder.
          _fileutil.remove(path,deep=1)
          #-- Retrieve id.
          idsAfter = self.getMetapatternIds(REQUEST)
          for id in idsAfter:
            if id not in idsBefore:
              new_id = id
          id = new_id
          #-- Reset path.
          ob = getattr(folder,id)
          ob.manage_changeProperties({'path':''})
        
        # Return with message.
        return RESPONSE.redirect('manage_customizeMetapatternForm?lang=%s&manage_lang=%s&manage_tabs_message=%s&id=%s'%(lang,manage_lang,message,id))

################################################################################
