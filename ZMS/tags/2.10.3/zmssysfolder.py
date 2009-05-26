################################################################################
# zmssysfolder.py
#
# $Id: zmssysfolder.py,v 1.4 2004/11/23 23:04:50 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.4 $
#
# Implementation of class ZMSSysFolder (see below).
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
from Globals import HTML, HTMLFile
import os
import string 
import urllib
import tempfile
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import _fileutil
import _globals


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################

manage_addZMSSysFolderForm = HTMLFile('manage_addzmssysfolderform', globals()) 
def manage_addZMSSysFolder(self, lang, manage_lang, _sort_id, REQUEST):
  """ manage_addZMSSysFolder """
  
  if REQUEST['btn'] == self.getLangStr('BTN_INSERT',manage_lang):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSSysFolder(self.getNewId(id_prefix),_sort_id+1)
    self._setObject(obj.id, obj)
        
    obj = getattr(self,obj.id)
    ##### Object State ####
    obj.setObjStateNew(REQUEST)
    ##### Init Properties ####
    obj.manage_changeProperties(lang,manage_lang,REQUEST)
    ##### VersionManager ####
    obj.onChangeObj(REQUEST)

    ##### Normalize Sort-IDs ####
    self.normalizeSortIds(id_prefix)
                
    # Return with message.
    message = self.getLangStr('MSG_INSERTED',manage_lang)%obj.display_type(REQUEST)
    if REQUEST.RESPONSE:
      REQUEST.RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,manage_lang,urllib.quote(message)))
          
  else:         
    if REQUEST.RESPONSE:
      REQUEST.RESPONSE.redirect('%s/manage_main?lang=%s&manage_lang=%s'%(self.absolute_url(),lang,manage_lang))


################################################################################
################################################################################
###   
###   C l a s s
###   
################################################################################
################################################################################

class ZMSSysFolder(ZMSContainerObject):
        
    # Properties.
    # -----------
    meta_type = "ZMSSysFolder"
    icon = "misc_/zms/zmssysfolder.gif"
    icon_disabled = "misc_/zms/zmssysfolder_disabled.gif"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',       'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES', 'action': 'manage_properties'},
	{'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'},
	{'label': 'TAB_SECURITY',   'action': 'manage_access'},
	{'label': 'TAB_OWNERSHIP',  'action': 'manage_owner'},
	{'label': 'TAB_SEARCH',     'action': 'manage_FindForm'},
	{'label': 'TAB_REFERENCES', 'action': 'manage_RefForm'},
	{'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_PREVIEW',    'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_deleteObjs','manage_undoObjs','manage_moveObjUp','manage_moveObjDown','manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_properties','manage_changeProperties',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm','manage_user',
		)
    __administratorPermissions__ = (
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		('ZMS Administrator', __administratorPermissions__),
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
        'work_uid':{'datatype':'string','multilang':True,'xml':False,'lang_inherit':False},
        'work_dt':{'datatype':'datetime','multilang':True,'xml':False,'lang_inherit':False},
        # Properties
        'active':{'datatype':'boolean','multilang':True},
        'attr_active_start':{'datatype':'datetime','multilang':True},
        'attr_active_end':{'datatype':'datetime','multilang':True},
        'title':{'datatype':'string','multilang':True,'size':40},
        'titleshort':{'datatype':'string','multilang':True,'size':20},
        'titleimage':{'datatype':'image','multilang':True},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/zmssysfolder/manage_main', globals()) 
    manage_importexport = HTMLFile('dtml/zmssysfolder/manage_importexport', globals()) 


    """
    ############################################################################    
    #
    #   CONSTRUCTOR
    #
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #	ZMSSysFolder.getHref2IndexHtml:
    #
    #   Reference to index_html.
    # --------------------------------------------------------------------------
    def getHref2IndexHtml(self, REQUEST, deep=1):
      href = self.absolute_url()
      if REQUEST.get('lang','') != '': href = self.url_append_params(href,{'lang':REQUEST['lang']})
      if REQUEST.get('preview','') == 'preview': href = self.url_append_params(href,{'preview':'preview'})
      return href

    # --------------------------------------------------------------------------
    #	ZMSSysFolder.getHref2SitemapHtml:
    #
    #   Reference to sitemap_html.
    # --------------------------------------------------------------------------
    def getHref2SitemapHtml(self, REQUEST): 
      return self.getParentNode().getHref2SitemapHtml(REQUEST)


    """
    ############################################################################    
    ###  
    ###  Override methods from CopySupport
    ### 
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #	ZMSSysFolder._get_id:
    #
    #	Allow containers to override the generation of
    #	object copy id by attempting to call its _get_id
    #	method, if it exists.
    # --------------------------------------------------------------------------
    def _get_id(self, id):
      newId = id
      while newId in self.objectIds():
        newId = 'copy_of_%s'%newId
      return newId


    ############################################################################    
    #  ZMSSysFolder.manage_import:
    #
    #  Import files.
    ############################################################################    
    def manage_import(self, file, lang, manage_lang, REQUEST, RESPONSE=None):
      """ ZMSSysFolder.manage_import """
      
      message = ''
      
      # Create temporary folder.
      folder = tempfile.mktemp()
      os.mkdir(folder)
      
      # Save to temporary file.
      filename = _fileutil.getOSPath('%s/%s'%(folder,_fileutil.extractFilename(file.filename)))
      _fileutil.exportObj(file,filename)
      if _fileutil.extractFileExt(filename) == 'zip':
        _fileutil.extractZipArchive(filename)
        _fileutil.remove(filename)

      # Import temporary file.
      _fileutil.importPath(self,folder)
      
      # Remove temporary files.
      _fileutil.remove(folder,deep=1)
      
      # Return with message.
      message += self.getLangStr('MSG_IMPORTED',manage_lang)%('<i>%s</i>'%_fileutil.extractFilename(file.filename))
      if RESPONSE:
        message = urllib.quote(message)
        return REQUEST.RESPONSE.redirect('manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(lang,manage_lang,message))

################################################################################
