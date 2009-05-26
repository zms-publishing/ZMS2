################################################################################
# _confmanager.py
#
# $Id: _confmanager.py,v 1.9 2004/11/30 20:03:17 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.9 $
#
# Implementation of class Configuration-Manager (see below).
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
from cStringIO import StringIO
from App.Common import package_home
from Globals import HTMLFile
from OFS.CopySupport import absattr
from OFS.Image import Image
import os
import stat
import urllib
# Product imports.
import _charformatmanager
import _globals
import _fileutil
import _filtermanager
import _mediadb
import _metadictmanager
import _metacmdmanager
import _metaobjmanager
import _multilangmanager
import _sequence
import _textformatmanager
import _workflowmanager
import zmslog


"""
################################################################################
###
###   Initialization
###
################################################################################
"""

# ------------------------------------------------------------------------------
#  _confmanager.initCSS:
# ------------------------------------------------------------------------------
def initCSS(self):
  stylesheet_css = getattr( self, 'stylesheet.css', None)
  if stylesheet_css is not None:
    container = getattr( self.getHome(), 'common', None)
    folder = getattr( container, 'css', None)
    if folder is not None:
      container = getattr( self.getHome(), 'instance', None)
      if container is None:
        self.getHome().manage_addFolder( id='instance', title='Local Graphics and Assets')
        container = getattr( self.getHome(), 'instance', None)
      folder = getattr( container, 'css', None)
    if folder is None:
      container.manage_addFolder( id='css', title='Cascading Style-Sheets')
      folder = getattr( container, 'css', None)
    ids = self.objectIds(['DTML Method'])
    excl_ids = filter( lambda x: x in ids, [ 'stylesheet.css'] + map( lambda x: 'stylesheet_%s.css'%x, self.getLangIds()))
    move_ids = filter( lambda x: x not in excl_ids and x.find('.css') > 0, ids)
    id = 'style.css'
    title = 'Default CSS'
    data = stylesheet_css.raw
    if data.find( '<dtml-var') >= 0:
      data = '<dtml-with content\n><dtml-call "REQUEST.RESPONSE.setHeader(\'Cache-Control\',\'public, max-age=3600\')"\n><dtml-var f_standard_html_request\n><dtml-var f_css_defaults>\n'+data+'\n</dtml-with>'
    if id not in folder.objectIds():
      folder.manage_addDTMLMethod( id, title, data)
    self.manage_delObjects( ids=excl_ids)
    try:
      cb_copy_data = self.manage_cutObjects(move_ids,self.REQUEST)
      folder.manage_pasteObjects(cb_copy_data=None,REQUEST=self.REQUEST)
    except:
      pass


# ------------------------------------------------------------------------------
#  _confmanager.initConf:
# ------------------------------------------------------------------------------
def initConf(self, profile, REQUEST):
  createIfNotExists = 1
  filenames = self.getConfFiles()
  for filename in filenames:
    if filename.find(profile + '.') == 0:
      if filename.find('.zip') > 0:
        self.importConfPackage(filename,REQUEST,createIfNotExists)
      elif filename.find('.xml') > 0:
        self.importConf(filename,REQUEST,createIfNotExists)


# ------------------------------------------------------------------------------
#  _confmanager.updateConf:
# ------------------------------------------------------------------------------
def updateConf(self, REQUEST):
  filenames = self.getConfFiles()
  for filename in filenames:
    self.importConf(filename,REQUEST,0)


