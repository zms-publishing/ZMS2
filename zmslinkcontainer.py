################################################################################
# zmslinkcontainer.py
#
# $Id: zmslinkcontainer.py,v 1.6 2004/11/24 20:54:37 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.6 $
#
# Implementation of class ZMSLinkContainer (see below).
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
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import zmslinkelement
import _globals
import _zreferableitem


################################################################################
################################################################################
###
###   Constructor(s)
###
################################################################################
################################################################################

def manage_addZMSLinkContainer(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSLinkContainer """
  
  ##### Create ####
  id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
  obj = ZMSLinkContainer(self.getNewId(id_prefix),_sort_id+1)
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
  obj.setObjProperty('active',1,lang)
  ##### VersionManager ####
  obj.onChangeObj(REQUEST)
  
  ##### Normalize Sort-IDs ####
  self.normalizeSortIds(id_prefix)
  
  # Return with message.
  message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
  RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,urllib.quote(message)))


################################################################################
################################################################################
###   
###   Class
###   
################################################################################
################################################################################

class ZMSLinkContainer(ZMSContainerObject): 

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSLinkContainer"
    icon = "misc_/zms/zmslinkcontainer.gif"
    icon_disabled = "misc_/zms/zmslinkcontainer_disabled.gif"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',       'action': 'manage_main'},
	{'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_PREVIEW',    'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace','manage_checkout',
		'manage_deleteObjs','manage_undoObjs',
		'manage_properties','manage_changeProperties',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
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
        'active':{'datatype':'boolean','multilang':True},
        'attr_active_start':{'datatype':'datetime','multilang':True},
        'attr_active_end':{'datatype':'datetime','multilang':True},
        'align':{'datatype':'string','type':'select','default':'NONE','options':['NONE', 'NONE', 'LEFT', 'LEFT', 'LEFT_FLOAT', 'LEFT_FLOAT', 'RIGHT', 'RIGHT', 'RIGHT_FLOAT', 'RIGHT_FLOAT']},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/zmslinkcontainer/manage_main', globals())


    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """
    
    ############################################################################
    #  ZMSLinkContainer.manage_changeProperties: 
    #
    #  Change LinkContainer properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE): 
      """ ZMSLinkContainer.manage_changeProperties """
        
      self._checkWebDAVLock()
      message = ''
      
      # Change.
      # -------
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        
        ##### Object State #####
        self.setObjStateModified(REQUEST)
        
        ##### Properties ####
        # Attributes.
        self.setReqProperty('active',REQUEST)
        self.setReqProperty('attr_active_start',REQUEST)
        self.setReqProperty('attr_active_end',REQUEST)
        self.setReqProperty('align',REQUEST)
        
        ##### Change #####
        if REQUEST['btn'] == self.getZMILangStr('BTN_CHANGE'):
          for ob in self.getChildNodes(REQUEST,['ZMSLinkElement']):
            id = ob.id
            url = REQUEST['url%s'%id]
            title = REQUEST['title%s'%id]
            description = REQUEST['description%s'%id]
            zmslinkelement.setZMSLinkElement(ob,title,url,description,REQUEST)
        
        ##### Add #####
        elif REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
          title = REQUEST['_title']
          url = REQUEST['_url']
          description = REQUEST['_description']
          zmslinkelement.addZMSLinkElement(self,title,url,description,REQUEST)
        
        ##### VersionManager ####
        self.onChangeObj(REQUEST)
        
        # Return with message.
        message = self.getZMILangStr('MSG_CHANGED')
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,urllib.quote(message)))
      
      else:
        # Return to parent.
        self.checkIn(REQUEST)
        return RESPONSE.redirect('%s/manage_main?lang=%s#_%s'%(self.getParentNode().absolute_url(),lang,self.id))


    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.isPageElement
    # --------------------------------------------------------------------------
    def isPage( self): 
      return self.getObjProperty('align',self.REQUEST) != 'NONE'

    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.isPage
    # --------------------------------------------------------------------------
    def isPage( self): 
      return False

    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt( self, REQUEST): 
      return self.display_type( REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.getLinkList: 
    #
    #  Returns list of URLs of links.
    #  @deprecated: use implementation that fits your own needs!
    # --------------------------------------------------------------------------
    def getLinkList(self, REQUEST, allow_none=0):
      print "[ZMSLinkContainer.getLinkList]: @deprecated: use implementation that fits your own needs!"
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      try:
        reqBuffId = 'getLinkList%i'%allow_none
        value = self.fetchReqBuff(reqBuffId,REQUEST)
        return value
      except:
      
        #-- Get value.
        value = []
        for ob in self.getChildNodes(REQUEST,['ZMSLinkElement']):
          visible = True
          visible = visible and self.isCommitted(REQUEST) # Object has been committed.
          if visible:
            url = ob.getObjAttrValue(ob.getObjAttr('attr_ref'),REQUEST)
            dct = {}
            dct['src'] = ob
            dct['dst'] = ob.getLinkObj(url,REQUEST)
            dct['url'] = ob.getLinkUrl(url,REQUEST)
            dct['title'] = ob.getObjProperty('title',REQUEST)
            dct['description'] = ob.getObjProperty('attr_dc_description',REQUEST)
            dct['internal'] = _zreferableitem.isInternalLink(url)
            medline = dct['title'].lower()=='medline'
            if medline:
              dct['url'] = _zreferableitem.getMedlineLink(dct['url'])
            if dct['url'] is not None or allow_none:
              value.append(dct)
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff(reqBuffId,value,REQUEST)


    """
    ############################################################################
    ###
    ###   HTML-Presentation
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSLinkContainer._getBodyContent:
    #
    #  HTML presentation of File.
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      # Return body-content.
      align = self.getObjProperty('align',REQUEST)
      subclass = ''
      if align in [ 'LEFT', 'RIGHT']:
        subclass = ' ' + align.lower()
      elif align in [ 'LEFT_FLOAT']:
        subclass = ' floatleft'
      elif align in [ 'RIGHT_FLOAT']:
        subclass = ' floatright'
      if len(subclass) > 0:
        bodyContent = self.renderShort(REQUEST)
        return '<div class="%s%s" id="%s">%s</div>'%( self.meta_type, subclass, self.id, bodyContent)
      return ''


    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.renderShort:
    #
    #  Renders short presentation of Link-Container.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      l = []
      l.append('<div class="%s">\n'%self.meta_type)
      obs = self.getChildNodes(REQUEST,['ZMSLinkElement'])
      obs = filter(lambda x: x.isVisible(REQUEST), obs)
      for ob in obs:
        l.append(ob.renderShort(REQUEST))
      l.append('</div>\n')
      return ''.join(l)


    """
    ############################################################################    
    ###  
    ###  DOM-Methoden 
    ### 
    ############################################################################    
    """
    
    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.getChildNodes:
    #
    #  Returns a NodeList that contains all children of this node in correct sort-order.
    #  If none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST={}, meta_types=None):
      lang = REQUEST.get('lang',None)
      nodelist = ZMSContainerObject.getChildNodes(self,REQUEST,meta_types)
      if lang is None:
        return nodelist
      else:
        return filter(lambda ob: ob.getDCCoverage(REQUEST).find("."+lang)>0,nodelist)

################################################################################
