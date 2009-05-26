################################################################################
# zmscontainerobject.py
#
# $Id: zmscontainerobject.py,v 1.10 2004/11/24 20:54:37 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.10 $
#
# Implementation of class ZMSContainerObject (see below).
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
from App.Common import package_home
from Globals import HTMLFile
import AccessControl.Role
import copy
import string 
import urllib
import time
# Product Imports.
from zmsobject import ZMSObject
from _metadata import Metadata
import zmsteaserelement
import _accessmanager
import _fileutil
import _globals
import _importable
import _objattrs
import _scormlib
import _versionmanager
import _ztrashcanclient


# ------------------------------------------------------------------------------
#  zmscontainerobject.isPageWithElements:
# ------------------------------------------------------------------------------
def isPageWithElements(obs):
  for ob in obs:
    if ob.isPageElement():
      return True
  return False


# ------------------------------------------------------------------------------
#  zmscontainerobject.getPrevSibling: 
#
#  The node immediately preceding this node, otherwise returns None. 
# ------------------------------------------------------------------------------
def getPrevSibling(self, REQUEST, incResource=False):
  parent = self.getParentNode()
  if parent is not None:
    siblings = parent.getChildNodes(REQUEST,[self.PAGES,self.NORESOLVEREF]) 
    if self in siblings:
      i = siblings.index(self) - 1
      while i >= 0:
        ob = siblings[i]
        if ob.isVisible(REQUEST) and (incResource or not ob.isResource(REQUEST)):
          return ob
        i = i - 1
  return None

# ------------------------------------------------------------------------------
#  zmscontainerobject.getNextSibling: 
#
#  The node immediately following this node, otherwise returns None. 
# ------------------------------------------------------------------------------
def getNextSibling(self, REQUEST, incResource=False):
  parent = self.getParentNode()
  if parent is not None:
    siblings = parent.getChildNodes(REQUEST,[self.PAGES,self.NORESOLVEREF]) 
    siblingIds = map( lambda x: x.id, siblings)
    if self.id in siblingIds:
      i = siblingIds.index( self.id) + 1
      while i < len(siblings):
        ob = siblings[i]
        if ob.isVisible(REQUEST) and (incResource or not ob.isResource(REQUEST)):
          return ob
        i = i + 1
  return None