################################################################################
################################################################################
###
###   class ConfManager:
###
################################################################################
################################################################################
class ConfManager(
	_multilangmanager.MultiLanguageManager,		# Languages
	_metadictmanager.MetadictManager,		# Metadata
	_metaobjmanager.MetaobjManager,			# Spec. Objects
	_metacmdmanager.MetacmdManager,			# Actions
	_workflowmanager.WorkflowManager,		# Workflow
	_textformatmanager.TextFormatManager,		# Text-Formats
	_charformatmanager.CharFormatManager,		# Char-Formats
	_filtermanager.FilterManager,			# Filters (XML Im-/Export)
	):

    # Management Interface.
    # ---------------------
    manage_customize = HTMLFile('dtml/zms/manage_customize', globals()) 
    manage_customizeDesignForm = HTMLFile('dtml/zms/manage_customizedesignform', globals()) 


    # --------------------------------------------------------------------------
    #  ConfManager.importConfPackage:
    # --------------------------------------------------------------------------
    def importConfPackage(self, file, REQUEST, createIfNotExists=0):
      if type( file) is str:
        filename = file
        filepath = package_home(globals())+'/import/'
        file = open(_fileutil.getOSPath(filepath+filename),'rb')
      files = _fileutil.getZipArchive( file)
      for f in files:
        self.importConf(f,REQUEST,createIfNotExists)


    # --------------------------------------------------------------------------
    #  ConfManager.importConf:
    # --------------------------------------------------------------------------
    def importConf(self, file, REQUEST, createIfNotExists=0):
      if type(file) is dict:
        filename = file['filename']
        xmlfile = StringIO( file['data'])
      else:
        filename = file
        filepath = package_home(globals())+'/import/'
        xmlfile = open(_fileutil.getOSPath(filepath+filename),'rb')
      if filename.find('.charfmt.') > 0:
        _charformatmanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      elif filename.find('.filter.') > 0:
        _filtermanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      elif filename.find('.metadict.') > 0:
        _metadictmanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      elif filename.find('.metaobj.') > 0:
        _metaobjmanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      elif filename.find('.metacmd.') > 0:
        _metacmdmanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      elif filename.find('.langdict.') > 0:
        _multilangmanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      elif filename.find('.textfmt.') > 0:
        _textformatmanager.importXml(self, xmlfile, REQUEST, 1, createIfNotExists)
      xmlfile.close()


    # --------------------------------------------------------------------------
    #  ConfManager.getConfFiles:
    #
    #  Returns configuration-files from $ZMS_HOME/import-Folder
    # --------------------------------------------------------------------------
    def getConfFiles(self, pattern=None):
      filenames = []
      filepath = package_home(globals())+'/import/'
      for filename in os.listdir(filepath):
        path = filepath + os.sep + filename
        mode = os.stat(path)[stat.ST_MODE]
        if not stat.S_ISDIR(mode):
          filenames.append(filename)
      if pattern is not None:
        filenames = filter(lambda x: x.find(pattern) >= 0, filenames)
      return filenames


    """
    ############################################################################    
    ###
    ###   Configuration-Properties Getters
    ###
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ConfManager.getSequence:
    #
    #  Returns sequence.
    # --------------------------------------------------------------------------
    def getSequence(self):
      id = 'acl_sequence'
      if id not in self.objectIds(['Sequence']):
        _sequence.manage_addSequence(self)
      ob = getattr(self,id)
      return ob

    # --------------------------------------------------------------------------
    #  ConfManager.getMediaDb:
    #
    #  Returns mediadb.
    # --------------------------------------------------------------------------
    def getMediaDb(self):
      return getattr(self,'acl_mediadb',None)

    # --------------------------------------------------------------------------
    #  ConfManager.getStylesheet:
    #
    #  Returns stylesheet.
    # --------------------------------------------------------------------------
    def getStylesheet(self, id=None):
      stylesheets = self.getStylesheets()
      if id is None:
        return stylesheets[0]
      else:
        for css in stylesheets:
          if absattr( css.id) == id:
            return css

    # --------------------------------------------------------------------------
    #  ConfManager.getStylesheets:
    #
    #  Returns list of stylesheets.
    # --------------------------------------------------------------------------
    def getStylesheets(self):
      ids = []
      obs = []
      for id in [ 'instance', 'common']:
        container = getattr( self, id, None)
        if container is not None:
          folder = getattr( container, 'css', None)
          if folder is not None:
            for ob in folder.objectValues(['DTML Method','DTML Document']):
              id = absattr( ob.id)
              if id not in ids:
                ids.append( id)
                if absattr( ob.id) == self.getConfProperty('ZMS.stylesheet','style.css'):
                  obs.insert( 0, ob)
                else:
                  obs.append( ob)
      return obs


    """
    ############################################################################    
    ###
    ###   Configuration-Tab Options
    ###
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ConfManager.customize_manage_options:
    # --------------------------------------------------------------------------
    customize_manage_options = [
        {'label':'TAB_SYSTEM','action':'manage_customize'},
        {'label':'TAB_LANGUAGES','action':'manage_customizeLanguagesForm'},
        {'label':'TAB_METADATA','action':'manage_customizeMetadictForm'},
        {'label':'TAB_METAOBJ','action':'manage_customizeMetaobjForm'},
        {'label':'TAB_METACMD','action':'manage_customizeMetacmdForm'},
        {'label':'TAB_WORKFLOW','action':'manage_customizeWorkflowForm'},
        {'label':'TAB_TEXTFORMAT','action':'manage_customizeTextFormatForm'},
        {'label':'TAB_FILTER','action':'manage_customizeFilterForm'},
        {'label':'TAB_DESIGN','action':'manage_customizeDesignForm'},
      ]


    """
    ############################################################################    
    ###
    ###   Configuration-Properties
    ###
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ConfManager.__get_attr_conf_dict__:
    #
    #  Returns property from configuration.
    # --------------------------------------------------------------------------
    def __get_attr_conf_dict__(self):
      return getattr( self, '__attr_conf_dict__', {})

    # --------------------------------------------------------------------------
    #  ConfManager.getConfProperty:
    #
    #  Returns property from configuration.
    #
    #  @param key	The key.
    #  @param default	The default-value.
    #  @return any
    # --------------------------------------------------------------------------
    def getConfProperty(self, key, default=None):
      return self.__get_attr_conf_dict__().get( key, default)

    # --------------------------------------------------------------------------
    #  ConfManager.setConfProperty:
    #
    #  Sets property into configuration.
    #
    #  @param key	The key.
    #  @param value	The value.
    #  @return void
    # --------------------------------------------------------------------------
    def setConfProperty(self, key, value):
      attr_conf_dict = self.__get_attr_conf_dict__()
      if value is None:
        if attr_conf_dict.has_key(key):
          del attr_conf_dict[key]
      else:
        attr_conf_dict[key] = value
      self.__attr_conf_dict__ = attr_conf_dict
      self.__attr_conf_dict__ = self.__attr_conf_dict__.copy()


    """
    ############################################################################    
    ###
    ###   Configuration-System
    ###
    ############################################################################    
    """

    ############################################################################
    #  ConfManager.manage_customizeSystem: 
    #
    #  Customize system properties.
    ############################################################################
    def manage_customizeSystem(self, btn, key, lang, REQUEST, RESPONSE): 
      """ ConfManager.manage_customizeSystem """
      
      message = ''
      params = []
      
      ##### ASP ####
      if key == 'ASP':
        self.setConfProperty('ZMSAdministrator.email',REQUEST.get('zmsadministrator_email',''))
        self.setConfProperty('ASP.ip_or_domain',REQUEST.get('asp_ip_or_domain',''))
        message = self.getZMILangStr('MSG_CHANGED')
      
      ##### Import ####
      elif key == 'Import':
        if btn == 'Import':
          f = REQUEST['file']
          createIfNotExists = 1
          if f:
            filename = f.filename
            self.importConfPackage( f, REQUEST, createIfNotExists)
          else:
            filename = REQUEST['init']
            self.importConfPackage( filename, REQUEST, createIfNotExists)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      ##### History ####
      elif key == 'History':
        old_active = self.getConfProperty('ZMS.Version.active',0)
        new_active = REQUEST.get('active',0)
        old_nodes = self.getConfProperty('ZMS.Version.nodes',['{$}'])
        new_nodes = self.string_list(REQUEST.get('nodes',''))
        self.setConfProperty('ZMS.Version.active',new_active)
        self.setConfProperty('ZMS.Version.nodes',new_nodes)
        nodes = []
        if old_active == 1 and new_active == 0:
          nodes = old_nodes
        if old_active == 1 and new_active == 1:
          nodes = self.difference_list( old_nodes, self.getConfProperty('ZMS.Version.nodes',['{$}']))
        for node in nodes:
          ob = self.getLinkObj( node)
          if ob is not None:
            message += '[%s: %i]'%(node,ob.packHistory())
        message = self.getZMILangStr('MSG_CHANGED')+message
      
      ##### Clients ####
      elif key == 'Clients':
        if btn == 'Change':
          s = REQUEST.get('portal_master','').strip()
          if s != self.getHome().id:
            self.setConfProperty('Portal.Master',s)
          l = []
          for s in REQUEST.get('portal_clients','').split('\n'):
            s = s.strip()
            if s in self.getHome().objectIds(['Folder']):
              l.append(s)
          self.setConfProperty('Portal.Clients',l)
          message = self.getZMILangStr('MSG_CHANGED')
      
      ##### MediaDb ####
      elif key == 'MediaDb':
        if btn == 'Create':
          location = REQUEST['mediadb_location'].strip()
          _mediadb.manage_addMediaDb(self,location)
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Pack':
          message = _mediadb.manage_packMediaDb(self)
        elif btn == 'Remove':
          message = _mediadb.manage_delMediaDb(self)
      
      ##### Custom ####
      elif key == 'Custom':
        if btn == 'Change':
          if len(REQUEST.get('conf_key','')) > 0:
            k = REQUEST.get( 'conf_key')
            v = REQUEST.get( 'conf_value', '')
            try:
              v = self.parseXmlString(self.getXmlHeader() + v)
              self.setConfProperty( k, v)
            except:
              _globals.writeException( self, "[manage_customizeSystem]: can't set conf-property %s=%s"%(str(k),str(v)))
            message = self.getZMILangStr('MSG_CHANGED')
            params.append( 'conf_key')
          else:
            k = REQUEST.get( 'option')
            v = REQUEST.get( 'value', '')
            self.setConfProperty( k, v)
            message = self.getZMILangStr('MSG_CHANGED')
            params.append( 'option')
      
      ##### InstalledProducts ####
      elif key == 'InstalledProducts':
        if btn == 'Change':
          self.setConfProperty('InstalledProducts.pil',REQUEST.get('pil',None))
          self.setConfProperty('InstalledProducts.pil.thumbnail.max',REQUEST.get('pil_thumbnail_max',100))
          self.setConfProperty('InstalledProducts.pil.hires.thumbnail.max',REQUEST.get('pil_hires_thumbnail_max',0))
          message = self.getZMILangStr('MSG_CHANGED')
      
      ##### StandardObjects ####
      elif key == 'StandardObjects':
        meta_types = []
        meta_types.extend(self.dGlobalAttrs.keys())
        meta_types.extend(self.getMetaobjIds())
        for meta_type in meta_types:
          self.setConfProperty('%s.enabled'%meta_type,meta_type in REQUEST.get('meta_types',[]))
        message = self.getZMILangStr('MSG_CHANGED')
      
      ##### Log ####
      elif key == 'Log':
        if btn == 'Create':
          obj = zmslog.ZMSLog()
          self._setObject(obj.id, obj)
          message = 'Log created'
        elif btn == 'Remove':
          self.manage_delObjects(ids=self.objectIds(['ZMS Log']))
          message = 'Log removed'

      # Return with message.
      d = {
      	'lang': lang,
      	'manage_tabs_message': message,
      }
      for param in params:
        d[param] = REQUEST.get( param, '')
      return RESPONSE.redirect( self.url_append_params( 'manage_customize', d) + '#_%s'%key)


    """
    ############################################################################    
    ###
    ###   Configuration-Design
    ###
    ############################################################################    
    """

    ############################################################################
    #  ConfManager.manage_customizeDesign: 
    #
    #  Customize design properties.
    ############################################################################
    def manage_customizeDesign(self, btn, lang, REQUEST, RESPONSE):
      """ ConfManager.manage_customizeDesign """
      message = ''
      cssId = REQUEST.get('cssId','')
      
      # Insert.
      # -------
      if btn == self.getZMILangStr('BTN_INSERT'):
        #-- Stylesheet.
        if REQUEST.has_key('newCssId'):
          title = 'CSSschema'
          data = '<dtml-with content\n><dtml-call "REQUEST.RESPONSE.setHeader(\'Cache-Control\',\'public, max-age=3600\')"\n><dtml-var f_standard_html_request\n><dtml-var f_css_defaults>\n\n</dtml-with>'
          self.common.css.manage_addDTMLMethod( REQUEST.get('newCssId'), title, data)
          message = self.getZMILangStr('MSG_INSERTED')%REQUEST.get('newCssId')
          cssId = REQUEST.get('newCssId')
        
      # Delete.
      # -------
      if btn == self.getZMILangStr('BTN_DELETE'):
        #-- Stylesheet.
        if REQUEST.has_key('cssId'):
          self.common.css.manage_delObjects(ids=[REQUEST.get('cssId')])
          message = self.getZMILangStr('MSG_DELETED')%int(1)
          cssId = ''
        
      # Change.
      # -------
      if btn == self.getZMILangStr('BTN_CHANGE'):
        #-- Stylesheet.
        if REQUEST.has_key('cssId'):
          if REQUEST.get('default'):
            self.setConfProperty('ZMS.stylesheet',REQUEST.get('cssId'))
          css = self.getStylesheet( REQUEST.get('cssId'))
          data = REQUEST.get('stylesheet')
          title = css.title
          css.manage_edit(data,title)
          message = self.getZMILangStr('MSG_CHANGED')
        #-- Sitemap.
        if REQUEST.has_key('attr_layoutsitemap'):
          if len(REQUEST['attr_layoutsitemap'])>0:
            self.attr_layoutsitemap = int(REQUEST['attr_layoutsitemap'])
          elif hasattr(self,'attr_layoutsitemap'):
            delattr(self,'attr_layoutsitemap')
          message = self.getZMILangStr('MSG_CHANGED')
      
      # Upload.
      # -------
      elif btn == self.getZMILangStr('BTN_UPLOAD'):
        #-- Logo.
        self.logo = Image(id='logo', title='', file='')
        self.logo.manage_upload(REQUEST['file'],REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeDesignForm?lang=%s&manage_tabs_message=%s&cssId=%s'%(lang,message,cssId))

################################################################################
