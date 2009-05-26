################################################################################
# zms.py
#
# $Id: zms.py,v 1.13 2004/03/24 18:05:13 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.13 $
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
from __future__ import nested_scopes
from Globals import HTMLFile
from AccessControl.User import UserFolder
from App.Common import package_home
from OFS.Image import Image
from sys import *
import copy
import string 
import time
import urllib
# Product imports.
import _accessmanager
import _builder
import _confmanager
import _enummanager
import _fileutil
import _ftpmanager
import _globals
import _importable
import _language
import _metaobjmanager
import _multilangmanager
import _objattrs
import _textformatmanager
import _xmllib
import _zcatalogmanager
import _zmsattributecontainer
import zmscontainerobject
from _versionmanager import getObjStates
from zmscustom import ZMSCustom
from zmsdocument import ZMSDocument
from zmsfile import ZMSFile
from zmsfolder import ZMSFolder
from zmsgraphic import ZMSGraphic
from zmslinkcontainer import ZMSLinkContainer
from zmslinkelement import ZMSLinkElement
from zmslog import ZMSLog
from zmsnote import ZMSNote
from zmssqldb import ZMSSqlDb
from zmssysfolder import ZMSSysFolder
from zmstable import ZMSTable
from zmsteasercontainer import ZMSTeaserContainer
from zmsteaserelement import ZMSTeaserElement
from zmstextarea import ZMSTextarea
from zmstrashcan import ZMSTrashcan


################################################################################
################################################################################
###   
###   C o m m o n   F u n c t i o n ( s )
###   
################################################################################
################################################################################

