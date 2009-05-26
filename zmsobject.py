################################################################################
# zmsobject.py
#
# $Id: zmsobject.py,v 1.12 2004/11/24 20:54:37 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.12 $
#
# Implementation of class ZMSObject (see below).
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
from Globals import HTMLFile, Persistent
from DateTime.DateTime import DateTime
from Acquisition import Implicit
from OFS.PropertySheets import PropertySheets, vps
from webdav.Lockable import ResourceLockedError
import OFS.SimpleItem, OFS.ObjectManager, OFS.FindSupport, webdav.Collection
import urllib
import time
import string 
# Product Imports.
import zmscontainerobject
import _accessmanager
import _cachemanager
import _copysupport
import _exportable 
import _globals
import _metacmdmanager
import _multilangmanager
import _objattrs
import _objchildren
import _objinputs
import _objtypes
import _pathhandler
import _versionmanager
import _webdav
import _workflowmanager
import _xmllib
import _textformatmanager
import _zcatalogmanager
import _zmsattributecontainer
import _zmsglobals
import _zreferableitem


################################################################################
################################################################################
###
###   abstract class ZMSObject:
###
###   This is the abstract base class for all ZMS-Objects.
###
################################################################################
################################################################################
class ZMSObject(
	OFS.ObjectManager.ObjectManager,
	webdav.Collection.Collection,
	OFS.SimpleItem.Item,
	OFS.FindSupport.FindSupport,
	Persistent,				# Persistent. 
	Implicit,				# Acquisition. 
	_accessmanager.AccessableObject,	# Access manager.
	_versionmanager.VersionItem,		# Version Item.
	_workflowmanager.WorkflowItem,		# Workflow Item.
	_copysupport.CopySupport,		# Copy Support (Paste Objects).
	_cachemanager.CacheableObject,		# Cacheable object.
	_metacmdmanager.MetacmdObject,		# Meta-Commandable object.
	_multilangmanager.MultiLanguageObject,	# Multi-Language object
	_exportable.Exportable,			# XML Export.
	_objattrs.ObjAttrs,			# Object-Attributes.
	_objchildren.ObjChildren,		# Object-Children.
	_objinputs.ObjInputs,			# Object-Inputs.
	_objtypes.ObjTypes,			# Object-Types.
	_pathhandler.PathHandler,		# Path-Handler.
	_textformatmanager.TextFormatObject,	# Text-Formats.
	_zcatalogmanager.ZCatalogItem,		# ZCatalog Item.
	_zmsglobals.ZMSGlobals,			# ZMS Global Functions and Definitions.
	_zreferableitem.ZReferableItem		# ZReferable Item.
	): 

    # Documentation string.
    __doc__ = """ZMS product module."""
    # Version string. 
    __version__ = '0.1' 
    
    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage_dtpref', 'manage_page_header', 'manage_page_footer', 'manage_tabs', 'manage_tabs_sub', 'manage_bodyTop', 
		'manage_UndoVersionForm', 'manage_UndoVersion', 
		)
    __administratorPermissions__ = (
		)
    __viewPermissions__ = (
		'manage_menu',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		('ZMS Author', __authorPermissions__),
		('View', __viewPermissions__),
		)

    # Properties.
    # -----------
    QUOT = chr(34)
    MISC_ZMS = '/misc_/zms/'
    banner_gif = '/misc_/zms/banner.gif'
    spacer_gif = '/misc_/zms/spacer.gif'

    # Templates.
    # ----------
    manage = HTMLFile('dtml/object/manage', globals())
    manage_workspace = HTMLFile('dtml/object/manage', globals()) # ZMI Manage
    manage_menu = HTMLFile('dtml/object/manage_menu', globals()) # ZMI Menu
    manage_wait = HTMLFile('dtml/object/manage_wait', globals()) # ZMI Wait
    manage_tabs = HTMLFile('dtml/object/manage_tabs', globals()) # ZMI Tabulators
    manage_tabs_sub = HTMLFile('dtml/object/manage_tabs_sub', globals()) # ZMI Tabulators (Sub)
    manage_bodyTop = HTMLFile('dtml/object/manage_bodytop', globals()) # ZMI bodyTop
    manage_page_header = HTMLFile('dtml/object/manage_page_header', globals()) # ZMI Page Header
    manage_page_footer = HTMLFile('dtml/object/manage_page_footer', globals()) # ZMI Page Footer
    f_display_icon = HTMLFile('dtml/object/f_display_icon', globals()) # ZMI Display-Icon
    f_recordset_init = HTMLFile('dtml/object/f_recordset_init', globals()) # ZMI RecordSet::Init
    f_recordset_grid = HTMLFile('dtml/object/f_recordset_grid', globals()) # ZMI RecordSet::Grid
    f_recordset_nav = HTMLFile('dtml/object/f_recordset_nav', globals()) # ZMI RecordSet::Navigation
    f_headline = HTMLFile('dtml/object/f_headline', globals()) # ZMI Headline
    f_breadcrumbs = HTMLFile('dtml/object/f_breadcrumbs', globals()) # ZMI Breadcrumbs
    f_context = HTMLFile('dtml/object/f_context', globals()) # ZMI Context (Editable, Active, Access, etc.)
    f_css_sys = HTMLFile('dtml/object/f_css_sys', globals()) # CSS: Fixed System StyleSheet
    f_css_defaults = HTMLFile('dtml/object/f_css_defaults', globals()) # CSS: Default StyleSheet (WAI)
    f_css_printhtml = HTMLFile('dtml/object/f_css_printhtml', globals()) # CSS: Fixed PrintHTML StyleSheet
    f_submitInputFields = HTMLFile('dtml/object/f_submitinputfields', globals())
    f_submitBtn = HTMLFile('dtml/object/f_submitbtn', globals())
    f_submitHrefForm = HTMLFile('dtml/object/f_submithrefform', globals())
    f_collectionBtn = HTMLFile('dtml/object/f_collectionbtn', globals())
    f_languages = HTMLFile('dtml/object/f_languages', globals())
    f_frame = HTMLFile('dtml/object/f_frame', globals()) 
    f_frame_top = HTMLFile('dtml/object/f_frame_top', globals()) 
    f_frame_bottom = HTMLFile('dtml/object/f_frame_bottom', globals()) 
    f_bo_area = HTMLFile('dtml/object/f_bo_area', globals()) 
    f_eo_area = HTMLFile('dtml/object/f_eo_area', globals()) 
    f_open_input_html = HTMLFile('dtml/object/f_open_input', globals()) 
    f_xstandard_browseImages = HTMLFile('dtml/object/f_xstandard_browseimages', globals()) 
    f_xstandard_browseFiles = HTMLFile('dtml/object/f_xstandard_browsefiles', globals()) 
    preview_html = HTMLFile('dtml/object/preview', globals()) 
    preview_top_html = HTMLFile('dtml/object/preview_top', globals()) 
    active_input_fields = '' # Deprecated
    version_input_fields = '' # Deprecated

    # JavaScript.
    # -----------
    comlib_js = HTMLFile('dtml/javascript/comlib', globals()) # Common Functions
    formlib_js = HTMLFile('dtml/javascript/formlib', globals()) # Form-Functions
    datelib_js = HTMLFile('dtml/javascript/datelib', globals()) # Date-Functions
    zmilib_js = HTMLFile('dtml/javascript/zmilib', globals()) # Manage-Functions
    styleswitcher_js = HTMLFile('dtml/javascript/styleswitcher', globals()) # Stylesheet Functions


    ############################################################################
    #  ZMSObject.__init__: 
    #
    #  Constructor (initialise a new instance of ZMSObject).
    ############################################################################
    def __init__(self, id='', sort_id=0): 
      """ ZMSObject.__init__ """
      self.id = id
      self.sort_id = _globals.format_sort_id(sort_id)


    # --------------------------------------------------------------------------
    #  ZMSObject.meta_id_or_type:
    # --------------------------------------------------------------------------
    def meta_id_or_type(self):
      return self.meta_type


    # --------------------------------------------------------------------------
    #  ZMSObject.title:
    # --------------------------------------------------------------------------
    def title(self, REQUEST={}):
      return self.getObjProperty('title', REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSObject.__proxy__:
    # --------------------------------------------------------------------------
    def __proxy__(self):
      return self


    # --------------------------------------------------------------------------
    #  ZMSObject.get_logo:
    # --------------------------------------------------------------------------
    get_logo__roles__ = None
    def get_logo(self, REQUEST, RESPONSE):
      """ ZMS.get_logo """
      v = self.logo
      try:
        v = v.data
      except:
        v = v.index_html(REQUEST,RESPONSE)
      return v


    # --------------------------------------------------------------------------
    #  ZMSObject.get_conf_blob:
    # --------------------------------------------------------------------------
    get_conf_blob__roles__ = None
    def get_conf_blob(self, path, REQUEST, RESPONSE):
      """ ZMS.get_conf_blob """
      v = self.__get_attr_conf_dict__()
      try:
        for id in path.split('/'):
          if type(v) is dict:
            v = v[id]
          elif type(v) is list:
            if id.find( ':int') > 0:
              v = v[ int( id[:id.find( ':int')])]
            elif id in v:
              v = v[ v.index(id)+1]
            else:
              l = filter(lambda x: x.get('id',None)==id, v)
              if len( l) > 0:
                v = l[ 0]
        RESPONSE.setHeader( 'Cache-Control', 'public, max-age=3600')
        RESPONSE.setHeader( 'Content-Type', v.getContentType())
        RESPONSE.setHeader( 'Content-Disposition', 'inline;filename=%s'%v.getFilename())
        v = v.getData()
      except:
        masterId = self.getConfProperty('Portal.Master','')
	if len(masterId) > 0:
          masterHome = getattr(self.getHome(),masterId)
          masterDocElmnt = masterHome.content
	  v = masterDocElmnt.get_conf_blob(path, REQUEST, RESPONSE)
	else:
          _globals.writeException(self,"[get_conf_blob]: path=%s"%str(path))
      return v


    # --------------------------------------------------------------------------
    #  ZMSObject.isMetaType:
    # --------------------------------------------------------------------------
    def isMetaType(self, meta_type, REQUEST={}):
      if meta_type is None:
        return 1
      if not type(meta_type) is list:
        meta_type = [meta_type]
      b = self.meta_type in meta_type
      if not b:
        if self.PAGES in meta_type:
          b = b or self.isPage()
        elif self.PAGEELEMENTS in meta_type:
          b = b or self.isPageElement()
      return b


    # --------------------------------------------------------------------------
    #  ZMSObject.isPage:
    # --------------------------------------------------------------------------
    def isPage(self): 
      return False


    # --------------------------------------------------------------------------
    #  ZMSObject.isPageElement:
    # --------------------------------------------------------------------------
    def isPageElement(self): 
      return False


    # --------------------------------------------------------------------------
    #  ZMSObject.isResource
    # --------------------------------------------------------------------------
    def isResource(self, REQUEST):
      return self.getObjProperty('attr_dc_type',REQUEST) == 'Resource' or \
             self.id in REQUEST.get( 'ZMS_IDS_RESOURCE', [])


    # --------------------------------------------------------------------------
    #  ZMSObject.isTranslated
    #
    #  Returns True if current object is translated to given language.
    # --------------------------------------------------------------------------
    def isTranslated(self, lang, REQUEST):
      rtnVal = False
      req = {'lang':lang,'preview':REQUEST.get('preview','')}
      value = self.getObjProperty('change_uid',req)
      rtnVal = value is not None and len(value) > 0
      return rtnVal


    # --------------------------------------------------------------------------
    #  ZMSObject.isModifiedInParentLanguage
    #
    #  Returns True if current object is modified in parent language.
    # --------------------------------------------------------------------------
    def isModifiedInParentLanguage(self, lang, REQUEST):
      rtnVal = False
      parent = self.getParentLanguage(lang)
      if parent is not None:
        req = {'lang':lang, 'preview':REQUEST.get('preview','') }
        change_dt_lang = self.getObjProperty('change_dt',req)
        req = {'lang':parent, 'preview':REQUEST.get('preview','') }
        change_dt_parent = self.getObjProperty('change_dt',req)
        try:
          rtnVal = _globals.compareDate(change_dt_lang, change_dt_parent) >= 0
        except:
          _globals.writeException(self,"[isModifiedInParentLanguage]: Unexpected exception: change_dt_lang=%s, change_dt_parent=%s!"%(str(change_dt_lang),str(change_dt_parent)))
      return rtnVal


    # --------------------------------------------------------------------------
    #  ZMSObject.isVisible:
    #
    #  Returns 1 if current object is visible.
    # --------------------------------------------------------------------------
    def isVisible(self, REQUEST):
      lang = REQUEST.get('lang',self.getPrimaryLanguage())
      visible = True
      visible = visible and self.isTranslated(lang,REQUEST) # Object is translated.
      visible = visible and self.isCommitted(REQUEST) # Object has been committed.
      visible = visible and self.isActive(REQUEST) # Object is active.
      return visible


    # --------------------------------------------------------------------------
    #  ZMSObject.get_size
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def get_size(self, REQUEST={}):
      size = 0
      keys = self.getObjAttrs().keys()
      if self.meta_type=='ZMSCustom' and self.getType()=='ZMSRecordSet':
        keys = [self.getMetaobjAttrIds(self.meta_id)[0]]
      for key in keys:
        size = size + _globals.get_size(self.getObjProperty(key,REQUEST,{'fetchReqBuff':True}))
      return size


    # --------------------------------------------------------------------------
    #  ZMSObject.getDCCoverage
    #
    #  Returns "Dublin Core: Coverage".
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}):
      key_coverage = 'attr_dc_coverage'
      obj_vers = self.getObjVersion(REQUEST)
      coverage = getattr( obj_vers, key_coverage, '') # Take a performant shortcut to get object-property.
      if coverage in [ '', None]: coverage = 'global.' + self.getPrimaryLanguage()
      return coverage


    # --------------------------------------------------------------------------
    #  ZMSObject.getDCType
    #
    #  Returns "Dublin Core: Type".
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def getDCType(self, REQUEST):
      return self.getObjProperty('attr_dc_type',REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSObject.getDCDescription
    #
    #  Returns "Dublin Core: Description".
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def getDCDescription(self, REQUEST):
      return self.getObjProperty('attr_dc_description',REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSObject.getSelf:
    # --------------------------------------------------------------------------
    def getSelf(self, meta_type=None):
      ob = self
      if meta_type is not None and not ob.isMetaType( meta_type):
        parent = ob.getParentNode()
        if parent is not None:
          ob = parent.getSelf(meta_type)
      return ob


    # --------------------------------------------------------------------------
    #  ZMSObject.display_icon:
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def display_icon(self, REQUEST, meta_type=None):
      key = 'icon'
      obj_type = meta_type
      if meta_type is None:
        if not self.isActive(REQUEST):
          key = 'icon_disabled'
        obj_type = self.meta_type
        if obj_type == 'ZMSCustom':
          obj_type = self.meta_id
      if obj_type in self.getMetaobjIds( sort=0):
        if key in self.getMetaobjAttrIds( obj_type):
          metaObjAttr = self.getMetaobjAttr( obj_type, key)
          value = metaObjAttr.get( 'custom', None)
          if value is not None:
            return '%s/get_conf_blob?path=ZMS.custom.objects/%s/__obj_attrs__/%s/custom'%(self.getDocumentElement().absolute_url(),obj_type,key)	    
      if not self.dGlobalAttrs.has_key( obj_type):
        obj_type = 'ZMSCustom'
        if meta_type is not None and meta_type in self.getMetaobjIds( sort=0):
          metaObj = self.getMetaobj( meta_type)
          if metaObj is not None:
            if metaObj[ 'type'] == 'ZMSResource':
              return '%sico_class.gif'%self.MISC_ZMS
            elif metaObj[ 'type'] == 'ZMSLibrary':
              return '%sico_library.gif'%self.MISC_ZMS
            elif metaObj[ 'type'] == 'ZMSPackage':
              return '%sico_package.gif'%self.MISC_ZMS
            elif metaObj[ 'type'] == 'ZMSRecordSet':
              obj_type = 'ZMSSqlDb'
            elif metaObj[ 'type'] == 'ZMSReference':
              obj_type = 'ZMSLinkContainer'
      icon = getattr(_globals.nvl(self.dGlobalAttrs[obj_type]['obj_class'],self),key)
      if ('/'+icon).find( self.MISC_ZMS) == 0:
        icon = '/'+icon
      return icon


    # --------------------------------------------------------------------------
    #  ZMSObject.display_type:
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def display_type(self, REQUEST={}, meta_type=None):
      meta_type = _globals.nvl( meta_type, self.meta_type )
      try:
        if meta_type == 'ZMSCustom':
          meta_type = self.meta_id
        if meta_type in self.getMetaobjIds():
          return self.getMetaobj(meta_type)['name']
      except:
        pass
      return self.getZMILangStr('TYPE_%s'%meta_type.upper())


    # --------------------------------------------------------------------------
    #  ZMSObject.breadcrumbs_obj_path:
    # --------------------------------------------------------------------------
    def breadcrumbs_obj_path(self):
      REQUEST = self.REQUEST
      # Handle This.
      rtn = []
      obj = self
      for lvl in range(self.getLevel()+1):
        if obj is not None:
          obj_item = [obj]
          obj_item.extend(rtn)
          rtn = obj_item
          obj = obj.getParentNode()
      # Handle Portal Master.
      if self.getConfProperty('Portal.Master',''):
        try:
          thisHome = self.getHome()
          masterHome = getattr(thisHome,self.getConfProperty('Portal.Master',''))
          masterDocElmnt = masterHome.content
          obj_item = masterDocElmnt.breadcrumbs_obj_path()
          obj_item.extend(rtn)
          rtn = obj_item
        except:
          _globals.writeException( self, '[breadcrumbs_obj_path]: An unexpected error occured while handling portal master!')
      return rtn


    # --------------------------------------------------------------------------
    #	ZMSObject.relative_obj_path:
    # --------------------------------------------------------------------------
    def relative_obj_path(self):
      return self.absolute_url()[len(self.getDocumentElement().absolute_url())+1:]


    """
    ############################################################################
    ###  
    ###  C o m m o n   F u n c t i o n s
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSObject.findObjId:
    #
    #  Find object by ids given in object path.
    # --------------------------------------------------------------------------
    def findObjId(self, relative_obj_path, REQUEST):
      if _globals.debug( self):
        _globals.writeLog( self, '[findObjId]: relative_obj_path=%s'%relative_obj_path)
      docElmnt = self.getDocumentElement()
      ob = docElmnt
      if len(relative_obj_path) > 0:
        ids = relative_obj_path.split( '/')
        for id in ids:
          ob = getattr(ob,id,None)
          if ob is None: 
            if self.getConfProperty('ZMS.InternalLinks.autocorrection',0)==1:
              ob = self.synchronizeRefs( self.getHome().id+'@'+relative_obj_path.split('/')[-1])
            break
      return ob


    # --------------------------------------------------------------------------
    #  ZMSObject.getDeclId:
    #
    #  Returns declarative id.
    # --------------------------------------------------------------------------
    def getDeclId(self, REQUEST={}):
      if self.getConfProperty( 'ZMS.pathhandler', 0) == 0:
        declId = self.id
      else:
        declId = ''
        obj_attrs_keys = self.getObjAttrs().keys()
        for key in [ 'attr_dc_identifier_doi', 'attr_dc_identifier_url_node']:
          if key in obj_attrs_keys:
            declId = self.getObjProperty( key, REQUEST)
            if len( declId) > 0:
              break
        if len(declId) == 0:
          declId = self.getTitlealt( REQUEST)
        declId = self.id_quote( declId)
      return declId


    # --------------------------------------------------------------------------
    #  ZMSObject.getDeclUrl:
    #
    #  Returns declarative url.
    # --------------------------------------------------------------------------
    def getDeclUrl(self, REQUEST={}):
      if self.getConfProperty('ZMS.pathhandler',0) == 0 or REQUEST.get('preview','')=='preview':
        url = self.absolute_url()
      else:
        ob = self.getDocumentElement()
        url = ob.absolute_url()
        for id in self.absolute_url()[len(url):].split('/'):
          if len(id) > 0:
            ob = getattr(ob,id,None)
            if ob is None: break
            url += '/' + ob.getDeclId(REQUEST)
      return url


    # --------------------------------------------------------------------------
    #  ZMSObject.getPageExt:
    #
    #  Get page-extension.
    # --------------------------------------------------------------------------
    def getPageExt(self, REQUEST):
      pageexts = ['.html']
      if 'attr_pageext' in self.getMetadictAttrs():
        metadictAttr = self.getMetadictAttr('attr_pageext')
        if metadictAttr.has_key('keys') and len(metadictAttr.get('keys')) > 0:
          pageexts = metadictAttr.get('keys')
      pageext = self.getObjProperty('attr_pageext',REQUEST)
      if pageext == '' or pageext is None:
        pageext = pageexts[0]
      return pageext


    # --------------------------------------------------------------------------
    #  ZMSObject.getHref2Html:
    #  ZMSObject.getHref2IndexHtml:
    #  ZMSObject.getHref2PrintHtml:
    #  ZMSObject.getHref2SitemapHtml:
    #
    #  "Sans-Document"-Navigation: reference to first page that contains visible 
    #  page-elements.
    # --------------------------------------------------------------------------
    def getHref2Html(self, fct, pageext, REQUEST):
      if not self.isPage():
        parent = self.getParentNode()
        pageext = parent.getPageExt(REQUEST)
        href = parent.getHref2Html( fct, pageext, REQUEST)
        href += '#' + self.id
      else:
        href = self.getDeclUrl(REQUEST)
        # Assemble href.
        if REQUEST.get('ZMS_INDEX_HTML',0)==1 or fct != 'index' or len(self.getLangIds())>1:
          href += '/%s_%s%s'%(fct,REQUEST['lang'],pageext)
        if REQUEST.get('preview','')=='preview': href=self.url_append_params(href,{'preview':'preview'})
      if (REQUEST.get('ZMS_PATHCROPPING',False) or self.getConfProperty('ZMS.pathcropping',0)==1) and REQUEST.get('export_format','') == '':
        base = REQUEST.get('BASE0','')
        if href.find( base) == 0:
          href = href[len(base):]
      return href
      
    #++
    def getHref2SitemapHtml(self, REQUEST): 
      if not REQUEST.has_key('lang'): REQUEST.set('lang',self.getPrimaryLanguage())
      href = 'sitemap_%s%s'%(REQUEST['lang'],self.getPageExt(REQUEST))
      if REQUEST.get('preview','')=='preview': href = self.url_append_params(href,{'preview':'preview'})
      return href
      
    #++
    def getHref2PrintHtml(self, REQUEST): 
      if not REQUEST.has_key('lang'): REQUEST.set('lang',self.getPrimaryLanguage())
      href = 'index_print_%s%s'%(REQUEST['lang'],self.getPageExt(REQUEST))
      qs = REQUEST.get('QUERY_STRING','')
      if len(qs)>0: href += '?' + qs
      if REQUEST.get('preview','')=='preview': href = self.url_append_params(href,{'preview':'preview'})
      return href
    
    #++
    def getHref2IndexHtml(self, REQUEST, deep=1): 
      if not REQUEST.has_key('lang'): REQUEST.set('lang',self.getPrimaryLanguage())
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      try:
        reqBuffId = 'getHref2IndexHtml_%i'%deep
        value = self.fetchReqBuff(reqBuffId,REQUEST)
        return value
      except:
        
        #-- Get value.
        ob = self
        if deep: ob = _globals.getPageWithElements( self, REQUEST)
        value = ob.getHref2Html( 'index', ob.getPageExt(REQUEST), REQUEST)
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff(reqBuffId,value,REQUEST)


    """
    ############################################################################
    ###  
    ###  Object-actions of management interface
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSObject.filtered_edit_actions:
    # --------------------------------------------------------------------------
    def filtered_edit_actions(self, path, REQUEST):
      actions = []
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      #-- Actions.
      coverage = self.getDCCoverage(REQUEST)
      if len(path) > 0:
        if self.getAutocommit() or \
           self.getPrimaryLanguage() == lang or \
           coverage == 'global.%s'%lang or \
           coverage.find('local.')==0:
          if self.getAutocommit() or self.inObjStates(['STATE_NEW'],REQUEST) or not self.getHistory():
          
            if self.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST):
              actions.append((self.getZMILangStr('BTN_UNDO'),'manage_undoObjs'))
            can_delete = not self.inObjStates( [ 'STATE_DELETED'], REQUEST)
            if can_delete and self.meta_type == 'ZMSCustom':
              ob_access = self.getObjProperty('manage_access',REQUEST)
              can_delete = can_delete and ((not type(ob_access) is dict) or (ob_access.get( 'delete') is None) or (len( self.intersection_list( ob_access.get( 'delete'), self.getUserRoles(auth_user))) > 0))
            if can_delete:
              method = 'manage_deleteObjs'
              if self.getParentByLevel(1).meta_type == 'ZMSTrashcan': 
                method = 'manage_eraseObjs'
              actions.append((self.getZMILangStr('BTN_DELETE'),method))
            actions.append((self.getZMILangStr('BTN_CUT'),'manage_cutObjects'))
          actions.append((self.getZMILangStr('BTN_COPY'),'manage_copyObjects'))
          if self.cb_dataValid():
            actions.append((self.getZMILangStr('BTN_PASTE'),'manage_pasteObjs'))
          actions.append((self.getZMILangStr('ACTION_MOVEUP'),path + 'manage_moveObjUp'))
          actions.append((self.getZMILangStr('ACTION_MOVEDOWN'),path + 'manage_moveObjDown'))
        
      #-- Commands.
      actions.extend(self.filtered_command_actions(path,REQUEST))
      
      #-- Headline,
      if len(actions) > 0:
        actions.insert(0,('----- %s -----'%self.getZMILangStr('ACTION_SELECT')%self.getZMILangStr('ATTR_ACTION'),''))
        
      # Return action list.
      return actions


    # --------------------------------------------------------------------------
    #  ZMSObject.filtered_command_actions:
    # --------------------------------------------------------------------------
    def filtered_command_actions(self, path, REQUEST):
      actions = []
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      #-- Commands.
      for metaCmdId in self.getMetaCmdIds():
        metaCmd = self.getMetaCmd(metaCmdId)
        hasMetaType = False
        hasMetaType = hasMetaType or (self.meta_type in metaCmd['meta_types'])
        hasMetaType = hasMetaType or (self.meta_type == 'ZMSCustom' and self.meta_id in metaCmd['meta_types'])
        hasRole = False
        hasRole = hasRole or len(self.intersection_list(self.getUserRoles(auth_user),metaCmd['roles'])) > 0
        hasRole = hasRole or auth_user.has_role('Manager')
        if hasMetaType and hasRole:
          actions.append((metaCmd['name'],path+'manage_executeMetacmd'))
      
      # Return action list.
      return actions


    # --------------------------------------------------------------------------
    #  ZMSObject.ajaxFilteredChildActions:
    #
    #  Returns ajax-xml with filtered-child-actions.
    # --------------------------------------------------------------------------
    def ajaxFilteredChildActions(self, REQUEST):
      """ ZMSObject.ajaxFilteredChildActions """
      
      #-- Get actions.
      path = self.id + '/'
      actions = []
      actions.extend( self.getParentNode().filtered_insert_actions(path,REQUEST))
      actions.extend( self.filtered_edit_actions(path,REQUEST))
      actions.extend( self.filtered_workflow_actions(path,REQUEST))
      
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxFilteredChildActions.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml = self.getXmlHeader()
      xml += "<select id=\""+self.id+"\">\n"
      for action in actions:
        xml += "<option label=\"" + _globals.html_quote(action[0]) + "\" value=\"" + action[1] + "\"/>\n"
      xml += "</select>\n"
      return xml


    """
    ############################################################################
    ###  
    ###  Check In / Out
    ### 
    ############################################################################
    """

    # Management Interface.
    # ---------------------
    manage_checkout = HTMLFile('dtml/object/manage_checkout', globals()) 
    checkout = HTMLFile('dtml/object/checkout', globals()) 


    # --------------------------------------------------------------------------
    #  ZMSObject.isCheckedOut:
    # --------------------------------------------------------------------------
    def isCheckedOut(self, REQUEST):
      lang = REQUEST['lang']
      if _objattrs.hasobjattr(self,'co_dat_%s'%lang):
        co_dat = getattr(self,'co_dat_%s'%lang)
        try:
          max_time = int( self.getConfProperty('ZMS.checkout.max_time',1))
        except:
          max_time = 1
        if time.time() - co_dat < max_time * 60 * 60:
          return True
      return False


    # --------------------------------------------------------------------------
    #	ZMSObject.checkIn:
    # --------------------------------------------------------------------------
    def checkIn(self, REQUEST):
      lang = REQUEST['lang']
      if _objattrs.hasobjattr(self,'co_dat_%s'%lang): 
        delattr(self,'co_dat_%s'%lang)
      if _objattrs.hasobjattr(self,'co_uid_%s'%lang): 
        delattr(self,'co_uid_%s'%lang)


    # --------------------------------------------------------------------------
    #	ZMSObject.checkOut:
    # --------------------------------------------------------------------------
    def checkOut(self, REQUEST):
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      setattr(self,'co_dat_%s'%lang,time.time())
      setattr(self,'co_uid_%s'%lang,str(auth_user))


    """
    ############################################################################
    ###  
    ###  Sitemap
    ### 
    ############################################################################
    """

    ############################################################################
    #  ZMSObject.manage_dtpref: 
    #
    #  De-/Activate Document-Template preference.
    ############################################################################
    def manage_dtpref(self, key, lang, REQUEST, RESPONSE):
      """ ZMSObject.manage_dtpref """
      v = 1
      if REQUEST.has_key(key):
        v = int(not string.atoi(REQUEST[key]))
      e=(DateTime('GMT')+365).rfc822()
      RESPONSE.setCookie(key,str(v),path='/',expires=e)
      return RESPONSE.redirect('manage?lang=%s'%lang)


    """
    ############################################################################
    ###  
    ###  DOM-Methoden 
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSObject.getLevel:
    #
    #  The hierarchical level of this node.
    # --------------------------------------------------------------------------
    def getLevel(self):
      docElmnt = self.getDocumentElement()
      url = self.absolute_url()[ len( docElmnt.absolute_url()):]
      return len( url.split('/')) - 1


    # --------------------------------------------------------------------------
    #  ZMSObject.isAnchestor:
    #
    #  True if self is anchestor of given object.
    # --------------------------------------------------------------------------
    def isAnchestor(self, ob):
      rtn = False
      if ob is not None:
        rtn = string.find(ob.absolute_url() + '/', self.absolute_url() + '/' ) == 0
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getParentByDepth:
    #
    #  The parent of this node by depth. 
    # --------------------------------------------------------------------------
    def getParentByDepth(self, deep):
      rtn = self
      for i in range(deep):
        rtn = rtn.getParentNode()
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getParentByLevel:
    #
    #  The parent of this node by level. 
    # --------------------------------------------------------------------------
    def getParentByLevel(self, level):
      rtn = self
      while rtn.getLevel() > level:
        rtn = rtn.getParentNode()
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getParentNode:
    # --------------------------------------------------------------------------
    getParentNode__roles__ = None
    def getParentNode(self):
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      rtn = getattr(self, 'aq_parent', None)
      # Handle ZMSProxyObjects.
      if hasattr( rtn, 'is_blob') or hasattr( rtn, 'base'):
        rtn = getattr( self, self.absolute_url().split( '/')[-2], None)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getTreeNodes:
    #
    #  Returns a NodeList that contains all children of this subtree in correct order.
    #  If none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def getTreeNodes(self, REQUEST={}, meta_types=None):
      rtn = []
      for ob in self.getChildNodes(REQUEST):
        if ob.isMetaType(meta_types): rtn.append(ob)
        rtn.extend(ob.getTreeNodes(REQUEST,meta_types))
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.ajaxGetChildNodes:
    # --------------------------------------------------------------------------
    def ajaxGetChildNodes(self, lang, REQUEST):
      """ ZMSObject.ajaxGetChildNodes """

      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      auth_user = REQUEST['AUTHENTICATED_USER']
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxGetChildNodes.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml = self.getXmlHeader()
      xml += "<pages"
      for key in REQUEST.form.keys():
        if key.find('get_') < 0 and key not in ['lang','preview','http_referer','meta_types']:
          xml += " %s=\"%s\""%(key,str(REQUEST.form.get(key)))
      xml += " level=\"%i\""%self.getLevel()
      xml += ">\n"
      meta_types = REQUEST.get('meta_types')
      if REQUEST.form.get('http_referer'):
        REQUEST.set('URL',REQUEST.form.get('http_referer'))
      obs = []
      obs.extend( self.getChildNodes(REQUEST,meta_types))
      if self.meta_type == 'ZMS':
        obs.extend( self.getPortalClients())
      for ob in obs:
        ob_users = None
        if REQUEST.form.get('get_users'):
          ob_users = ob.getUsers(REQUEST)
        ob_perms = None
        if REQUEST.form.get('get_permissions'):
          ob_perms = []
          perms_optpl = [
            ['ZMS Administrator',self.getLangStr('ROLE_ZMSADMINISTRATOR',lang)],
            ['ZMS Editor',self.getLangStr('ROLE_ZMSEDITOR',lang)],
            ['ZMS Author',self.getLangStr('ROLE_ZMSAUTHOR',lang)],
            ['ZMS UserAdministrator',self.getLangStr('ROLE_ZMSUSERADMINISTRATOR',lang)],
            ['ZMS Subscriber',self.getLangStr('ROLE_ZMSSUBSCRIBER',lang)],
            ]
          for perm in perms_optpl:
            if auth_user.has_permission(perm[0],ob):
              ob_perms.append(perm[1])
        ob_restricted = None
        if REQUEST.form.get('get_restricted'):
          ob_restricted = ob.hasRestrictedAccess()
        ob_meta_type = ob.meta_type
        if ob_meta_type == 'ZMSCustom':
          ob_meta_type = ob.meta_id
        xml += "<page"
        xml += " absolute_url=\"%s\""%str(ob.absolute_url())
        xml += " access=\"%s\""%str(ob.hasAccess(REQUEST))
        xml += " active=\"%s\""%str(ob.isActive(REQUEST))
        xml += " display_icon=\"%s\""%str(ob.display_icon(REQUEST))
        xml += " display_type=\"%s\""%str(ob.display_type(REQUEST))
        xml += " id=\"%s_%s\""%(ob.getHome().id,ob.id)
        xml += " index_html=\"%s\""%_globals.html_quote(ob.getHref2IndexHtml(REQUEST,deep=0))
        xml += " is_page=\"%s\""%(ob.isPage())
        xml += " is_pageelement=\"%s\""%(ob.isPageElement())
        xml += " has_children=\"%s\""%str(len(ob.getChildNodes(REQUEST,meta_types))>0)
        xml += " meta_type=\"%s\""%(ob_meta_type)
        xml += " title=\"%s\""%_globals.html_quote(ob.getTitle(REQUEST))
        xml += " titlealt=\"%s\""%_globals.html_quote(ob.getTitlealt(REQUEST))
        if ob_perms is not None:
          xml += " permissions=\"%s\""%str(','.join(ob_perms))
        if ob_restricted is not None:
          xml += " restricted=\"%s\""%str(ob_restricted)
        xml += ">"
        if ob_users is not None:
          xml += "<users>%s</users>"%self.toXmlString(ob_users)
        if REQUEST.form.get('get_attrs', 1):
          obj_attrs = ob.getObjAttrs()
          for key in obj_attrs.keys():
            obj_attr = obj_attrs[ key]
            if obj_attr['datatype_key'] in _globals.DT_STRINGS or \
               obj_attr['datatype_key'] in _globals.DT_NUMBERS or \
               obj_attr['datatype_key'] in _globals.DT_DATETIMES:
              v = ob.getObjAttrValue(obj_attr,REQUEST)
              if v is not None:
                xml += "<%s>%s</%s>"%(key,self.toXmlString(v),key)
            elif obj_attr['datatype_key'] in _globals.DT_BLOBS:
              v = ob.getObjAttrValue(obj_attr,REQUEST)
              if v is not None:
                xml += "<%s>"%key
                xml += "<filename>%s</filename>"%v.getFilename()
                xml += "<content_type>%s</content_type>"%v.getContentType()
                xml += "</%s>"%key
        xml += "</page>"
      xml += "</pages>"
      return xml


    # --------------------------------------------------------------------------
    #  ZMSObject.getChildNodes:
    #
    #  Returns a NodeList that contains all children of this node, 
    #  if none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST={}, meta_types=None): 
      return []


    """
    ############################################################################
    ###  
    ###  Sort-Order
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSObject.setSortId:
    #
    #  Sets Sort-ID (integer).
    # --------------------------------------------------------------------------
    def setSortId(self, sort_id):
      setattr( self, 'sort_id', _globals.format_sort_id(sort_id))


    # --------------------------------------------------------------------------
    #  ZMSObject.getSortId:
    #
    #  Returns Sort-ID (integer).
    # --------------------------------------------------------------------------
    def getSortId(self, REQUEST=None): 
      try:
        sort_id = getattr( self, 'sort_id')
        rtnVal = string.atoi(sort_id[len(_globals.id_prefix(sort_id)):])
      except:
        rtnVal = 0
      return rtnVal


    ############################################################################
    # ZMSObject.manage_moveObjUp:
    #
    # Moves an object up in sort order.
    ############################################################################
    def manage_moveObjUp(self, lang, REQUEST, RESPONSE):
      """ ZMSObject.manage_moveObjUp """
      self._checkWebDAVLock()
      parent = self.getParentNode()
      sort_id = self.getSortId()
      self.setSortId(sort_id - 15)
      parent.normalizeSortIds(_globals.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJUP')%("<i>%s</i>"%self.display_type(REQUEST))
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(parent.absolute_url(),lang,urllib.quote(message),self.id))


    ############################################################################
    # ZMSObject.manage_moveObjDown:
    #
    # Moves an object down in sort order.
    ############################################################################
    def manage_moveObjDown(self, lang, REQUEST, RESPONSE):
      """ ZMSObject.manage_moveObjDown """
      self._checkWebDAVLock()
      parent = self.getParentNode()
      sort_id = self.getSortId()
      self.setSortId(sort_id + 15)
      parent.normalizeSortIds(_globals.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJDOWN')%("<i>%s</i>"%self.display_type(REQUEST))
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(parent.absolute_url(),lang,urllib.quote(message),self.id))


    ############################################################################
    # ZMSObject.manage_moveObjToPos:
    #
    # Moves an object to specified position in sort order.
    ############################################################################
    def manage_moveObjToPos(self, lang, pos, REQUEST, RESPONSE):
      """ ZMSObject.manage_moveObjToPos """
      self._checkWebDAVLock()
      parent = self.getParentNode()
      if pos == 1:
        self.setSortId(0)
      else:
        self.setSortId(pos * 10 + 5)
      parent.normalizeSortIds(_globals.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%self.display_type(REQUEST)),(pos+1))
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(parent.absolute_url(),lang,urllib.quote(message),self.id))


    # --------------------------------------------------------------------------
    #  ZMSObject.getBodyContent:
    #
    #  HTML presentation in BodyContent.
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      html = ''
      return html

    def getBodyContent(self, REQUEST):
      html = ''
      if self.isVisible( REQUEST):
        html = self._getBodyContent( REQUEST)
        # Custom hook.
        try:
          name = 'getCustomBodyContent'
          if hasattr(self,name):
            html = getattr(self,name)(context=self,html=html,REQUEST=REQUEST)
        except:
          _globals.writeException( self, '[getBodyContent]: can\'t %s'%name)
      return html


    """
    ############################################################################
    #
    #   Printable
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSObject.printHtml:
    #
    #  Renders print presentation of an Object.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      return self._getBodyContent(REQUEST)


    """
    ############################################################################
    #
    #   XML-BUILDER
    #
    ############################################################################
    """
    
    ############################################################################
    # ZMSObject.xmlOnStartElement(self, dTagName, dAttrs, oCurrNodes, oRoot):
    # ZMSObject.xmlOnCharacterData(self, data, bInCData):
    # ZMSObject.xmlOnEndElement(self):
    # ZMSObject.xmlOnUnknownStartTag(self, sTagName, dTagAttrs)
    # ZMSObject.xmlOnUnknownEndTag(self, sTagName)
    # ZMSObject.xmlGetTagName(self):
    # ZMSObject.xmlGetParent(self):
    #
    # handler for XML-Builder (_builder.py)
    ############################################################################
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode, oRoot):
        if _globals.debug( self):
          _globals.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)
        
        self.dTagStack    = _globals.MyStack()
        self.dValueStack  = _globals.MyStack()
        
        # WORKAROUND! The member variable "aq_parent" does not contain the right 
        # parent object at this stage of the creation process (it will later 
        # on!). Therefore, we introduce a special attribute containing the 
        # parent object, which will be used by xmlGetParent() (see below).
        self.oParent = oParentNode


    def xmlOnEndElement(self): 
        self.initObjChildren( self.REQUEST)

    def xmlOnCharacterData(self, sData, bInCData):
        return _xmllib.xmlOnCharacterData(self,sData,bInCData)


    def xmlOnUnknownStartTag(self, sTagName, dTagAttrs):
        return _xmllib.xmlOnUnknownStartTag(self,sTagName,dTagAttrs)


    def xmlOnUnknownEndTag(self, sTagName):
        return _xmllib.xmlOnUnknownEndTag(self,sTagName)


    def xmlGetParent(self):
        return self.oParent


    def xmlGetTagName(self):
        return self.meta_type


    """
    ############################################################################
    #
    #   WebDAV
    #
    ############################################################################    
    """

    # Standard DAVProperties + ZMSProperties.
    # ---------------------------------------
    propertysheets=vps(_webdav.ZMSPropertySheets)


    # --------------------------------------------------------------------------
    #  ZMSObject._checkWebDAVLock
    # --------------------------------------------------------------------------
    def _checkWebDAVLock(self):
      if self.wl_isLocked():
        raise ResourceLockedError, 'This %s Object is locked via WebDAV' % self.meta_type


    # --------------------------------------------------------------------------
    #  ZMSObject.document_src
    # --------------------------------------------------------------------------
    def document_src(self, REQUEST={}):
      """ document_src returns ZMSAttributes as XML """
      return self.toXml(REQUEST, incl_embedded=False, deep=False, data2hex=True)


    manage_FTPget = manage_DAVget = document_src

    # --------------------------------------------------------------------------
    #  ZMSObject.PUT
    # --------------------------------------------------------------------------
    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests"""
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        
        file=REQUEST['BODYFILE']
        
        builder = _webdav.XmlWebDAVBuilder()
        
        v = builder.parse(file)
        
        lang = REQUEST.get('lang', None)
        
        if lang is None:
          lang = self.getPrimaryLanguage()
          REQUEST.set('lang', lang)
        
        if _globals.debug( self):
          for key in v.keys():
            _globals.writeLog( self, '%s: %s' %(key, v.get(key, lang)))
        
        attrs = self.getObjAttrs()
        
        if _globals.debug( self):
          _globals.writeLog( 'Updating %s via WebDAV' % self.absolute_url())
        
        self.setObjStateModified(REQUEST)
        
        for attr in attrs.keys():
          if attr in v.keys():
            # get new value
            value_new = v.get(attr, lang)
            
            # if value is used as datetime, convert to correct form
            datatype = attrs[attr].get('datatype', 'string')
            if datatype == 'datetime':
                if value_new[0] == '(':
                    value_new = value_new[1:-1].split(',')
                    value_new = map(int, value_new)
                    value_new = _globals.getDateTime(tuple(value_new))
            
            # if value is used as boolea, convert to correct form
            if datatype == 'boolean':
                value_new = bool(value_new)
            
            # get old value
            value_old = self.getObjProperty(attr, REQUEST)
            
            # if value has changed
            if value_new != value_old:
              if _globals.debug( self):
                _globals.writeLog( 'Updating property %s: %s' % (attr, value_new))
              self.setObjProperty(attr, value_new, forced=1)
        
        self.onChangeObj(REQUEST)
        
        RESPONSE.setStatus(204)
        return RESPONSE


    # --------------------------------------------------------------------------
    #  ZMSObject.listDAVObjects
    # --------------------------------------------------------------------------
    def listDAVObjects(self):
      objectValues = getattr(self, 'objectValues', None)
      if objectValues is not None:
        spec = [ 'BTreeFolder2',
                 'DTML Document',
                 'DTML Method',
                 'File',
                 'Folder',
                 'Folder (Ordered)',
                 'Image',
                 'Script (Python)']
        spec.extend( self.dGlobalAttrs.keys())
        return objectValues(spec = spec)
      return []

################################################################################
