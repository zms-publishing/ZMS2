################################################################################
# _objchildren.py
#
# $Id: _objchildren.py,v 1.7 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.7 $
#
# Implementation of class ObjChildren (see below).
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
import copy
import time
import urllib
# Product Imports.
import _blobfields
import _globals


################################################################################
################################################################################
###
###   O B J E C T   C H I L D R E N
###
################################################################################
################################################################################
class ObjChildren:

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage_initObjChild',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)

    """
    ############################################################################
    ###
    ###  Constructor
    ###
    ############################################################################
    """
    # --------------------------------------------------------------------------
    #	ObjChildren.initObjChild
    # --------------------------------------------------------------------------
    def initObjChild(self, id, _sort_id, type, REQUEST):

      ##### ID ####
      metaObjAttr = self.getObjChildrenAttr(id)
      repetitive = metaObjAttr.get('repetitive',0)==1
      if repetitive:
        id += str(self.getSequence().nextVal())
      
      ##### Create ####
      oItem = getattr(self,id,None)
      if oItem is None or id not in self.objectIds():
        if self.dGlobalAttrs.has_key(type):
          obj = self.dGlobalAttrs[type]['obj_class'](id,_sort_id+1)
        else:
          obj = self.dGlobalAttrs['ZMSCustom']['obj_class'](id,_sort_id+1)
          obj.meta_id = type
        self._setObject(obj.id, obj)
        oItem = getattr(self,id)
        
      ##### Object State ####
      oItem.setObjStateNew(REQUEST)
      ##### Init Properties ####
      oItem.setObjStateModified(REQUEST)
      for lang in self.getLangIds():
        oItem.setObjProperty('active',1,lang)
      ##### VersionManager ####
      oItem.onChangeObj(REQUEST)
          
      ##### Normalize Sort-IDs ####
      self.normalizeSortIds(_globals.id_prefix(id))
        
      return oItem


    # --------------------------------------------------------------------------
    #	ObjChildren._initObjChildren
    # --------------------------------------------------------------------------
    def _initObjChildren(self, obj_attr, REQUEST):
      id = obj_attr['id']
      ids = []
      for ob in self.getChildNodes(REQUEST):
        if ob.id[:len(id)]==id: 
          ids.append(ob.id)
      mandatory = obj_attr.get('mandatory',0)==1
      if mandatory:
        if len(ids) == 0:
          if obj_attr['type'] == '*' and type( obj_attr['keys']) is list and len( obj_attr['keys']) > 0:
            obj_attr['type'] = obj_attr['keys'][0]
          self.initObjChild(obj_attr['id'],0,obj_attr['type'],REQUEST)
      repetitive = obj_attr.get('repetitive',0)==1
      if repetitive:
        if id in ids:
          new_id = self.getNewId(id)
          if _globals.debug( self):
            _globals.writeLog( self, "[_initObjChildren]: Rename %s to %s"%(id,new_id))
          if new_id not in self.objectIds():
            self.manage_renameObject(id=id,new_id=new_id)
      else:
        if not id in ids and len(ids)>0:
          old_id = ids[0]
          if _globals.debug( self):
            _globals.writeLog( self, "[_initObjChildren]: Rename %s to %s"%(old_id,id))
          if id not in self.objectIds():
            self.manage_renameObject(id=old_id,new_id=id)


    # --------------------------------------------------------------------------
    #	ObjChildren.initObjChildren
    # --------------------------------------------------------------------------
    def initObjChildren(self, REQUEST):
      if _globals.debug( self):
        _globals.writeLog( self, "[initObjChildren]")
      if self.meta_type=='ZMSCustom':
        self.getObjProperty( 'initObjChildren' ,REQUEST)
        for obj_attr in self.getMetaobj(self.meta_id)['attrs']:
          type = obj_attr['type']
          if type == '*' or type in self.dGlobalAttrs.keys() or type in self.getMetaobjIds(sort=0):
            self._initObjChildren(obj_attr,REQUEST)
      else:
        for key in self.getMetadictAttrs(self.meta_type):
          obj_attr = self.getMetadictAttr(key)
          if obj_attr['type'] in self.getMetaobjIds():
            self._initObjChildren(obj_attr,REQUEST)


    # --------------------------------------------------------------------------
    #  ObjChildren.getObjChildrenMetadictAttrs:
    # --------------------------------------------------------------------------
    def getObjChildrenMetadictAttrs(self, REQUEST):
      rtn = []
      for key in self.getMetadictAttrs(self.meta_type):
        metadictAttr = self.getMetadictAttr(key)
        metadictAttrId = metadictAttr['id']
        metadictAttrType = metadictAttr['type']
        if metadictAttrType in self.getMetaobjIds(sort=0):
          metaObj = self.getMetaobj(metadictAttrType)
          if metaObj['type'] == 'ZMSResource':
            if len(self.getObjChildren(metadictAttrId,REQUEST)) > 0:
              rtn.append(metadictAttr)
      return rtn
    
    
    # --------------------------------------------------------------------------
    #  ObjChildren.getObjChildrenAttr:
    # --------------------------------------------------------------------------
    def getObjChildrenAttr(self, key, meta_type=None):
      # Meta-Type.
      if self.meta_type=='ZMSCustom':
        meta_type = _globals.nvl(meta_type,self.meta_id)
      else:
        meta_type = _globals.nvl(meta_type,self.meta_type)
      ##### Meta-Objects ####
      if meta_type in self.getMetaobjIds(sort=0) and key in self.getMetaobjAttrIds(meta_type):
        obj_attr = self.getMetaobjAttr(meta_type,key)
      ##### Meta-Dictionaries ####
      elif 'attr_%s'%key.lower() in self.getMetadictAttrs(meta_type):
        obj_attr = self.getMetadictAttr('attr_%s'%key.lower())
      ##### Default ####
      else:
        obj_attr = {'id':key,'repetitive':1,'mandatory':0}
      return obj_attr


    # --------------------------------------------------------------------------
    #	ObjChildren.getObjChildren
    # --------------------------------------------------------------------------
    def getObjChildren(self, id, REQUEST, meta_types=None):
      objAttr = self.getObjChildrenAttr(id)
      return filter(lambda ob: \
        len(id)==0 or \
        ((int(objAttr.get('repetitive',0))==0 and ob.id==id) or \
         (int(objAttr.get('repetitive',0))==1 and len(ob.id) > len(id) and ob.id[:len(id)]==id and ob.id[len(id)] in ['0','1','2','3','4','5','6','7','8','9'])),
        self.getChildNodes(REQUEST,meta_types))


    """
    ############################################################################
    ###
    ###  Action-List 
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #	ObjChildren.filtered_insert_actions_objChildren:
    #
    #	Insert-actions of management interface.
    # --------------------------------------------------------------------------
    def filtered_insert_actions_objChildren(self, objAttr, path, REQUEST):
      actions = []
      lang = REQUEST['lang']
      manage_lang = REQUEST['manage_lang']

      #-- Objects.
      repetitive = objAttr.get('repetitive',0)==1
      if repetitive or len(self.getObjChildren(objAttr['id'],REQUEST))==0:
        if objAttr['type']=='*':
          meta_types = objAttr['keys']
        else:
          meta_types = [objAttr['type']]
        for meta_type in meta_types:
          if meta_type in self.dGlobalAttrs.keys():
            value = 'manage_addProduct/zms/%s'%self.dGlobalAttrs[meta_type]['constructor']
          else:
            value = 'manage_addProduct/zms/manage_addzmscustomform'
          record = (self.display_type(REQUEST,meta_type),value)
          if not record in actions:
            actions.append(record)

      #-- Sort.
      actions.sort()
      
      #-- Headline,
      if len(actions) > 0:
        actions.insert(0,('----- %s -----'%self.getLangStr('ACTION_INSERT',manage_lang)%self.display_type(REQUEST),''))
      
      # Return action list.
      return actions


    # --------------------------------------------------------------------------
    #	ObjChildren.filtered_container_actions_objChildren:
    #
    #	Object-actions of management interface.
    # --------------------------------------------------------------------------
    def filtered_container_actions_objChildren(self, objAttr, path, REQUEST):
      actions = []
      lang = REQUEST['lang']
      manage_lang = REQUEST['manage_lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      #-- Actions.
      repetitive = objAttr.get('repetitive',0)==1
      mandatory = objAttr.get('mandatory',0)==1
      if path:
        if repetitive or not mandatory:
          if self.getAutocommit() or \
             self.getPrimaryLanguage() == lang or \
             self.getDCCoverage(REQUEST).find('local.') == 0:
            if self.getAutocommit() or self.inObjStates(['STATE_NEW'],REQUEST) or not self.getHistory():
              if self.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST):
                actions.append((self.getLangStr('BTN_UNDO',manage_lang),'manage_undoObjs'))
              can_delete = not self.inObjStates( [ 'STATE_DELETED'], REQUEST)
              if can_delete and self.meta_type == 'ZMSCustom':
                ob_access = self.getObjProperty('manage_access',REQUEST)
                can_delete = can_delete and ((not type(ob_access) is dict) or (ob_access.get( 'delete') is None) or (len( self.intersection_list( ob_access.get( 'delete'), self.getUserRoles(auth_user))) > 0))
              if can_delete:
                actions.append((self.getLangStr('BTN_DELETE',manage_lang),'manage_deleteObjs'))
              actions.append((self.getLangStr('BTN_CUT',manage_lang),'manage_cutObjects'))
            actions.append((self.getLangStr('BTN_COPY',manage_lang),'manage_copyObjects'))
            actions.append((self.getLangStr('ACTION_MOVEUP',manage_lang),path + 'manage_moveObjUp'))
            actions.append((self.getLangStr('ACTION_MOVEDOWN',manage_lang),path + 'manage_moveObjDown'))
      if (repetitive or len(self.getObjChildren(objAttr['id'],REQUEST))==0) and (self.cb_dataValid()):
        if objAttr['type']=='*':
          meta_types = objAttr['keys']
        else:
          meta_types = [objAttr['type']]
        append = True
        try:
          for ob in self.cp_get_obs( REQUEST):
            append = append and \
              ( ( ob.meta_type in meta_types) or \
                ( ob.meta_type == 'ZMSCustom' and ob.meta_id in meta_types))
        except:
          append = False
        if append:
          actions.append((self.getLangStr('BTN_PASTE',manage_lang),'manage_pasteObjs'))

      #-- Commands.
      actions.extend(self.filtered_command_actions(path,REQUEST))
      
      #-- Headline.
      if len(actions) > 0:
        actions.insert(0,('----- %s -----'%self.getLangStr('ACTION_SELECT',manage_lang)%self.getLangStr('ATTR_ACTION',manage_lang),'',actions))

      #-- Insert.
      if (repetitive or len(self.getObjChildren(objAttr['id'],REQUEST))==0):
        ob = self
        if len( path) > 0:
          ob = self.getParentNode()
        actions.extend(ob.filtered_insert_actions_objChildren(objAttr,path,REQUEST))
        
      # Return action list.
      return actions


    ############################################################################
    #  ObjChildren.manage_initObjChild: 
    #
    #  Create object-child.
    ############################################################################
    def manage_initObjChild(self, id, type, lang, manage_lang, REQUEST, RESPONSE=None): 
      """ ObjChildren.manage_initObjChild """
      
      # Create.      
      obj = self.initObjChild(id,self.getNewSortId(),type,REQUEST)
      
      # Return with message.
      if RESPONSE is not None:
        message = self.getLangStr('MSG_INSERTED',manage_lang)%obj.display_type(REQUEST)
        message = urllib.quote(message)
        target = REQUEST.get('target','%s/manage_main'%obj.id)
        RESPONSE.redirect('%s?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(target,lang,manage_lang,message))

################################################################################