# ------------------------------------------------------------------------------
#  ZMS.recurse_updateVersionBuild:
#
#  Update version build.
# ------------------------------------------------------------------------------
def recurse_updateVersionBuild(docElmnt, self, REQUEST):
  message = ''

  ##### Build 126a: ZMSFolder. ####
  if getattr( docElmnt, 'build', '000') < '126':
    if self.meta_type == 'ZMS':
      self.setConfProperty('ZMSFolder.enabled',1)
      self.setConfProperty('ZMSRubrik.enabled',0)
      # Meta-Attributes.
      metaDictAttrs = self.getConfProperty('ZMS.custom.metas',[])
      for i in range( len( metaDictAttrs) / 2):
        metaDictAttr = metaDictAttrs[ i * 2 + 1]
        if 'ZMSRubrik' in metaDictAttr['dst_meta_types']:
          j = metaDictAttr['dst_meta_types'].index( 'ZMSRubrik')
          del metaDictAttr['dst_meta_types'][ j]
          metaDictAttr['dst_meta_types'].insert( j, 'ZMSFolder')
      # Meta-Commands.
      metaCmds = getattr(self,'__attr_dc_metacmds__',[])
      for metaCmd in metaCmds:
        if 'ZMSRubrik' in metaCmd[ 'meta_types']:
          j = metaCmd[ 'meta_types'].index( 'ZMSRubrik')
          del metaCmd[ 'meta_types'][ j]
          metaCmd[ 'meta_types'].insert( j, 'ZMSFolder')
      # Meta-Objects.
      metaObjs = self.getConfProperty('ZMS.custom.objects',{})
      for metaObjId in metaObjs.keys():
        metaObj = metaObjs[ metaObjId]
        for metaObjAttr in metaObj.get( '__obj_attrs__', []):
          if metaObjAttr[ 'type'] == 'ZMSRubrik':
            metaObjAttr[ 'type'] = 'ZMSFolder'
          elif metaObjAttr[ 'type'] == '*' and 'ZMSRubrik' in metaObjAttr[ 'keys']:
            j = metaObjAttr[ 'keys'].index( 'ZMSRubrik')
            del metaObjAttr[ 'keys'][ j]
            metaObjAttr[ 'keys'].insert( j, 'ZMSFolder')
    # Rename ZMSRubriks.
    for rubrik in self.objectValues( ['ZMSRubrik']):
      old_id = rubrik.id
      new_id = rubrik.id+'~'
      self.manage_renameObject( id=old_id, new_id=new_id)
    # Copy ZMSRubriks into ZMSFolders.
    for rubrik in self.objectValues( ['ZMSRubrik']):
      rubrik_id = rubrik.id
      rubrik_local_roles = list( rubrik.get_local_roles())
      folder_id = rubrik.id[:-1]
      folder = ZMSFolder( folder_id)
      self._setObject( folder.id, folder)
      # Copy attributes from ZMSRubrik to ZMSFolder.
      folder = getattr( self, folder.id)
      for key in rubrik.__dict__.keys():
        if key != 'id' and hasattr( rubrik, key):
          v = getattr( rubrik, key)
          if key == '__work_state__' or v is None or type( v) is str:
            setattr( folder, key, v)
      # Copy local-roles from ZMSRubrik to ZMSFolder.
      for local_role in list( rubrik_local_roles):
        id = local_role[ 0]
        roles = local_role[ 1]
        folder.manage_setLocalRoles( id, roles)
      # Move sub-objects from ZMSRubrik to ZMSFolder.
      cb_copy_data = rubrik.manage_cutObjects( rubrik.objectIds())
      folder.manage_pasteObjects( cb_copy_data)
      # Delete ZMSRubrik.
      self.manage_delObjects( ids=[ rubrik_id])

  ##### Build 127a: ZMSFolder (ii). ####
  if getattr( docElmnt, 'build', '000') < '127':
    if self.meta_type == 'ZMS':
      # DTML-Methods.
      for container in [ self.getHome(), self]:
        for method in container.objectValues( ['DTML Method']):
          title = method.title
          data = method.raw
          changed = False
          while True:
            i = data.find( 'ZMSRubrik')
            if i < 0:
              break
            data = data[:i]+'ZMSFolder'+data[i+len('ZMSRubrik'):]
            changed = True
          if changed:
            _globals.writeBlock( self, "[recurse_updateVersionBuild]: DTML Method %s (%s)"%(method.id,method.title))
            method.manage_edit( title=title, data=data)
      # Meta-Commands.
      if hasattr(self,'__attr_dc_metacmds__'):
        metaCmds = getattr(self,'__attr_dc_metacmds__')
        self.setConfProperty('ZMS.custom.commands',metaCmds)
        delattr(self,'__attr_dc_metacmds__')
      # Meta-Objects.
      metaObjs = self.getConfProperty('ZMS.custom.objects',{})
      for metaObjId in metaObjs.keys():
        metaObj = metaObjs[ metaObjId]
        for metaObjAttr in metaObj.get( '__obj_attrs__', []):
          if metaObjAttr[ 'type'] in ['DTML Method', 'DTML Document', 'method']:
            data = metaObjAttr[ 'custom']
            changed = False
            while True:
              i = data.find( 'ZMSRubrik')
              if i < 0:
                break
              data = data[:i]+'ZMSFolder'+data[i+len('ZMSRubrik'):]
              changed = True
            if changed:
              _globals.writeBlock( self, "[recurse_updateVersionBuild]: Meta-Object: %s.%s"%(metaObjId,metaObjAttr['id']))
              metaObjAttr[ 'custom'] = data
      # Attributes.
      for obj_vers in self.objectValues( ['ZMSAttributeContainer']):
        for key in self.getObjAttrs().keys():
          obj_attr = self.getObjAttr(key)
          datatype = obj_attr['datatype_key']
          if datatype in _globals.DT_STRINGS:
            for lang in self.getLangIds():
              data = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
              if data is not None and type( data) is str and data != '':
                changed = False
                while True:
                  i = data.find( 'ZMSRubrik')
                  if i < 0:
                    break
                  data = data[:i]+'ZMSFolder'+data[i+len('ZMSRubrik'):]
                  changed = True
                if changed:
                  _globals.writeBlock( self, "[recurse_updateVersionBuild]: Attribute: %s"%key)
                  setobjattr(self,obj_vers,obj_attr,data,lang)

  ##### Build 128a: ZMSFolder (iii). ####
  if getattr( docElmnt, 'build', '000') < '128':
    if self.meta_type == 'ZMSFolder':
      self.synchronizePublicAccess()

  ##### Build 129a: Access-Rights ####
  if getattr( docElmnt, 'build', '000') < '129':
    mapping = { 
      'attr_has_subscriber': 'attr_dc_accessrights_restricted',
      'attr_dc_accessrights': 'attr_dc_accessrights_restrictededitors'
      }
    if self.meta_type == 'ZMS':
      # Meta-Attributes.
      metaDictAttrs = self.getConfProperty('ZMS.custom.metas',[])
      for i in range( len( metaDictAttrs) / 2):
        id = metaDictAttrs[ i * 2]
        if id in mapping.keys():
          ob = metaDictAttrs[ i * 2 + 1]
          ob[ 'id'] = mapping[ id][ 5:]
          del metaDictAttrs[ i * 2]
          metaDictAttrs.insert( i * 2, mapping[ id])
      # Meta-Objects.
      metaObjs = self.getConfProperty('ZMS.custom.objects',{})
      for metaObjId in metaObjs.keys():
        metaObj = metaObjs[ metaObjId]
        for metaObjAttr in metaObj.get( '__obj_attrs__', []):
          if metaObjAttr[ 'id'] in mapping.keys():
            metaObjAttr[ 'id'] = mapping[ metaObjAttr[ 'id']]
      # Synchronize.
      self.synchronizeObjAttrs()
    # Attributes.
    changed = False
    for key in mapping.keys():
      for ob_vers in self.objectValues( ['ZMSAttributeContainer']):
        for lang in self.getLangIds():
          if hasattr( ob_vers, key+'_'+lang):
            try:
              setattr( ob_vers, mapping[ key]+'_'+lang, getattr( ob_vers, key+'_'+lang))
              delattr( ob_vers, key+'_'+lang)
              changed = True
            except:
              pass 
        if hasattr( ob_vers, key):
          try:
            setattr( ob_vers, mapping[ key], getattr( ob_vers, key))
            delattr( ob_vers, key)
            changed = True
          except:
            pass 
    if changed:
      self.synchronizePublicAccess()

  # Recursion.
  for ob in self.objectValues( self.dGlobalAttrs.keys()):
    recurse_updateVersionBuild(docElmnt, ob, REQUEST)
  
  # Return with message.
  return message


