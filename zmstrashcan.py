################################################################################
# zmstrashcan.py
#
# $Id: zmstrashcan.py,v 1.5 2004/11/23 23:19:31 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.5 $
#
# Implementation of classes ZMSTrashcan (see below).
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
from Globals import HTML, HTMLFile
import copy
import string
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import _globals


################################################################################
################################################################################
###
###   C l a s s
###
################################################################################
################################################################################
class ZMSTrashcan(ZMSContainerObject):

    # Properties.
    # -----------
    meta_type = "ZMSTrashcan"
    icon = "misc_/zms/zmstrashcan.gif"
    icon_disabled = "misc_/zms/zmstrashcan_disabled.gif"
    
    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TYPE_ZMSTRASHCAN', 'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES',   'action': 'manage_properties'},
	) 

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_eraseObjs','manage_moveObjUp','manage_moveObjDown','manage_cutObjects',
		'manage_userForm','manage_user',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)

    # Management Interface.
    # ---------------------
    manage_properties = HTMLFile('dtml/zmstrashcan/manage_properties', globals())

    # Properties.
    # -----------
    __obj_attrs__ = {}

    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSTrashcan.manage_changeProperties: 
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST=None): 
      """ ZMSTrashcan.manage_changeProperties """
      
      if REQUEST.get('btn','') in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        return REQUEST.RESPONSE.redirect('manage_main?lang=%s'%lang)
        
      ##### Garbage Collection #####
      setattr(self,'garbage_collection',REQUEST.get('garbage_collection',''))
      self.run_garbage_collection(forced=1)
      
      # Return with message.
      message = self.getZMILangStr('MSG_CHANGED')
      if REQUEST and hasattr(REQUEST,'RESPONSE'):
        if REQUEST.RESPONSE:
          return REQUEST.RESPONSE.redirect('manage_properties?lang=%s&manage_tabs_message=%s'%(lang,urllib.quote(message)))


    # --------------------------------------------------------------------------
    #  ZMSTrashcan.run_garbage_collection:
    #
    #  Runs garbage collection.
    # --------------------------------------------------------------------------
    def run_garbage_collection(self, forced=0):
      now = time.time()
      last_run = getattr(self,'last_garbage_collection',None)
      if forced or \
         last_run is None or \
         _globals.daysBetween(last_run,now)>1:
        #-- Get days.
        days = getattr(self,'garbage_collection','2')
        try: days = int(days)
        except: return
        #-- Get IDs.
        ids = []
        for ob in self.objectValues(self.dGlobalAttrs.keys()):
          delete = True
          for lang in self.getLangIds():
            req = {'lang':lang,'preview':'preview'}
            change_dt = ob.getObjProperty('change_dt',req)
            if change_dt is not None:
              delete = delete and _globals.daysBetween(change_dt,now)>days
          if delete:
            ids.append(ob.id)
        #-- Delete objects.
        self.manage_delObjects(ids=ids)
        #-- Update time-stamp.
        setattr(self,'last_garbage_collection',now)
    

    # --------------------------------------------------------------------------
    #  ZMSTrashcan._verifyObjectPaste:
    #
    #  Overrides _verifyObjectPaste of OFS.CopySupport.
    # --------------------------------------------------------------------------
    def _verifyObjectPaste(self, object, validate_src=1): 
      return

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.getDCCoverage:
    #
    #  Overrides getDCCoverage of ZMSObject.
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}): 
      return 'global.'+self.getPrimaryLanguage()

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.isActive
    # --------------------------------------------------------------------------
    def isActive(self, REQUEST): 
      return len(self.getChildNodes(REQUEST))>0

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.getTitle
    # --------------------------------------------------------------------------
    def getTitle(self, REQUEST): 
      return self.display_type(REQUEST) + " (" + str(len(self.getChildNodes(REQUEST))) + " " + self.getLangStr('ATTR_OBJECTS',REQUEST['lang']) + ")"

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt(self, REQUEST): 
      return self.display_type(REQUEST)

################################################################################
