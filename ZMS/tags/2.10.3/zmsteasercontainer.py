################################################################################
# zmsteasercontainer.py
#
# $Id: zmsteasercontainer.py,v 1.5 2004/11/23 23:04:51 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.5 $
#
# Implementation of class ZMSTeaserContainer (see below).
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

def manage_addZMSTeaserContainer(self, lang, manage_lang, _sort_id, REQUEST):
  """ manage_addZMSTeaserContainer """
  
  ##### Create ####
  id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
  obj = ZMSTeaserContainer(self.getNewId(id_prefix),_sort_id+1)
  self._setObject(obj.id, obj)
    
  obj = getattr(self,obj.id)
  ##### VersionManager ####
  obj.setObjStateNew(REQUEST)
  ##### Init Coverage ####
  coverage = self.getDCCoverage(REQUEST)
  if coverage.find('local.')==0:
    obj.setObjProperty('attr_dc_coverage',coverage)
  else:
    obj.setObjProperty('attr_dc_coverage','global.'+lang)
  ##### Init Properties ####
  obj.setObjProperty('active',1,lang)
  for key in ['attr_borderstyle','attr_bgcolor_border','attr_bgcolor_title','attr_bgcolor_text']:
    obj_attr = obj.getObjAttr(key)
    obj.setObjProperty(key,self.getConfProperty('%s.defaults.%s'%(obj.meta_type,key),obj_attr['default']),lang)
  ##### VersionManager ####
  obj.onChangeObj(REQUEST)
            
  ##### Normalize Sort-IDs ####
  self.normalizeSortIds(id_prefix)
        
  # Return with message.        
  if REQUEST.RESPONSE:
    message = self.getLangStr('MSG_INSERTED',manage_lang)%obj.display_type(REQUEST)
    REQUEST.RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,manage_lang,urllib.quote(message)))


################################################################################

lstPenetrance = [
  0,'this',
  1,'sub_nav',
  2,'sub_all'
]

################################################################################
################################################################################
###   
###   C l a s s
###   
################################################################################
################################################################################

class ZMSTeaserContainer(ZMSContainerObject):

    # Properties.
    # -----------
    meta_type = "ZMSTeaserContainer"
    icon = "misc_/zms/zmsteaser.gif"
    icon_disabled = "misc_/zms/zmsteaser_disabled.gif"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',       'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES', 'action': 'manage_properties'},
	{'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'},
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_addZMSTeaserElement','manage_addZMSNote',
		'manage_deleteObjs','manage_undoObjs','manage_moveObjUp','manage_moveObjDown','manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_properties','manage_changeProperties',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm','manage_user',
		)
    __administratorPermissions__ = (
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
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
        'active':{'datatype':'boolean','multilang':True},
        'attr_active_start':{'datatype':'datetime','multilang':True},
        'attr_active_end':{'datatype':'datetime','multilang':True},
        'attr_borderstyle':{'datatype':'int','default':True},
        'attr_bgcolor_border':{'datatype':'color','default':'primColorStrong0'},
        'attr_bgcolor_title':{'datatype':'color','default':'primColorLight0'},
        'attr_bgcolor_text':{'datatype':'color','default':'neutralColorWhite'},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
    }


    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """

    # Management Interface.
    # ---------------------
    manage_properties = HTMLFile('dtml/zmsteasercontainer/manage_properties',globals()) 

    ############################################################################
    #  ZMSTeaserContainer.manage_changeProperties: 
    #
    #  Change Teaser properties.
    ############################################################################
    def manage_changeProperties(self, lang, manage_lang, REQUEST, RESPONSE): 
      """ ZMSTeaserContainer.manage_changeProperties """
        
      if REQUEST.get('btn','') in  [ self.getLangStr('BTN_CANCEL',manage_lang), self.getLangStr('BTN_BACK',manage_lang)]:
        return RESPONSE.redirect('manage_main?lang=%s&manage_lang=%s'%(lang,manage_lang))
      
      ##### Object State #####
      self.setObjStateModified(REQUEST)
      
      ##### Properties #####
      # Active.
      self.setReqProperty('active',REQUEST)
      self.setReqProperty('attr_active_start',REQUEST)
      self.setReqProperty('attr_active_end',REQUEST)
      # Styles.
      for key in ['attr_borderstyle','attr_bgcolor_border','attr_bgcolor_title','attr_bgcolor_text']:
        self.setReqProperty(key,REQUEST)
        # Set defaults for next initialization.
        self.setConfProperty('%s.defaults.%s'%(self.meta_type,key),self.getObjProperty(key,REQUEST))
      
      ##### Metadata #####
      self.setMetadata(lang,manage_lang,REQUEST)
      
      ##### VersionManager ####
      self.onChangeObj(REQUEST)
      
      # Return with message.
      message = self.getLangStr('MSG_CHANGED',manage_lang)
      RESPONSE.redirect('manage_properties?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(lang,manage_lang,urllib.quote(message)))


    # --------------------------------------------------------------------------
    #  ZMSTeaserContainer.isPage:
    # --------------------------------------------------------------------------
    def isPage( self): 
      return False

    # --------------------------------------------------------------------------
    #  ZMSTeaserContainer.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt( self, REQUEST): 
      return self.display_type(REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTeaserContainer.getTitle
    # --------------------------------------------------------------------------
    def getTitle( self, REQUEST): 
      return self.getParentNode().getTitle(REQUEST)


    """
    ############################################################################
    ###
    ###  H T M L - P r e s e n t a t i o n 
    ###
    ############################################################################
    """

    # preload display interface
    rendershort_default = HTMLFile('dtml/zmsteasercontainer/rendershort_default', globals()) 
    element_icon = HTMLFile('dtml/zmsteasercontainer/element_icon', globals()) 

    # --------------------------------------------------------------------------
    #  ZMSTeaserContainer.renderShort:
    #
    #  Renders short presentation of a Teaser-Container.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      # Retrieve properties.
      res = self.getChildNodes(REQUEST,['ZMSTeaserElement','ZMSCustom'])
      # Return <html>-presentation.
      return self.rendershort_default(self,res=res,REQUEST=REQUEST)

################################################################################