# ------------------------------------------------------------------------------
#  ZMS.recurse_updateVersionPatch:
#
#  Update version patch.
# ------------------------------------------------------------------------------
def recurse_updateVersionPatch(docElmnt, self, REQUEST):
  message = ''

  _metaobjmanager.recurse_updateVersionPatch(docElmnt, self, REQUEST)
  _confmanager.updateConf(self,REQUEST)
  _confmanager.initCSS(self)
  self.getSequence()
  self.synchronizeObjAttrs()
  self.initLangStr()
  self.initRoleDefs()
  
  # Return with message.
  return message


# ------------------------------------------------------------------------------
#  initTheme:
# ------------------------------------------------------------------------------
def initTheme(self, theme, folder_id, REQUEST):

  ### Import theme from ZEXP.
  theme_zexp = theme + '.zexp'
  _fileutil.importZexp(self,package_home(globals())+'/import/',theme_zexp)

  ### Assign folder-id.
  if folder_id != theme: self.manage_renameObject(theme,folder_id)

  ### Return new ZMS home instance.
  return getattr(self,folder_id)


# ------------------------------------------------------------------------------
#  initZMS:
# ------------------------------------------------------------------------------
def initZMS(self, id, titleshort, title, lang, manage_lang, REQUEST):
  
  ### Constructor.
  obj = ZMS()
  obj.id = id
  self._setObject(obj.id, obj)
  obj = getattr(self,obj.id)
  
  ### Log.
  if REQUEST.get('zmslog'):
    zmslog = ZMSLog( copy_to_stdout=True, logged_entries=[ 'ERROR', 'INFO'])
    obj._setObject(zmslog.id, zmslog)
  
  ### Init Configuration.
  obj.setConfProperty('ZMS.autocommit',1)
  obj.setConfProperty('ZMS.Version.autopack',2)
  obj.setConfProperty('ZMSAdministrator.email',REQUEST.get('manager_email',''))
  obj.setConfProperty('ASP.ip_or_domain',REQUEST.get('asp_ip_or_domain',''))
  obj.setConfProperty('ZMSSqlDb.enabled',0)
  obj.setConfProperty('ZMSSysFolder.enabled',0)
  
  ### Init zcatalog.
  obj.recreateCatalog()
  
  ### Init languages.
  obj.setPrimaryLanguage(lang)
  obj.setLanguage(lang,REQUEST['lang_label'],'',manage_lang)
  
  ### Init configuration.
  _confmanager.initConf(obj, 'default_'+manage_lang, REQUEST)
  
  ### Init text-formats.
  xml = open(package_home(globals())+'/import/default.textfmt.xml')
  _textformatmanager.importXml(obj,xml=xml)
  xml.close()
  
  ### Init Object-Attributes.
  obj.synchronizeObjAttrs()
  
  ### Init Role-Definitions and Permission Settings.
  obj.initRoleDefs()
  
  ### Init Properties: active, titlealt, title.
  obj.setObjStateNew(REQUEST)
  obj.updateVersion(lang,REQUEST)
  obj.setObjProperty('active',1,lang)
  obj.setObjProperty('titleshort',titleshort,lang)
  obj.setObjProperty('title',title,lang)
  obj.onChangeObj(REQUEST,forced=1)
  
  ### Return new ZMS instance.
  return obj


