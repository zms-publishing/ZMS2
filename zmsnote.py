################################################################################
# zmsnote.py
#
# $Id: zmsnote.py,v 1.4 2004/11/23 23:04:48 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.4 $
#
# Implementation of class ZMSNote (see below).
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
import string
import urllib
# Product Imports.
from zmsobject import ZMSObject
import _globals


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################

def manage_addZMSNote(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSNote """

  ##### Create ####    
  id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
  obj = ZMSNote(self.getNewId(id_prefix),_sort_id+1)
  self._setObject(obj.id, obj)
    
  obj = getattr(self,obj.id)
  ##### Object State ####
  obj.setObjStateNew(REQUEST)
  ##### Init Coverage ####
  coverage = self.getDCCoverage(REQUEST)
  if coverage.find('local.')==0:
    obj.setObjProperty('attr_dc_coverage',coverage)
  else:
    obj.setObjProperty('attr_dc_coverage','global.'+lang)
  ##### Init Properties ####
  obj.manage_changeProperties(lang,REQUEST,RESPONSE)
  ##### VersionManager ####
  obj.onChangeObj(REQUEST)
            
  ##### Normalize Sort-IDs ####
  self.normalizeSortIds(id_prefix)
        
  # Return with message.        
  if REQUEST.RESPONSE:
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    REQUEST.RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,urllib.quote(message)))


################################################################################
################################################################################
###   
###   Class
###   
################################################################################
################################################################################

class ZMSNote(ZMSObject):

    # Properties.
    # -----------
    meta_type = "ZMSNote"
    icon = "misc_/zms/zmsnote.gif"
    icon_disabled = "misc_/zms/zmsnote.gif"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',       'action': 'manage_main'},
	{'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'},
	) 

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace','manage_checkout',
		'manage_changeProperties',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_userForm','manage_user',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
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
        'master_version':{'datatype':'int','xml':False,'default':0},
        'major_version':{'datatype':'int','xml':False,'default':0},
        'minor_version':{'datatype':'int','xml':False,'default':0},
        # Properties
        'text':{'datatype':'string','multilang':True,'type':'text','size':50},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/zmsnote/manage_main', globals())


    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSNote.manage_changeProperties: 
    #
    #  Change Note properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE): 
      """ ZMSNote.manage_changeProperties """
      
      self._checkWebDAVLock()
      message = ''
      
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        
        ##### Object State #####
        self.setObjStateModified(REQUEST)
          
        ##### Properties #####
        for key in self.getObjAttrs().keys():
          self.setReqProperty(key,REQUEST)
          
        ##### VersionManager ####
        self.onChangeObj(REQUEST)
          
        ##### Message #####
        message = self.getZMILangStr('MSG_CHANGED')
        
      # Return with message.
      self.checkIn(REQUEST)
      return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(self.getParentNode().absolute_url(),lang,urllib.quote(message),self.id))


    # --------------------------------------------------------------------------
    #	ZMSNote.isActive
    # --------------------------------------------------------------------------
    def isActive(self,REQUEST): return 1 # Always active.

    # --------------------------------------------------------------------------
    #	ZMSNote.isVisible
    # --------------------------------------------------------------------------
    def isVisible(self,REQUEST): return 0 # Always invisible.

    # --------------------------------------------------------------------------
    #	ZMSNote.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt(self,REQUEST): return self.display_type(REQUEST)

    # --------------------------------------------------------------------------
    #	ZMSNote.getText
    # --------------------------------------------------------------------------
    def getText(self,REQUEST): return self.getObjProperty('text',REQUEST,'')


    """
    ############################################################################
    ###
    ###  H T M L - P r e s e n t a t i o n 
    ###
    ############################################################################
    """

    # preload display interface for notes
    rendershort_default = HTMLFile('dtml/zmsnote/rendershort_default', globals()) 

    # --------------------------------------------------------------------------
    #  ZMSNote.renderShort:
    #
    #  Renders short presentation of a Note.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      return self.rendershort_default(self,text=self.getText(REQUEST),REQUEST=REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSNote.printHtml:
    #
    #  Renders print presentation of a Note.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      return '<!--%s-->'%self.getText(REQUEST)

################################################################################