################################################################################
################################################################################
###
###   A b s t r a c t   C l a s s
###
###   This is the abstract base class for all ZMS-Container Objects.
###
################################################################################
################################################################################
class ZMSContainerObject(
	ZMSObject, 
	Metadata, 
	AccessControl.Role.RoleManager,		# Security manager. 
	_accessmanager.AccessableContainer,	# Access manager.
	_importable.Importable,
	_scormlib.SCORMLib,
	_versionmanager.VersionManagerContainer,
	_ztrashcanclient.ZTrashcanClient
	):

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_system',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    # Interface.
    # ----------
    pageelement_TOC = HTMLFile('dtml/zmscontainerobject/pageelement_toc', globals())
    pageelement_Teaser = HTMLFile('dtml/zmsteasercontainer/pageelement_teaser', globals())
    bodyContent_Teaser = HTMLFile('dtml/zmsteasercontainer/pageelement_teaser', globals()) # DEPRECATED!
    
    # Management Interface.
    # ---------------------
    zmscontainerobject_input_js = HTMLFile('dtml/zmscontainerobject/input_js', globals()) # JavaScript
    zmslinkelement_input_js = HTMLFile('dtml/zmslinkelement/input_js', globals()) # JavaScript
    zmsfile_input_js = HTMLFile('dtml/zmsfile/input_js', globals()) # JavaScript
    main_js = HTMLFile('dtml/zmscontainerobject/main_js', globals()) # JavaScript
    manage_main = HTMLFile('dtml/zmscontainerobject/manage_main', globals()) 
    manage_main_btn = HTMLFile('dtml/zmscontainerobject/manage_main_btn', globals()) # Buttons
    manage_main_change = HTMLFile('dtml/zmscontainerobject/manage_main_change', globals()) # Change (Author & Date)
    manage_main_actions = HTMLFile('dtml/zmscontainerobject/manage_main_actions', globals()) # Actions
    manage_search = HTMLFile('dtml/zmscontainerobject/manage_search', globals()) 
    manage_search_attrs = HTMLFile('dtml/zmscontainerobject/manage_search_attrs', globals()) 
    manage_properties = HTMLFile('dtml/zmscontainerobject/manage_properties', globals())
    manage_form = HTMLFile('dtml/zmscontainerobject/manage_form', globals())
    manage_system = HTMLFile('dtml/zmscontainerobject/manage_system', globals())
    manage_importexport = HTMLFile('dtml/zmscontainerobject/manage_importexport', globals()) 
    manage_importexportFtp = HTMLFile('dtml/zmscontainerobject/manage_importexportftp', globals()) 


    # Sitemap.
    # --------
    sitemap_layout0 = HTMLFile('dtml/zmscontainerobject/sitemap/version0', globals()) 
    sitemap_layout1 = HTMLFile('dtml/zmscontainerobject/sitemap/version1', globals()) 
    sitemap_layout2 = HTMLFile('dtml/zmscontainerobject/sitemap/version2', globals())
    sitemap_layout3 = HTMLFile('dtml/zmscontainerobject/sitemap/version3', globals())


    # Role Manager.
    # -------------    
    def manage_addZMSCustom(self, meta_id, values={}, REQUEST=None):
      values['meta_id'] = meta_id
      return self.manage_addZMSObject('ZMSCustom',values,REQUEST)
    def manage_addZMSFolder(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSFolder',values,REQUEST)
    def manage_addZMSDocument(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSDocument',values,REQUEST)
    def manage_addZMSFile(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSFile',values,REQUEST)
    def manage_addZMSGraphic(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSGraphic',values,REQUEST)
    def manage_addZMSNote(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSNote',values,REQUEST)
    def manage_addZMSLinkContainer(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSLinkContainer',values,REQUEST)
    def manage_addZMSLinkElement(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSLinkElement',values,REQUEST)
    def manage_addZMSSqlDb(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSSqlDb',values,REQUEST)
    def manage_addZMSSysFolder(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSSysFolder',values,REQUEST)
    def manage_addZMSTable(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSTable',values,REQUEST)
    def manage_addZMSTeaserContainer(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSTeaserContainer',values,REQUEST)
    def manage_addZMSTeaserElement(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSTeaserElement',values,REQUEST)
    def manage_addZMSTextarea(self, values={}, REQUEST=None):
      return self.manage_addZMSObject('ZMSTextarea',values,REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.manage_addZMSObject:
    # --------------------------------------------------------------------------
    def manage_addZMSObject(self, meta_type, values, REQUEST):
      
      attrs = []
      for key in values.keys():
        attrs.extend([key,values[key]])
      
      # Get id.
      if 'id_prefix' in attrs:
        i = attrs.index('id_prefix')
        id_prefix = attrs[i+1]
        id = self.getNewId(id_prefix)
        del attrs[i] # Key.
        del attrs[i] # Value.
      elif 'id' in attrs:
        i = attrs.index('id')
        id = attrs[i+1]
        del attrs[i] # Key.
        del attrs[i] # Value.
      else:
        id = self.getNewId()
      
      # Get sort id.
      key = 'sort_id'
      if key in attrs and attrs.index(key)%2 == 0:
        i = attrs.index(key)
        sort_id = attrs[i+1]
        del attrs[i] # Key.
        del attrs[i] # Value.
      else:
        sort_id = 99999
      
      # Create new object.
      newNode = self.dGlobalAttrs[meta_type]['obj_class'](id,sort_id)
      self._setObject(newNode.id, newNode)
      node = getattr(self,newNode.id)
      
      # Init meta object.
      key = 'meta_id'
      if meta_type == 'ZMSCustom' and key in attrs and attrs.index(key)%2 == 0:
        i = attrs.index(key)
        meta_id = attrs[i+1]
        setattr(node,key,meta_id)
        del attrs[i] # Key.
        del attrs[i] # Value.
      
      # Object state.
      node.setObjStateNew(REQUEST)
      
      # Init properties.
      key = 'active'
      if not (key in attrs and attrs.index(key)%2 == 0):
        attrs.extend([key,1])
      for i in range(len(attrs)/2):
        key = attrs[i*2]
        value = attrs[i*2+1]
        node.setObjProperty(key,value,REQUEST['lang'])
      
      # Version manager.
      node.onChangeObj(REQUEST)
      
      # Normalize sort-ids.
      self.normalizeSortIds(_globals.id_prefix(id))
      
      # Return object.
      return node


    """
    ############################################################################    
    ###
    ###   T r a s h c a n
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSContainerObject.manage_eraseObjs:
    #
    #  Delete a subordinate object:
    #  The objects specified in 'ids' get deleted.
    ############################################################################
    def manage_eraseObjs(self, lang, ids, REQUEST, RESPONSE=None):
      """ ZMSContainerObject.manage_eraseObjs """ 
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      count = len(ids)
      self.manage_delObjects(ids=ids)
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_DELETED')%count
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('target','manage_main')
        return RESPONSE.redirect('%s?lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    ############################################################################
    #  ZMSContainerObject.manage_undoObjs:
    #
    #  Undo a subordinate object:
    #  The objects specified in 'ids' get undone.
    ############################################################################
    def manage_undoObjs(self, lang, ids, REQUEST, RESPONSE=None):
      """ ZMSContainerObject.manage_undoObjs """ 
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      c = 0
      for child in self.getChildNodes():
        if child.id in ids:
          if child.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST):
            child.rollbackObjChanges( self, REQUEST)
            c += 1
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_UNDONE')%c
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('target','manage_main')
        return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    ############################################################################
    #  ZMSContainerObject.manage_deleteObjs:
    #
    #  Delete a subordinate object:
    #  The objects specified in 'ids' get deleted.
    ############################################################################
    def manage_deleteObjs(self, lang, ids, REQUEST, RESPONSE=None):
      """ ZMSContainerObject.manage_deleteObjs """ 
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      versionMgrCntnrs = []
      for child in self.getChildNodes():
        if child.id in ids:
          if child.inObjStates(['STATE_NEW'],REQUEST):
            self.moveObjsToTrashcan([child.id], REQUEST)
          else:
            child.setObjStateDeleted(REQUEST)
            versionMgrCntnr = child.getVersionManagerContainer()
            if versionMgrCntnr not in versionMgrCntnrs:
              versionMgrCntnrs.append( versionMgrCntnr)
      
      ##### VersionManager ####
      for versionMgrCntnr in versionMgrCntnrs:
        versionMgrCntnr.onChangeObj(REQUEST)
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_TRASHED')%len(ids)
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('target','manage_main')
        return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    """
    ############################################################################
    ###
    ###  Properties
    ###
    ############################################################################
    """

    ############################################################################
    #  ZMSContainerObject.manage_changeProperties: 
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST=None): 
      """ ZMSContainerObject.manage_changeProperties """
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      target = REQUEST.get( 'target', 'manage_main')
      
      if REQUEST.get('btn','') not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        
        ##### Object State #####
        self.setObjStateModified(REQUEST)
        
        ##### Properties #####
        root = self.getHome()
        # Title.
        self.setReqProperty('title',REQUEST)
        self.setReqProperty('titleshort',REQUEST)
        self.setReqProperty('titleimage',REQUEST)
        # Active.
        self.setReqProperty('active',REQUEST)
        self.setReqProperty('attr_active_start',REQUEST)
        self.setReqProperty('attr_active_end',REQUEST)
        # Levelnfc
        if 'levelnfc' in self.getObjAttrs().keys():
          self.setReqProperty('levelnfc',REQUEST)
        # Cacheable
        if REQUEST['AUTHENTICATED_USER'].has_permission('ZMS Administrator',self) and \
           'attr_cacheable' in self.getObjAttrs().keys() and self.getConfProperty('ZMS.cache.active')==1:
          self.setReqProperty('attr_cacheable',REQUEST)
        
        ##### Metadata #####
        self.setMetadata(lang,REQUEST)
        
        ##### VersionManager ####
        self.onChangeObj(REQUEST)

        ##### Message ####
        message = self.getZMILangStr('MSG_CHANGED') + ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      
      # Return with message.
      if REQUEST and hasattr(REQUEST,'RESPONSE'):
        if REQUEST.RESPONSE:
          RESPONSE = REQUEST.RESPONSE
          target = self.url_append_params( target, { 'lang': lang, 'preview': 'preview', 'manage_tabs_message': message})
          target = '%s#_%s'%( target, self.id)
          return RESPONSE.redirect( target)


    # --------------------------------------------------------------------------
    #	ZMSContainerObject.isPage:
    # --------------------------------------------------------------------------
    def isPage( self): 
      return True


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getLevelnfc
    # --------------------------------------------------------------------------
    def _getLevelnfc(self, REQUEST):
      s = ''
      if self.getLevel() > 0:
        parent = self.getParentNode()
        if hasattr(parent,'_getLevelnfc') and parent.getLevel() < self.getLevel():
          s = parent._getLevelnfc(REQUEST)
        levelnfc = parent.getObjProperty('levelnfc',REQUEST)
        if len(levelnfc) > 0:
          siblings = parent.filteredChildNodes(REQUEST,self.PAGES)
          if self in siblings:
            i = siblings.index(self)
            if levelnfc == '0':
              s += str(i + 1) + '.'        
            elif levelnfc == '1':
              s += chr(i + ord('A')) + '.'
            elif levelnfc == '2':
              s += chr(i + ord('a')) + '.'
      return s

    def getLevelnfc(self, REQUEST):
      s = ''
      if self.getLevel() > 0:
        parent = self.getParentNode()
        if parent is not None:
          levelnfc = parent.getObjProperty('levelnfc',REQUEST)
          if len(levelnfc) > 0:
            s = self._getLevelnfc(REQUEST)
            if len(s) > 0: s += ' '
      return s


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getTitle
    # --------------------------------------------------------------------------
    def getTitle( self, REQUEST): 
      title = self.getLevelnfc(REQUEST) + self.getObjProperty('title',REQUEST)
      if len(title) == 0: title = self.display_type(REQUEST)
      return title


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt( self, REQUEST): 
      titlealt = self.getLevelnfc(REQUEST) + self.getObjProperty('titleshort',REQUEST)
      if len(titlealt) == 0: titlealt = self.display_type(REQUEST)
      return titlealt


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getTitleimage
    # --------------------------------------------------------------------------
    def getTitleimage( self, REQUEST): 
      return self.getObjProperty('titleimage',REQUEST) 


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getContentType
    # --------------------------------------------------------------------------
    def getContentType( self, REQUEST): 
      return 'text/html'


    """
    ############################################################################
    ###
    ###  Page-Navigation
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getFirstPage:
    # --------------------------------------------------------------------------
    def getFirstPage(self, REQUEST, incResource=False, root=None): 
      root = _globals.nvl(root,self.getDocumentElement())
      return root
    
    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getPrevPage:
    # --------------------------------------------------------------------------
    def getPrevPage(self, REQUEST, incResource=False, root=None): 
      ob = None
      root = _globals.nvl(root,self.getDocumentElement())
      while True:
        ob = getPrevSibling(self,REQUEST,incResource)
        if ob is None:
          parent = self.getParentNode()
          if parent is not None:
            ob = parent.getPrevPage(REQUEST,incResource,root)
        else:
          ob = ob.getLastPage(REQUEST,incResource,ob)
        if not ob is None and not ob.isMetaType(self.PAGES,REQUEST):
          ob = ob.getPrevPage(REQUEST,incResource,root)
        if ob is None or ob.isMetaType(self.PAGES,REQUEST):
          break
      return ob

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNextPage:
    # --------------------------------------------------------------------------
    def getNextPage(self, REQUEST, incResource=False, root=None): 
      ob = None
      root = _globals.nvl(root,self.getDocumentElement())
      while True:
        children = self.filteredChildNodes(REQUEST,self.PAGES)
        if len(children) > 0:
          ob = children[0]
        else:
          current = self
          while ob is None and current is not None:
            ob = getNextSibling(current,REQUEST,incResource)
            current = current.getParentNode()
        if not ob is None and not ob.isMetaType(self.PAGES,REQUEST):
          ob = ob.getNextPage(REQUEST,incResource,root)
        if ob is None or ob.isMetaType(self.PAGES,REQUEST):
          break
      return ob

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getLastPage:
    # --------------------------------------------------------------------------
    def getLastPage(self, REQUEST, incResource=False, root=None):
      ob = None
      root = _globals.nvl(root,self.getDocumentElement())
      children = [root]
      while len( children) > 0:
        i = len( children)-1
        while i >= 0:
          if (incResource or not children[i].isResource(REQUEST)):
            ob = children[i]
            i = 0
          i = i - 1
        if ob == self:
          break
        children = ob.filteredChildNodes(REQUEST,self.PAGES)
      return ob


    """
    ############################################################################
    ###
    ###  Related Links 
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getLinkList:
    #
    #  Returns list of link-URLs for child-objects.
    # --------------------------------------------------------------------------
    def getLinkList(self, REQUEST, allow_none=0):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      try:
        reqBuffId = 'getLinkList%i'%allow_none
        value = self.fetchReqBuff(reqBuffId,REQUEST)
        return value
      except:
        
        #-- Get value.
        value = []
        for ob in self.filteredChildNodes(REQUEST,['ZMSFile','ZMSLinkContainer','ZMSLinkElement']):
          if not ob.meta_type=='ZMSLinkElement' or \
             not ob.isPage() or \
             not ob.getObjProperty('attr_type',REQUEST)=='embed':
            value.extend(ob.getLinkList(REQUEST,allow_none))
        
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
    #  ZMSContainerObject.filtered_insert_actions:
    # --------------------------------------------------------------------------
    def filtered_insert_actions(self, path, REQUEST):
      actions = []
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
        
      #-- ZMS-Objects.
      for ac_inherited_permission in self.ac_inherited_permissions(1):
        ac_permission = ac_inherited_permission[0]
        ac_actions = ac_inherited_permission[1]
        for ac_action in list(ac_actions):
          if ac_action.find('manage_addZMS')==0:
            meta_type = ac_action[10:]
            if meta_type != 'ZMSModule' and self.getConfProperty('%s.enabled'%meta_type,1)==1:
              constructor = self.dGlobalAttrs[meta_type]['constructor']
              if constructor is not None:
                record = (_globals.html_quote(self.display_type(REQUEST,meta_type)),'manage_addProduct/zms/%s'%self.dGlobalAttrs[meta_type]['constructor'])
                if not record in actions:
                  actions.append(record)
      
      #-- Meta-Objects.
      for meta_id in self.getMetaobjIds():
        ob = self.getMetaobj(meta_id)
        ob_access = self.getObjProperty('manage_access',REQUEST)
        can_insert = True
        can_insert = can_insert and (self.getConfProperty('%s.enabled'%meta_id,1) == 1)
        can_insert = can_insert and ((not type(ob_access) is dict) or (ob_access.get( 'insert') is None) or (len( self.intersection_list( ob_access.get( 'insert'), self.getUserRoles(auth_user))) > 0))
        if can_insert:
          if (self.meta_type in ['ZMS','ZMSFolder'] and ob['type'] in ['ZMSDocument','ZMSModule','ZMSObject','ZMSResource','ZMSRecordSet','ZMSReference']) or \
             (self.meta_type in ['ZMSDocument'] and ob['type'] in ['ZMSModule','ZMSObject','ZMSResource','ZMSRecordSet']) or \
             (self.meta_type in ['ZMSTeaserContainer'] and ob['type'] in ['ZMSTeaserElement']):
            if ob['type'] in ['ZMSModule']:
              record = (_globals.html_quote(ob['name']),'manage_addZMSModule')
            else:
              record = (_globals.html_quote(ob['name']),'manage_addProduct/zms/manage_addzmscustomform')
            if not record in actions:
              actions.append(record)
      
      #-- Sort.
      actions.sort()
      
      #-- Headline,
      if len(actions) > 0:
        actions.insert(0,('----- %s -----'%self.getZMILangStr('ACTION_INSERT')%self.display_type(REQUEST),''))
      
      # Return action list.
      return actions


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.ajaxFilteredContainerActions:
    #
    #  Returns ajax-xml with filtered-child-actions.
    # --------------------------------------------------------------------------
    def ajaxFilteredContainerActions(self, REQUEST):
      """ ZMSContainerObject.ajaxFilteredChildActions """

      #-- Get actions.
      path = '' # self.id + '/'      
      actions = []
      actions.extend( self.filtered_insert_actions(path,REQUEST))
      actions.extend( self.filtered_edit_actions(path,REQUEST))
      actions.extend( self.filtered_workflow_actions(path,REQUEST))
      
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxFilteredContainerActions.xml'
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
    ###  H T M L - P r e s e n t a t i o n 
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNavItems:
    #
    #  Items of main-navigation in content-area.
    #
    #	@param	current	the currently displayed page
    #	@param	REQUEST	the triggering http-request
    #	@param	opt	the dictionary of options:
    #			'add_self' (boolean=False)	= add self to list
    #			'deep' (boolean=True)		= process child nodes
    #			'id' (string='')		= id of base ul-element
    # --------------------------------------------------------------------------
    def getNavItems(self, current, REQUEST, opt={}):
      items = []
      items.append( '<ul')
      if opt.get('id',''):
        items.append( ' id="%s"'%opt.get('id',''))
        opt['id'] = ''
      items.append('>\n')
      obs = []
      if opt.get('add_self',False):
        obs.append( self)
      obs.extend( self.filteredChildNodes(REQUEST,self.PAGES))
      for ob in obs:
        if not ob.isResource(REQUEST):
          css = []
          if ob.id == current.id:
            css.append( 'current')
            css.append( 'active')
          elif ob.id != self.id and ob.id in current.getPhysicalPath():
            css.append( 'active')
          else: 
            css.append( 'inactive')
          items.append('<li')
          items.append(' class="%s"'%(' '.join(css)))
          items.append('>')
          items.append('<a ')
          items.append(' href="%s"'%ob.getHref2IndexHtml(REQUEST))
          items.append(' title="%s"'%ob.getTitle(REQUEST))
          if len(css) > 0:
            items.append(' class="%s"'%(' '.join(css)))
          items.append('>')
          items.append('<span>%s</span>'%ob.getTitlealt(REQUEST))
          items.append('</a>')
          if opt.get('deep',True) and ob.id != self.id and ob.id in current.getPhysicalPath():
            items.append( ob.getNavItems( current, REQUEST, opt))
          items.append('</li>\n')
      items.append( '</ul>\n')
      return ''.join(items)

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNavElements: 
    #
    #  Elements of main-navigation in content-area.
    # --------------------------------------------------------------------------
    def getNavElements(self, REQUEST, expand_tree=1, current_child=None, subElements=[]):
      elmnts = []
      # Child navigation.
      obs = self.filteredChildNodes(REQUEST)
      if not expand_tree and \
         current_child is not None and \
         current_child.meta_type not in ['ZMSDocument','ZMSCustom'] and \
         isPageWithElements(obs) and \
         self.getLevel() > 0:
        obs = [current_child]
      for ob in obs:
        if ob.isPage() and not ob.isResource(REQUEST): 
          elmnts.append(ob)
        if current_child is not None and \
           current_child.id == ob.id:
          elmnts.extend(subElements)
      # Parent navigation.
      parent = self.getParentNode()
      if parent is not None:
        elmnts = parent.getNavElements(REQUEST,expand_tree,self,elmnts)
      # Return elements.
      return elmnts


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getIndexNavElements: 
    #
    #  Elements of index-navigation in content-area.
    # --------------------------------------------------------------------------
    def getIndexNavElements(self, REQUEST):
      indexNavElmnts = []
      # Retrieve elements.
      if REQUEST.get('op','')=='':
        indexNavElmnts = filter(lambda ob: ob.isPage() and ob.isMetaType(['ZMSDocument','ZMSCustom']) and not ob.isResource(REQUEST),self.filteredChildNodes(REQUEST,self.PAGES))
      # Return elements.
      return indexNavElmnts


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.renderShort:
    #
    #  Renders short presentation of a container-object.
    # --------------------------------------------------------------------------
    def renderShort(self,REQUEST):
      return '<h2>%s</h2>'%self.getTitlealt(REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.printHtml:
    #
    #  Renders print presentation of a container-object.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      html = ''
      
      # Title.
      sectionizer.processLevel( level)
      title = self.getTitle( REQUEST)
      title = '%s %s'%(str(sectionizer),title)
      REQUEST.set( 'ZMS_SECTIONIZED_TITLE', '<h%i>%s</h%i>'%( level, title, level))
      
      # pageregionBefore
      attr = REQUEST.get( 'ZMS_PAGEREGION_BEFORE', 'pageregionBefore')
      if hasattr( self, attr):
        html += getattr( self, attr)( self, REQUEST)
      elif hasattr( self, 'bodyContent_PagePre'):
        html += getattr( self, 'bodyContent_PagePre')( self,REQUEST)
    
      # bodyContent
      subsectionizer = {}
      for ob in self.filteredChildNodes( REQUEST, self.PAGEELEMENTS):
        if not subsectionizer.has_key( ob.meta_type):
          subsectionizer[ob.meta_type] = sectionizer.clone()
        subsectionizer[ob.meta_type].processLevel(level+1)
        html += ob.printHtml( level+1, subsectionizer[ob.meta_type], REQUEST)
      
      # pageregionAfter
      attr = REQUEST.get( 'ZMS_PAGEREGION_AFTER', 'pageregionAfter')
      if hasattr( self, attr):
        html += getattr( self, attr)( self, REQUEST)
      elif hasattr( self ,'bodyContent_PagePost'):
        html += getattr( self ,'bodyContent_PagePost')( self,REQUEST)
      
      # Container-Objects.
      if deep:
        for ob in self.filteredChildNodes(REQUEST,self.PAGES):
          html += ob.printHtml( level+1, sectionizer, REQUEST, deep)
      
      return html


    """
    ############################################################################
    ###  
    ###  DOM-Methoden 
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.filteredTreeNodes:
    #
    #  Returns a NodeList that contains all accessible children of this subtree 
    #  in correct order. If none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def filteredTreeNodes(self, REQUEST, meta_types, order_by=None, order_dir=None, max_len=None, recursive=True):
      rtn = []
      
      #-- Process tree.
      if not self.meta_type == 'ZMSLinkElement':
        obs = self.getChildNodes(REQUEST)
        for ob in obs:
          append = True
          append = append and ob.isMetaType(meta_types)
          append = append and ob.isVisible(REQUEST)
          if append: 
            rtn.append(ob)
          if not append or (append and recursive):
            if ob.isPage():
              rtn.extend(ob.filteredTreeNodes(REQUEST,meta_types,None,order_dir,None,recursive))
      
      #-- Order.
      if order_by is not None:
      
        # order by select-options of special object
        options = []
        if type(meta_types) is str and meta_types in self.getMetaobjIds():
          metaObj = self.getMetaobj(meta_types)
          attrs = metaObj['attrs']
          for attr in attrs:
            if attr['id'] == order_by:
              options = attr.get('keys',[])
      
        # collect object-items
        tmp = []
        for ob in rtn:
          value = ob.getObjProperty(order_by,REQUEST)
          if value in options:
            value = options.index(value)
          tmp.append((value,ob))
        
        # sort object-items
        tmp.sort()
        
        # truncate sort-id from sorted object-items
        rtn = map( lambda ob: ob[1], tmp)
        if order_dir == 'desc': 
          rtn.reverse()
      
      #-- Size.
      if max_len is not None:
        if len(rtn) > max_len:
          rtn = rtn[:max_len]
      
      return rtn

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.firstFilteredChildNode:
    #
    #  Returns the first accessible child of this node.
    # --------------------------------------------------------------------------
    def firstFilteredChildNode(self, REQUEST={}, meta_types=None):
      for node in self.getChildNodes(REQUEST,meta_types):
        if node.isVisible(REQUEST):
          return node
      return None

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.filteredChildNodes:
    #
    #  Returns a NodeList that contains all accessible children of this node in 
    #  correct order. If none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def filteredChildNodes(self, REQUEST={}, meta_types=None):
      return filter(lambda ob: ob.isVisible(REQUEST),self.getChildNodes(REQUEST,meta_types))

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getChildNodes:
    #
    #  Returns a NodeList that contains all children of this node in correct 
    #  order. If none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST=None, meta_types=None):
      # if _globals.debug( self):
      #   t0 = time.time() 
      #   _globals.writeLog( self, "[getChildNodes] >>>>> IN")
      obs = []
      # Get all object-items.
      if REQUEST is None:
        obs = map( lambda x: ( getattr( x, 'sort_id', ''), x), self.objectValues( self.dGlobalAttrs.keys()))
      # Get selected object-items.
      else:
        lang = REQUEST.get('lang',None)
        # Get coverages.
        multilang = lang is not None and len(self.getLangs().keys()) > 1
        if multilang:
          key_coverage = 'attr_dc_coverage'
          prim_lang = self.getPrimaryLanguage()
          coverages = []
          coverages.extend(['global.'+lang,'local.'+lang])
          for parent in self.getParentLanguages( lang):
            coverages.append('global.'+parent)
        for ob in filter( lambda x: x.isMetaType( meta_types, REQUEST), self.objectValues( filter( lambda x: x!='ZMSTrashcan', self.dGlobalAttrs.keys()))):
          if multilang:
            obj_vers = ob.getObjVersion( REQUEST)
            coverage = getattr( obj_vers, key_coverage, '')
            if coverage in [ '', None]: coverage = 'global.' + prim_lang
          if not multilang or coverage in coverages:
            proxy = ob.__proxy__()
            if proxy is not None:
              sort_id = getattr( ob, 'sort_id', '')
              if ob.isPage():
                sort_id = 's' + sort_id
              obs.append( ( sort_id, proxy))
      # Sort child-nodes.
      obs.sort()
      # Return child-nodes in correct sort-order.
      # if _globals.debug( self): 
      #   _globals.writeLog( self, "[getChildNodes] <<<<< OUT (%s)"%str(time.time()-t0))
      return map(lambda ob: ob[1],obs)


    """
    ############################################################################
    ###  
    ###  Sort-Order
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.normalizeSortIds:
    #
    #  Normalizes sort-ids for all children of this node 
    # --------------------------------------------------------------------------
    def normalizeSortIds(self, id_prefix='e'):
      # Get all object-items.
      obs = []
      for ob in self.objectValues( self.dGlobalAttrs.keys()):
        sort_id = getattr( ob, 'sort_id', '')
        proxy = ob.__proxy__()
        if proxy is not None:
          sort_id = getattr( ob, 'sort_id', '')
          if proxy.isPage(): sort_id = 's%s'%sort_id
          obs.append((sort_id,ob))
      # Sort child-nodes.
      obs.sort()
      # Normalize sort-order.
      new_sort_id = 10
      for ( sort_id, ob) in obs:
       if ob.id[:len(id_prefix)] == id_prefix:
         ob.setSortId( new_sort_id)
         new_sort_id  += 10


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNewSortId:
    #
    #  Get new Sort-ID.
    # --------------------------------------------------------------------------
    def getNewSortId(self):
      new_sort_id = 0
      for ob in self.getChildNodes():
        sort_id = ob.getSortId()
        if sort_id > new_sort_id:
          new_sort_id = sort_id
      new_sort_id = new_sort_id + 10
      return new_sort_id


    """
    ############################################################################
    ###
    ###  Teaser
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getTeaserElements:
    #
    #  Returns Teaser-Objects.
    # --------------------------------------------------------------------------
    def getTeaserElements(self, REQUEST, current=None):
      teaserElmnts = []
      # Retrieve elements.
      current = _globals.nvl(current,self)
      # Process parent.
      abort_penetrance = current.meta_type == 'ZMSLinkElement' or current.getObjProperty('attr_zmsteasercontainer_abort_penetrance',REQUEST) != ''
      if not abort_penetrance:
        parent = self.getParentNode()
        if parent is not None:
          teaserElmnts.extend(parent.getTeaserElements(REQUEST,current))
      # Process this.
      thisTeaserElmnts = filter( lambda x: x.getType() == 'ZMSTeaserElement', self.filteredChildNodes( REQUEST,[ 'ZMSCustom']))
      for teaserCntnr in self.filteredChildNodes( REQUEST,[ 'ZMSTeaserContainer']):
        thisTeaserElmnts.extend( teaserCntnr.filteredChildNodes( REQUEST,[ 'ZMSTeaserElement', 'ZMSCustom']))
      for teaserElmnt in thisTeaserElmnts:
          #-- Penetrance
          penetrance = teaserElmnt.getPenetrance( REQUEST)
          append = False
          # 0= this 
          append = append or (penetrance == 0 and current == self)
          # 1= sub_nav
          append = append or (penetrance == 1 and current.isMetaType(['ZMS','ZMSFolder'],REQUEST))
          # 2= sub_all
          append = append or (penetrance == 2)
          #-- Append
          if append: 
            teaserElmnts.append(teaserElmnt)
      # Return elements.
      return teaserElmnts

    """
    ############################################################################
    #
    #   Module
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.manage_addZMSModule:
    #
    #  Add module.
    # --------------------------------------------------------------------------
    def manage_addZMSModule(self, lang, _sort_id, custom, REQUEST, RESPONSE):
      """ manage_addZMSModule """
      meta_id = self.getMetaobjId( custom)
      metaObj = self.getMetaobj( meta_id)
      key = self.getMetaobjAttrIds( meta_id)[0]
      attr = self.getMetaobjAttr( meta_id, key)
      zexp = attr[ 'custom']
      filename = zexp.getFilename()
      fileid = filename[:filename.find('.')]
      path = package_home(globals()) + '/import/'
      _fileutil.exportObj( zexp, path + filename)
      _fileutil.importZexp( self, path, filename)
      _fileutil.remove( path + filename)
      
      ##### Create ####
      id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
      newid = self.getNewId(id_prefix)
      
      ##### Rename ####
      self.manage_renameObject(fileid,newid)
      
      ##### Normalize Sort-IDs ####
      obj = getattr( self, newid)
      obj.sort_id = _sort_id
      self.normalizeSortIds( id_prefix)
      
      # Return with message.
      message = self.getZMILangStr('MSG_INSERTED')%custom
      RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),newid,lang,urllib.quote(message)))

################################################################################