# ------------------------------------------------------------------------------
#  initContent:
# ------------------------------------------------------------------------------
def initContent(self, filename, REQUEST):
  xmlfile = open(_fileutil.getOSPath(package_home(globals())+'/import/'+filename),'rb')
  _importable.importFile( self, xmlfile, REQUEST, _importable.importContent)
  xmlfile.close()


################################################################################
################################################################################
###   
###   constructor ZMS:
###   
################################################################################
################################################################################
manage_addZMSForm = HTMLFile('manage_addzmsform', globals()) 
def manage_addZMS(self, lang, manage_lang, REQUEST, RESPONSE):
  """ manage_addZMS """
  message = ''
  t0 = time.time()
  
  if REQUEST['btn'] == 'Add':
  
    ##### Add Theme ####
    homeElmnt = initTheme(self,REQUEST['theme'],REQUEST['folder_id'],REQUEST)
      
    #-- Zope Manager.
    userFldr = UserFolder()
    homeElmnt._setObject(userFldr.id, userFldr)
    name = REQUEST.get('manager_name','')
    password = REQUEST.get('manager_password','')
    confirm = password
    roles = ['Manager']
    domains = []
    userFldr._addUser(name,password,confirm,roles,domains)
    
    ##### Add ZMS ####
    titlealt = 'ZMS home'
    title = 'ZMS - ZOPE-based contentmanagement system for science, technology and medicine'
    obj = initZMS(homeElmnt,'content',titlealt,title,lang,manage_lang,REQUEST)
    
    ##### Default content ####
    if REQUEST.get('initialization',0)==1:
      initContent(obj,'content.default.zip',REQUEST)
    
    ##### E-Learning components ####
    if REQUEST.get('initialization',0)==2:
      # Create Home.
      lcmsHomeElmnt = initTheme(homeElmnt,'lcms','lcms',REQUEST)
      # Create LCMS.
      titlealt = 'LCMS'
      title = 'Learning Content Management System'
      lcms = initZMS(lcmsHomeElmnt,'content',titlealt,title,lang,manage_lang,REQUEST)
      lcms.setLanguage('eng', 'English', 'ger')
      # Init configuration.
      _confmanager.initConf(lcms, 'lcms', REQUEST)
      _confmanager.initConf(obj, 'lms', REQUEST)
      # Register Portal/Client.
      lcms.setConfProperty('Portal.Master',homeElmnt.id)
      obj.setConfProperty('Portal.Clients',[lcmsHomeElmnt.id])
      # Init content.
      initContent(lcms,'lcms.default.xml',REQUEST)
      initContent(obj,'lms.default.zip',REQUEST)
    
    ##### Configuration ####
    
    #-- Example Database
    if REQUEST.get('specobj_exampledb',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'exampledb', REQUEST)
      # Init content.
      initContent(obj,'exampledb.content.xml',REQUEST)
    
    #-- Bulletin Board
    if REQUEST.get('specobj_discussions',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'discussions', REQUEST)
      # Init content.
      initContent(obj,'discussions.content.xml',REQUEST)
    
    #-- Newsletter
    if REQUEST.get('specobj_newsletter',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'newsletter', REQUEST)
    
    #-- Calendar
    if REQUEST.get('specobj_calendar',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'calendar', REQUEST)

    ##### Access ####
    obj.synchronizePublicAccess()
    
    # Return with message.
    message = obj.getLangStr('MSG_INSERTED',manage_lang)%obj.meta_type
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    RESPONSE.redirect('%s/%s/manage?manage_tabs_message=%s'%(homeElmnt.absolute_url(),obj.id,urllib.quote(message)))
  
  else:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


