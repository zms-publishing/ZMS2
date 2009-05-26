################################################################################
# zmsfolder.py
#
# $Id: $
# $Name: $
# $Author: $
# $Revision: $
#
# Implementation of class ZMSFolder (see below).
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
from Globals import HTMLFile
import string
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import _globals


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################

manage_addZMSFolderForm = HTMLFile('manage_addzmsfolderform', globals()) 
def manage_addZMSFolder(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSFolder """

  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSFolder(self.getNewId(id_prefix),_sort_id+1)
    self._setObject(obj.id, obj)
    
    obj = getattr(self,obj.id)
    ##### Object State ####
    obj.setObjStateNew(REQUEST)
    ##### Init Properties ####
    obj.manage_changeProperties(lang,REQUEST)
    
    ##### Normalize Sort-IDs ####
    self.normalizeSortIds(id_prefix)
    
    # Return with message.
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    target = REQUEST.get( 'target', '%s/%s/manage_main'%( self.absolute_url(), obj.id))
    RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))
          
  else:         
    target = REQUEST.get( 'target', '%s/manage_main'%self.absolute_url())
    RESPONSE.redirect('%s?preview=preview&lang=%s'%(target,lang))



################################################################################
################################################################################
###
###   C l a s s
###
################################################################################
################################################################################
class ZMSFolder(ZMSContainerObject):

    # Properties.
    # -----------
    meta_type = meta_id = 'ZMSFolder'
    icon = "misc_/zms/zmsfolder.gif"
    icon_disabled = "misc_/zms/zmsfolder_disabled.gif"
    
    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',         'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES',   'action': 'manage_properties'},
	{'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'},
	{'label': 'TAB_TASKS',        'action': 'manage_tasks'},
	{'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'},
	{'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_PREVIEW',      'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_addZMSFolder','manage_addZMSDocument','manage_addZMSTextarea','manage_addZMSGraphic','manage_addZMSTable','manage_addZMSFile','manage_addZMSTeaserContainer','manage_addZMSNote','manage_addZMSLinkContainer','manage_addZMSLinkElement','manage_addZMSSqlDb','manage_addZMSModule',
		'manage_deleteObjs','manage_undoObjs','manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs','manage_ajaxDragDrop',
		'manage_properties','manage_changeProperties',
		'manage_search','manage_search_attrs','manage_tasks',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm', 'manage_user',
		'manage_importexport', 'manage_import', 'manage_export',
		)
    __administratorPermissions__ = (
		'manage_addZMSSysFolder',
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
        'title':{'datatype':'string','multilang':True,'size':40, 'mandatory': True},
        'titleshort':{'datatype':'string','multilang':True,'size':20, 'mandatory': True},
        'titleimage':{'datatype':'image','multilang':True},
        'levelnfc':{'datatype':'string','type':'select','options':[0,0,1,1,2,2],'label':'ATTR_LEVELNFC'},
        'attr_cacheable':{'datatype':'int','type':'select','options':[0,0,1,1,2,2],'default':True,'label':'ATTR_CACHEABLE'},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }

################################################################################