################################################################################
################################################################################
###   
###   class ZMS:
###   
################################################################################
################################################################################
class ZMS(
        zmscontainerobject.ZMSContainerObject,
        _accessmanager.AccessManager,
        _builder.Builder,
        _confmanager.ConfManager,
        _ftpmanager.FtpManager,
        _language.Language,
        _objattrs.ObjAttrsManager,
        _zcatalogmanager.ZCatalogManager,
        ):

    # Version-Info.
    # -------------
    zms_build = '129'		# Internal use only, designates object model!
    zms_patch = 'f'		# Internal use only!

    # Properties.
    # -----------
    meta_type = meta_id = 'ZMS'
    icon = "misc_/zms/zms.gif"
    icon_disabled = 'misc_/zms/zms_disabled.gif'

    # Management Options.
    # -------------------
    manage_options = (
	{'label': 'TAB_EDIT',         'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES',   'action': 'manage_properties'},
	{'label': 'TAB_ACCESS',       'action': 'manage_users'},
	{'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'},
	{'label': 'TAB_TASKS',        'action': 'manage_tasks'},
	{'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'},
	{'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_CONFIGURATION','action': 'manage_customize'},
	{'label': 'TAB_PREVIEW',      'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_importexportFtp',
		'manage_addZMSSysFolder',
		'manage_customize', 'manage_customizeSystem',
		'manage_changeLanguages', 'manage_customizeLanguagesForm',
		'manage_changeMetaobjs', 'manage_customizeMetaobjForm', 'manage_BigPictureMetaobjForm',
		'manage_changeMetadicts', 'manage_customizeMetadictForm', 'manage_BigPictureMetadictForm',
		'manage_changeMetacmds', 'manage_customizeMetacmdForm',
		'manage_changeWorkflow', 'manage_changeWfTransitions', 'manage_changeWfActivities', 'manage_customizeWorkflowForm',
		'manage_customizeTextFormat', 'manage_customizeTextFormatForm',
		'manage_customizeDesign', 'manage_customizeDesignForm',
		)
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_wait',
		'manage_addZMSFolder','manage_addZMSDocument','manage_addZMSTextarea','manage_addZMSGraphic','manage_addZMSTable','manage_addZMSFile','manage_addZMSTeaserContainer','manage_addZMSNote','manage_addZMSLinkContainer','manage_addZMSLinkElement','manage_addZMSSqlDb','manage_addZMSModule',
		'manage_deleteObjs','manage_undoObjs',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_properties','manage_changeProperties',
		'manage_search','manage_search_attrs','manage_tasks',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm', 'manage_user',
		'manage_importexport', 'manage_import', 'manage_export',
		)
    __userAdministratorPermissions__ = (
		'manage_users', 'manage_userProperties', 'manage_roleProperties',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		('ZMS Author', __authorPermissions__),
		('ZMS UserAdministrator', __userAdministratorPermissions__),
		)

    # Properties.
    # -----------
    __obj_attrs__ = {
        # Changed by
        'created_uid':{'datatype':'string','multilang':False,'xml':False},
        'created_dt':{'datatype':'datetime','multilang':False,'xml':False},
        'change_uid':{'datatype':'string','multilang':True,'xml':False,'lang_inherit':False},
        'change_dt':{'datatype':'datetime','multilang':True,'xml':False,'lang_inherit':False},
        # Version info
        'change_history':{'datatype':'list','xml':False,'default':[]},
        'master_version':{'datatype':'int','xml':False,'default':0},
        'major_version':{'datatype':'int','xml':False,'default':0},
        'minor_version':{'datatype':'int','xml':False,'default':0},
        # Versioned by
        'work_uid':{'datatype':'string','multilang':1,'lang_inherit':0},
        'work_dt':{'datatype':'datetime','multilang':1,'lang_inherit':0},
        # Properties
        'active':{'datatype':'boolean','multilang':1},
        'attr_active_start':{'datatype':'datetime','multilang':1},
        'attr_active_end':{'datatype':'datetime','multilang':1},
        'title':{'datatype':'string','multilang':1,'size':40, 'mandatory': True},
        'titleshort':{'datatype':'string','multilang':1,'size':20, 'mandatory': True},
        'titleimage':{'datatype':'image','multilang':1},
        'levelnfc':{'datatype':'string','type':'select','options':[0,0,1,1,2,2],'label':'ATTR_LEVELNFC'},
        'attr_cacheable':{'datatype':'int','type':'select','options':[0,0,1,1,2,2],'default':True,'label':'ATTR_CACHEABLE'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }

    # Globals.
    # --------
    dGlobalAttrs = {
	'ZMS':{	 		'obj_class':None, 
				'constructor':None, 
				'obj_attrs':__obj_attrs__ },
	'ZMSCustom':{ 		'obj_class':ZMSCustom, 
				'constructor':None, 
				'obj_attrs':ZMSCustom.__obj_attrs__ },
	'ZMSDocument':{ 	'obj_class':ZMSDocument,
				'constructor':'manage_addzmsdocumentform',
				'obj_attrs':ZMSDocument.__obj_attrs__ },
	'ZMSFile':{ 		'obj_class':ZMSFile,
				'constructor':'manage_addzmsfileform',
				'obj_attrs':ZMSFile.__obj_attrs__ },
	'ZMSFolder':{ 		'obj_class':ZMSFolder,
				'constructor':'manage_addzmsfolderform',
				'obj_attrs':ZMSFolder.__obj_attrs__ },
	'ZMSGraphic':{ 		'obj_class':ZMSGraphic,
				'constructor':'manage_addzmsgraphicform',
				'obj_attrs':ZMSGraphic.__obj_attrs__ },
	'ZMSLinkContainer':{ 	'obj_class':ZMSLinkContainer,
				'constructor':'manage_addZMSLinkContainer',
				'obj_attrs':ZMSLinkContainer.__obj_attrs__ },
	'ZMSLinkElement':{ 	'obj_class':ZMSLinkElement,
				'constructor':'manage_addzmslinkelementform',
				'obj_attrs':ZMSLinkElement.__obj_attrs__ },
	'ZMSNote':{		'obj_class':ZMSNote,
				'constructor':'manage_addZMSNote',
				'obj_attrs':ZMSNote.__obj_attrs__ },
	'ZMSSqlDb':{ 		'obj_class':ZMSSqlDb,
				'constructor':'manage_addzmssqldbform',
				'obj_attrs':ZMSSqlDb.__obj_attrs__ },
	'ZMSSysFolder':{	'obj_class':ZMSSysFolder,
				'constructor':'manage_addzmssysfolderform',
				'obj_attrs':ZMSSysFolder.__obj_attrs__ },
	'ZMSTable':{		'obj_class':ZMSTable,
				'constructor':'manage_addzmstableform',
				'obj_attrs':ZMSTable.__obj_attrs__ },
	'ZMSTeaserElement':{	'obj_class':ZMSTeaserElement,
				'constructor':'manage_addZMSTeaserElement',
				'obj_attrs':ZMSTeaserElement.__obj_attrs__ },
	'ZMSTeaserContainer':{	'obj_class':ZMSTeaserContainer,
				'constructor':'manage_addZMSTeaserContainer',
				'obj_attrs':ZMSTeaserContainer.__obj_attrs__ },
	'ZMSTextarea':{		'obj_class':ZMSTextarea,
				'constructor':'manage_addzmstextareaform',
				'obj_attrs':ZMSTextarea.__obj_attrs__ },
	'ZMSTrashcan':{		'obj_class':ZMSTrashcan,
				'constructor':None,
				'obj_attrs':ZMSTrashcan.__obj_attrs__ },
	}

    # Interface.
    # ----------
    index_html = HTMLFile('dtml/zms/index', globals()) # index_html
    not_found_html = HTMLFile('dtml/zms/not_found', globals()) # index_html
    f_inactive_html = HTMLFile('dtml/zms/f_inactive', globals()) # inactive_html
    f_headDoctype = HTMLFile('dtml/zms/f_headdoctype', globals()) # Template_L1: DOCTYPE
    f_bodyContent = HTMLFile('dtml/zms/f_bodycontent', globals()) # Template: Body-Content / Element
    f_bodyContent_Float = HTMLFile('dtml/zms/f_bodycontent_float', globals()) # Template: Body-Content
    f_bodyContent_Sitemap = HTMLFile('dtml/zms/f_bodycontent_sitemap', globals()) # Template: Sitemap
    f_bodyContent_Search = HTMLFile('dtml/zms/f_bodycontent_search', globals()) # Template: Search
    f_bodyContent_NotFound = HTMLFile('dtml/zms/f_bodycontent_notfound', globals()) # Template: Not Found
    f_headTitle = HTMLFile('dtml/zms/f_headtitle', globals()) # Head.Title
    f_headMeta_DC = HTMLFile('dtml/zms/f_headmeta_dc', globals()) # Head.Meta.DC
    f_headMeta_Locale = HTMLFile('dtml/zms/f_headmeta_locale', globals()) # Head.Locale (Content-Type & Charset)
    f_sitemap = HTMLFile('dtml/zms/f_sitemap', globals()) # f_sitemap
    f_standard_html_request = HTMLFile('dtml/zms/f_standard_html_request', globals()) # f_standard_html_request
    f_standard_html_header = HTMLFile('dtml/zms/f_standard_html_header', globals()) # f_standard_html_header
    f_standard_html_footer = HTMLFile('dtml/zms/f_standard_html_footer', globals()) # f_standard_html_footer
    headScript = HTMLFile('dtml/zms/headscript', globals()) # Head.Script
    headMeta = HTMLFile('dtml/zms/headmeta', globals()) # Head.Meta
    headCStyleSheet = HTMLFile('dtml/zms/headcstylesheet', globals()) # Template_L1: CSS-Referenz
    headCSS = HTMLFile('dtml/zms/headcstylesheet', globals()) # Template_L1: CSS-Referenz
    search_nav_html = HTMLFile('dtml/zms/search_nav', globals()) # search_nav_html
    manage_editorForm = HTMLFile('dtml/zms/manage_editorform', globals()) # manage_editorForm
    zmsgraphic_manage_form = HTMLFile('dtml/zmsgraphic/manage_form', globals())
    zmstextarea_manage_form = HTMLFile('dtml/zmstextarea/manage_form', globals())
    
    # Enumerations.
    # -------------
    browse_enum = HTMLFile('dtml/zms/browse_enum', globals()) 
    enumManager = _enummanager.EnumManager()


    ############################################################################    
    #
    #   CONSTRUCTOR
    #
    ############################################################################    

    # --------------------------------------------------------------------------
    #  ZMS.__init__: 
    # --------------------------------------------------------------------------
    def __init__(self):
      """
      Constructor.
      """
      self.id = 'content'
      file = open(_fileutil.getOSPath(package_home(globals())+'/www/spacer.gif'),'rb')
      self.logo = Image(id='logo', title='', file=file.read())
      file.close()

    # --------------------------------------------------------------------------
    #  ZMS.zms_version:
    #
    #  Get version.
    # --------------------------------------------------------------------------
    def zms_version(self):
      file = open(_fileutil.getOSPath(package_home(globals())+'/version.txt'),'r')
      rtn = file.read()
      file.close()
      return rtn

    # --------------------------------------------------------------------------
    #  ZMS.getDocumentElement
    # --------------------------------------------------------------------------
    def getDocumentElement(self):
      """
      The root element of the site.
      """
      return self

    # --------------------------------------------------------------------------
    #  ZMS.getHome
    # --------------------------------------------------------------------------
    def getHome(self):
      """
      Returns the home-folder of the site.
      """
      docElmnt = self.getDocumentElement()
      ob = docElmnt
      try:
        depth = 0
        while ob.meta_type != 'Folder': 
          if depth > 50:
            raise "Maximum recursion depth exceeded"
          depth = depth + 1
          ob = ob.aq_parent
      except:
        ob = getattr( docElmnt, docElmnt.absolute_url().split( '/')[-2])
      return ob
    
    # --------------------------------------------------------------------------
    #  ZMS.getNewId
    # --------------------------------------------------------------------------
    def getNewId(self, id_prefix='e'):
      """
      Returns new (unique) Object-ID.
      """
      return '%s%i'%(id_prefix,self.getSequence().nextVal())

    # --------------------------------------------------------------------------
    #  ZMS.getMetaTypes:
    # --------------------------------------------------------------------------
    def getMetaTypes(self, REQUEST, excl_meta_types=['ZMS','ZMSCustom','ZMSTrashcan']): 
      """
      Returns list of meta-types.
      """
      meta_types = []
      meta_types.extend(map(lambda x: (self.display_type(REQUEST,x),x),filter(lambda x: x not in excl_meta_types and self.dGlobalAttrs[x].has_key('constructor'), self.dGlobalAttrs.keys())))
      meta_types.extend(map(lambda x: (self.display_type(REQUEST,x),x),filter(lambda x: self.getMetaobj(x)['type'] != 'ZMSPackage', self.getMetaobjIds())))
      meta_types.sort()
      return meta_types

    # --------------------------------------------------------------------------
    #  ZMS.getDCCoverage
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}):
      """
      Returns Dublin-Core Meta-Attribute Coverage.
      """
      return 'global.'+self.getPrimaryLanguage()

    # --------------------------------------------------------------------------
    #  ZMS.sendMail
    # --------------------------------------------------------------------------
    def sendMail(self, mto, msubject, mbody, REQUEST):
      """
      Sends Mail via MailHost.
      """
      
      ##### Get Sender ####
      auth_user = REQUEST['AUTHENTICATED_USER']
      mfrom = self.getUserAttr(auth_user,'email',self.getConfProperty('ZMSAdministrator.email',''))
      
      ##### Get MailHost ####
      mailhost = None
      homeElmnt = self.getHome()
      if len(homeElmnt.objectValues(['Mail Host'])) == 1:
        mailhost = homeElmnt.objectValues(['Mail Host'])[0]
      elif getattr(homeElmnt,'MailHost',None) is not None:
        mailhost = getattr(homeElmnt,'MailHost',None)
      
      ##### Get MessageText ####
      messageText = ''
      messageText += 'Content-Type: text/plain; charset=unicode-1-1-utf-8\n'
      if type(mto) is dict and mto.has_key( 'From'):
        messageText += 'From: %s\n'%mto['From']
      else:
        messageText += 'From: %s\n'%mfrom
      if type(mto) is dict:
        for key in ['To','Cc','Bcc']:
          if mto.has_key( key):
            messageText += '%s: %s\n'%(key,mto[key])
      else:
        messageText += 'To: %s\n'%mto
      messageText += 'Subject: %s\n\n'%msubject
      messageText += '%s\n'%mbody
      
      ##### Send mail ####
      try:
        _globals.writeBlock( self, "[sendMail]: %s"%messageText)
        mailhost.send(messageText)
        return 0
      except:
        return -1


    ############################################################################    
    #
    #   ZMS - Portals
    #
    ############################################################################    

    # --------------------------------------------------------------------------
    #  ZMS.getPortalMaster
    # --------------------------------------------------------------------------
    def getPortalMaster(self):
      """
      Returns portal-master, none if it does not exist.
      """
      v = self.getConfProperty('Portal.Master','')
      if len(v) > 0:
        try:
          return getattr( self, v).content
        except:
          _globals.writeException(self, '[getPortalMaster]: %s not found!'%str(v))
      return None

    # --------------------------------------------------------------------------
    #  ZMS.getPortalClients
    # --------------------------------------------------------------------------
    def getPortalClients(self):
      """
      Returns portal-clients, empty list if none exist.
      """
      docElmnts = []
      v = self.getConfProperty('Portal.Clients',[])
      if len(v) > 0:
        thisHome = self.getHome()
        for id in v:
          try:
            docElmnts.append(getattr(thisHome,id).content)
          except:
            _globals.writeException(self, '[getPortalClients]: %s not found!'%str(id))
      return docElmnts


    ############################################################################    
    #
    #   ZMS - Versions
    #
    ############################################################################    

    # --------------------------------------------------------------------------
    #  ZMS.updateVersion:
    #
    #  Update version.
    # --------------------------------------------------------------------------
    def updateVersion(self, lang, REQUEST, maintenance=True):
      message = ''
      build = getattr( self, 'build', '000')
      patch = getattr( self, 'patch', '000')
      if build != self.zms_build:
        message += recurse_updateVersionBuild( self, self, REQUEST)
        setattr( self, 'build', self.zms_build)
        message += 'Synchronized object-model from build #%s%s to #%s%s!<br/>'%(build,patch,self.zms_build,self.zms_patch)
      if build != self.zms_build or patch != self.zms_patch:
        message += recurse_updateVersionPatch( self, self, REQUEST)
        setattr( self, 'patch', self.zms_patch)
        message += 'Synchronized object-model from patch #%s%s to #%s%s!<br/>'%(build,patch,self.zms_build,self.zms_patch)
      if maintenance:
        self.getTrashcan( ).run_garbage_collection( )
      
      # Process clients.
      for portalClient in self.getPortalClients():
        message += portalClient.updateVersion( lang, REQUEST, False)
      
      return message


    ############################################################################
    ###  
    ###  DOM-Methoden 
    ### 
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMS.getParentNode
    # --------------------------------------------------------------------------
    getParentNode__roles__ = None
    def getParentNode(self): 
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      return None


    ############################################################################    
    ###
    ###   XML-Builder
    ###
    ############################################################################    

    # --------------------------------------------------------------------------
    # ZMS.xmlOnStartElement
    # --------------------------------------------------------------------------
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode, oRoot):
      """
      Handler for XML-Builder (_builder.py)
      """
      if _globals.debug( self):
        _globals.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)
      
      # remove all ZMS-objects.
      self.manage_delObjects(self.objectIds(self.dGlobalAttrs.keys()))
      # remove all languages.
      for s_lang in self.getLangIds():
        self.delLanguage(s_lang)
      
      self.dTagStack = _globals.MyStack()
      self.dValueStack  = _globals.MyStack()
      
      # WORKAROUND! The member variable "aq_parent" does not contain the right 
      # parent object at this stage of the creation process (it will later on!). 
      # Therefore, we introduce a special attribute containing the parent 
      # object, which will be used by xmlGetParent() (see below).
      self.oParent = None

################################################################################
