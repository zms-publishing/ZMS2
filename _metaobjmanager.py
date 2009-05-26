################################################################################
# _metaobjmanager.py
#
# $Id: _metaobjmanager.py,v 1.9 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.9 $
#
# Implementation of class MetaobjManager (see below).
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
from Products.ExternalMethod import ExternalMethod
from Products.PythonScripts import PythonScript
import ZPublisher.HTTPRequest
import copy
import sys
# Product Imports.
import _blobfields
import _fileutil
import _globals
import _objattrs


"""
################################################################################
#
#   K E Y S
#
################################################################################
"""

CONF_METAOBJS = "ZMS.custom.objects"


"""
################################################################################
#
#   X M L   I M / E X P O R T
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _metaobjmanager.importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, zms_system=0, createIfNotExists=1):
  id = item['key']
  metaObjs = getRawMetaobjs(self)
  ids = metaObjs.keys()
  ids = filter( lambda x: metaObjs[x].get('zms_system',0)==1, ids)
  if createIfNotExists == 1 or id in ids:
    newValue = item.get('value')
    newValue['zms_system'] = zms_system
    newDtml = item.get('dtml')
    newEnabled = item.get('enabled',1)
    # Delete Object.
    if id in ids:
      delMetaobj( self, id )
    # Set Object.
    setMetaobj( self, id, newValue, newDtml )
    # Set Attributes.
    for attr in newValue['__obj_attrs__']:
      attr_id = attr.get('id')
      newName = attr.get('name')
      newMandatory = attr.get('mandatory')
      newMultilang = attr.get('multilang')
      newRepetitive = attr.get('repetitive')
      newType = attr.get('type')
      newKeys = attr.get('keys')
      newCustom = attr.get('custom')
      newDefault = attr.get('default','')
      self._setMetaObjAttr( id, attr_id, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault, zms_system)
    # Set Enabled.
    self.setConfProperty( '%s.enabled'%id, newEnabled )

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  v = self.parseXmlString( xml, mediadbStorable=False)
  if type(v) is list:
    for item in v:
      id = _importXml(self,item,zms_system,createIfNotExists)
  else:
    id = _importXml(self,v,zms_system,createIfNotExists)
  self.synchronizeObjAttrs()


# ------------------------------------------------------------------------------
#  _metaobjmanager.recurse_updateVersionPatch:
#
#  Update version patch.
# ------------------------------------------------------------------------------
def recurse_updateVersionPatch(docElmnt, self, REQUEST):
  message = ''
  container = self.getDocumentElement()
  Special_Objects = getattr( container, 'Special_Objects', None)
  if Special_Objects is None:
    container.manage_addFolder( id='Special_Objects', title='Special Objects')
    Special_Objects = filter( lambda x: x.id == 'Special_Objects', container.objectValues(['Folder']))[0]
    for meta_id in self.getMetaobjIds():
      meta_obj = self.getMetaobj(meta_id)
      if not meta_obj[ 'acquired']:
        for key in self.getMetaobjAttrIds( meta_id):
          attr = self.getMetaobjAttr(meta_id, key)
          if attr['type'] == 'method':
            Special_Objects.manage_addDTMLMethod( meta_id+'.'+key, attr['type']+': '+attr['name'], attr['custom'])
  return message


# ------------------------------------------------------------------------------
#  _metaobjmanager.getRawMetaobjs:
#
#  Returns raw dictionary of meta-objects.
# ------------------------------------------------------------------------------
def getRawMetaobjs(self):
  return self.getConfProperty(CONF_METAOBJS,{})


# ------------------------------------------------------------------------------
#  _metaobjmanager.setMetaobj:
# 
#  Sets Meta-Object with specified values.
# ------------------------------------------------------------------------------
def setMetaobj(self, id, meta_obj, newDtml=None, newAttrs=[]):
  obs = getRawMetaobjs(self)

  # Create template.
  if newDtml is not None:  
    tmpltId = getTemplateId( id)
    tmpltTitle = 'Template: %s'%meta_obj['name']
    container = self.getHome()
    if tmpltId in container.objectIds():
      container.manage_delObjects( ids=[ tmpltId])
    container.manage_addDTMLMethod( tmpltId, tmpltTitle, '')
    dtml_method = getattr( container, tmpltId)
    dtml_method.manage_edit( newDtml, tmpltTitle)
    dtml_method.manage_proxy( roles=[ 'Manager'])
  
  # Set Attributes to Meta-Object.
  meta_obj = meta_obj.copy()
  meta_obj['__obj_attrs__'] = newAttrs
  obs[id] = meta_obj
  self.setConfProperty(CONF_METAOBJS,obs.copy())


# ------------------------------------------------------------------------------
#  _metaobjmanager.delMetaobj:
# 
#  Delete Meta-Object specified by id.
# ------------------------------------------------------------------------------
def delMetaobj(self, id):

  # Handle methods.
  ids = filter( lambda x: x.startswith(id+'.'), self.Special_Objects.objectIds( ['DTML Method']))
  if ids:
    self.Special_Objects.manage_delObjects( ids)
  
  # Delete template.
  tmpltId = getTemplateId( id)
  container = self.getHome()
  if tmpltId in container.objectIds():
    container.manage_delObjects( ids=[ tmpltId] )
  
  # Delete object.
  cp = getRawMetaobjs(self)
  obs = {}
  for key in cp.keys():
    if key == id:
      # Delete attributes.
      attr_ids = map( lambda x: x['id'], cp[key]['__obj_attrs__'] )
      for attr_id in attr_ids:
        delMetaObjAttr(self, id, attr_id)
    else:
      obs[key] = cp[key]

  # Set Attributes to Meta-Object.
  self.setConfProperty(CONF_METAOBJS,obs.copy())


# ------------------------------------------------------------------------------
#  _metaobjmanager.findMetaobj
#
#  Search tree for instance of object with given meta-ids.
# ------------------------------------------------------------------------------
def findMetaobj(self, ids):
  if self.meta_type == 'ZMSCustom' and self.meta_id in ids:
    return self
  for child in self.getChildNodes():
    ob = findMetaobj(child, ids)
    if ob is not None:
      return ob
  return None


# ------------------------------------------------------------------------------
#  _metaobjmanager.delMetaObjAttr:
# 
#  Delete Attribute from Meta-Object specified by id.
# ------------------------------------------------------------------------------
def delMetaObjAttr(self, id, attr_id):
  ob = self.__get_metaobj__(id)
  attrs = copy.copy(ob['__obj_attrs__'])

  # Delete Attribute.
  cp = []
  for attr in attrs:
    if attr['id'] == attr_id:
      if attr['type'] in [ 'method']: 
        home = self.Special_Objects
        if id+'.'+attr['id'] in home.objectIds(['DTML Method']):
          home.manage_delObjects(ids=[id+'.'+attr['id']])
      elif attr['type'] in [ 'method', 'DTML Method', 'DTML Document', 'External Method', 'Script (Python)']:
        home = self.getHome()
        if attr['id'] in home.objectIds([attr['type']]):
          home.manage_delObjects(ids=[attr['id']])
        if attr['type'] == 'External Method':
          try:
            _fileutil.remove( INSTANCE_HOME+'/Extensions/'+attr['id']+'.py')
          except:
            pass
    else:
      cp.append(attr)
  ob['__obj_attrs__'] = cp
  
  # Assign Attributes to Meta-Object.
  ob['zms_system'] = 0
  obs =  getRawMetaobjs(self)
  obs[id] = ob
  self.setConfProperty(CONF_METAOBJS,obs.copy())


# ------------------------------------------------------------------------------
#  MetaobjManager._moveMetaObjAttr:
# 
#  Moves Meta-Object Attribute in specified position.
# ------------------------------------------------------------------------------
def moveMetaObjAttr(self, id, attr_id, pos):
  ob = self.__get_metaobj__(id)
  attrs = copy.copy(ob['__obj_attrs__'])
  
  # Move Attribute.
  ids = self.getMetaobjAttrIds(id)
  i = ids.index(attr_id)
  attr = attrs[i]
  attrs.remove(attr)
  attrs.insert(pos,attr)
  ob['__obj_attrs__'] = attrs
      
  # Assign Attributes to Meta-Object.
  ob['zms_system'] = 0
  obs =  getRawMetaobjs(self)
  obs[id] = ob
  self.setConfProperty(CONF_METAOBJS,obs.copy())


# ------------------------------------------------------------------------------
#  _metaobjmanager.getTemplateId
#
#  Returns template-id for meta-object specified by given Id.
# ------------------------------------------------------------------------------
def getTemplateId(id):
  return "bodyContentZMSCustom_%s"%id


# ------------------------------------------------------------------------------
#  _metaobjmanager.getMetaobjZMI
#
#  Returns ZMI from method 'manage_main' for meta-object specified by given Id.
# ------------------------------------------------------------------------------
def getMetaobjZMI(self, id, REQUEST):
  metaObj = self.getMetaobj(id)
  for metaObjAttr in metaObj['attrs']:
    if metaObjAttr['id']=='manage_main':
      value = metaObjAttr['custom']
      REQUEST.set('ZMS_ACTION','manage_changeProperties')
      html = []
      if REQUEST.get('ZMS_INSERT',None) is not None:
        html.append('<form name="form0" action="manage_addZMSCustom" method="post" enctype="multipart/form-data">\n')
        html.append('<input type="hidden" name="meta_id" value="%s">\n'%id)
        html.append('<input type="hidden" name="id" value="%s">\n'%REQUEST.get('id','e'))
        html.append('<input type="hidden" name="_sort_id:int" value="%i">\n'%REQUEST.get('_sort_id'))
        html.append('<input type="hidden" name="ZMS_INSERT" value="%s">\n'%REQUEST.get('ZMS_INSERT'))
      else:
        html.append('<form name="form0" action="manage_changeProperties" method="post" enctype="multipart/form-data">\n')
      html.append(self.f_submitInputFields(self,REQUEST))
      try:
        value = _globals.dt_html(self,value,REQUEST)
      except:
        value = _globals.writeException(self,'[getMetaobjZMI]')
      html.append(value)
      html.append('</form>\n')
      return ''.join(html)
  return None


################################################################################
################################################################################
###
###   class MetaobjManager
###
################################################################################
################################################################################
class MetaobjManager: 

    # Management Interface.
    # ---------------------
    manage_customizeMetaobjForm = HTMLFile('dtml/metaobj/manage_customizeform', globals()) 
    manage_BigPictureMetaobjForm = HTMLFile('dtml/metaobj/manage_bigpicture', globals()) 
    metaobj_record_select = HTMLFile('dtml/metaobj/recordset/record_select', globals())
    metaobj_record_update = HTMLFile('dtml/metaobj/recordset/record_update', globals())
    metaobj_record_insert = HTMLFile('dtml/metaobj/recordset/record_insert', globals())
    metaobj_record_summary = HTMLFile('dtml/metaobj/recordset/record_summary', globals())
    metaobj_recordset_details_grid = HTMLFile('dtml/metaobj/recordset/details_grid', globals())
    metaobj_recordset_details = HTMLFile('dtml/metaobj/recordset/details', globals())
    metaobj_recordset_main_grid = HTMLFile('dtml/metaobj/recordset/main_grid', globals())
    metaobj_recordset_main = HTMLFile('dtml/metaobj/recordset/main', globals())
    metaobj_recordset_actions = HTMLFile('dtml/metaobj/recordset/actions', globals())
    metaobj_recordset_input_fields = HTMLFile('dtml/metaobj/recordset/input_fields', globals())
    metaobj_recordset_input_js = HTMLFile('dtml/metaobj/recordset/input_js', globals())
    metaobj_input_fields = HTMLFile('dtml/metaobj/input_fields', globals())
    metaobj_input_js = HTMLFile('dtml/metaobj/input_js', globals())

    # --------------------------------------------------------------------------
    #  MetaobjManager.__get_metaobjs__:
    # 
    #  Returns all meta-objects (including acquisitions).
    # --------------------------------------------------------------------------
    def __get_metaobjs__(self): 
      obs = {}
      raw = getRawMetaobjs(self)
      master_obs = None
      for ob_id in raw.keys():
        ob = raw.get(ob_id)
        # Acquire from parent.
        if ob.get('acquired',0) == 1:
          if master_obs is None:
            portalMaster = self.getPortalMaster()
            if portalMaster is not None:
              master_obs = portalMaster.__get_metaobjs__()
          if master_obs is not None:
            ob = master_obs[ob_id].copy()
            ob['acquired'] = 1
            obs[ob_id] =  ob
            if ob['type'] == 'ZMSPackage':
              package = ob_id
              for ob_id in master_obs.keys():
                ob = master_obs[ob_id].copy()
                if ob.get( 'package') == package:
                  ob['acquired'] = 1
                  obs[ob_id] =  ob
        else:
          obs[ob_id] = ob
      return obs

    # --------------------------------------------------------------------------
    #  MetaobjManager.__get_metaobj__:
    # 
    #  Returns meta-object identified by Id.
    # --------------------------------------------------------------------------
    def __get_metaobj__(self, id):
      obs = {}
      raw = getRawMetaobjs(self)
      if id in raw.keys():
        obs = raw
        ob = obs.get( id)
        if ob.get('acquired',0) == 1:
          portalMaster = self.getPortalMaster()
          if portalMaster is not None:
            ob = portalMaster.__get_metaobj__(id).copy()
            ob ['acquired'] = 1
      else:
        obs = self.__get_metaobjs__()
        ob = obs.get( id)
      return ob

    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjIds:
    # 
    #  Returns list of specObj-Ids.
    # --------------------------------------------------------------------------
    def getMetaobjIds(self, sort=1):
      obs = self.__get_metaobjs__()
      ids = obs.keys()
      if sort:
        mapping = map(lambda x: (self.getMetaobj(x)['name'],x),ids)
        mapping.sort()
        ids = map(lambda x: x[1],mapping)
      return ids

    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobj:
    # 
    #  Returns specObj specified by Id.
    # --------------------------------------------------------------------------
    def getMetaobj(self, id):
      ob = _globals.nvl( self.__get_metaobj__(id), {})
      d = {}
      d[ 'id'] = id
      d[ 'tmplt'] = getTemplateId( id)
      d[ 'name'] = ob.get( 'name', id)
      d[ 'type'] = ob.get( 'type', 'ZMSDocument')
      d[ 'package'] = ob.get( 'package' , '')
      d[ 'attrs'] = ob.get( '__obj_attrs__', [])
      d[ 'acquired'] = ob.get( 'acquired' ,0 )
      d[ 'zms_system'] = ob.get( 'zms_system' ,0 )
      return d

    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjId:
    # 
    #  Returns Id for specObj specified by Name.
    # --------------------------------------------------------------------------
    def getMetaobjId(self, name):
      for id in self.getMetaobjIds():
        ob = self.getMetaobj(id)
        if name == ob['name']:
          return id
      return None

    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjZMI:
    # 
    #  Returns Meta-Object Management Interface identified by Id.
    # --------------------------------------------------------------------------
    def getMetaobjZMI(self, id, REQUEST):
      return getMetaobjZMI(self,id,REQUEST)


    """
    ############################################################################
    #
    #   A T T R I B U T E S
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  MetaobjManager._initMetaObjAttrs:
    # 
    #  Init list of Attributes for Meta-Object specified by ID.
    # --------------------------------------------------------------------------
    def _initMetaObjAttrs(self, id):
      attrs = []
      cp = copy.copy(attrs)
      # Init Attributes.
      ob = self.__get_metaobj__(id)
      ob['__obj_attrs__'] = attrs
      # Set Attributes to Meta-Object.
      obs =  getRawMetaobjs(self)
      obs[id] = ob
      self.setConfProperty( CONF_METAOBJS, obs.copy() )


    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjAttrIdentifierId:
    # 
    #  Returns Attribute-ID of Datatable-Identifier for Meta-Object specified by ID.
    # --------------------------------------------------------------------------
    def getMetaobjAttrIdentifierId(self, meta_id):
      for attr_id in self.getMetaobjAttrIds( meta_id):
        metaObjAttr = self.getMetaobjAttr( meta_id, attr_id)
        if metaObjAttr[ 'type'] in [ 'identifier', 'string', 'int']:
          return attr_id
      return None


    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjAttrIds:
    # 
    #  Returns list of Attribute-IDs for Meta-Object specified by ID.
    # --------------------------------------------------------------------------
    def getMetaobjAttrIds(self, meta_id):
      ob = self.__get_metaobj__(meta_id)
      attrs = ob['__obj_attrs__']
      ids = map(lambda x: x['id'], attrs)
      return ids


    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjAttr:
    # 
    #  Get Attribute for Meta-Object specified by key.
    # --------------------------------------------------------------------------
    def getMetaobjAttr(self, meta_id, key):
      meta_objs = self.__get_metaobjs__()
      if meta_objs.get(meta_id,{}).get('acquired',0) == 1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          attr = portalMaster.getMetaobjAttr( meta_id, key)
          return attr
      meta_obj = meta_objs.get(meta_id)
      attrs = meta_obj['__obj_attrs__']
      for attr in attrs:
        if attr['id'] == key:
          attr = attr.copy()
          attr['mandatory'] = attr.get('mandatory',0)
          attr['multilang'] = attr.get('multilang',1)
          attr['size'] = attr.get('size',35)
          attr['errors'] = attr.get('errors','')
          try:
            if attr['type'] in [ 'method']:
              home = self.Special_Objects
              ob = getattr( home, meta_id+'.'+attr['id'])
              attr['custom'] = ob.raw
            elif attr['type'] in [ 'DTML Method', 'DTML Document', 'Script (Python)']:
              home = self.getHome()
              ob = getattr( home, attr['id'])
              if ob.meta_type in [ 'DTML Method', 'DTML Document']:
                attr['custom'] = ob.raw
              elif ob.meta_type in [ 'Script (Python)']:
                attr['custom'] = ob.body()
          except:
            value = _globals.writeException(self,'[getMetaobjAttr]')
          return attr
      return None


    # --------------------------------------------------------------------------
    #  MetaobjManager._setMetaObjAttr:
    # 
    #  Set/add Meta-Object Attribute with specified values.
    # --------------------------------------------------------------------------
    def _setMetaObjAttr(self, id, oldId, newId, newName, newMandatory=0, newMultilang=1, newRepetitive=0, newType='string', newKeys=[], newCustom='', newDefault='', zms_system=0 ):
      ob = self.__get_metaobj__(id)
      attrs = copy.copy(ob['__obj_attrs__'])
      
      # Set Attributes.
      if newType in ['delimiter','hint','interface']:
        newCustom = ''
      if newType in ['resource'] and (type(newCustom) is str or type(newCustom) is int):
        newCustom = None
      if not newType in ['*','multiselect','recordset','select']:
        newKeys = []
      if newType=='*' or newType in self.dGlobalAttrs.keys() or newType in self.getMetaobjIds():
        newMultilang = 0
      
      # Defaults for Insert
      method_types = [ 'method', 'DTML Method', 'DTML Document', 'External Method', 'Script (Python)']
      if oldId is None and \
         newType in method_types and \
         (newCustom == '' or type(newCustom) is not str):
        if newType in [ 'method', 'DTML Method', 'DTML Document']:
          newCustom = ''
          newCustom += '<!--// BO '+ newId + ' //-->\n'
          newCustom += '\n'
          newCustom += '<!--// EO '+ newId + ' //-->\n'
        elif newType in [ 'External Method']:
          newCustom = ''
          newCustom += '# Example code:\n'
          newCustom += '\n'
          newCustom += 'def ' + newId + '():\n'
          newCustom += '  return "This is the external method ' + newId + '"\n'
        elif newType in [ 'Script (Python)']:
          newCustom += ''
          newCustom += '# --// BO '+ newId + ' //--\n'
          newCustom += '# Example code:\n'
          newCustom += '\n'
          newCustom += '# Import a standard function, and get the HTML request and response objects.\n'
          newCustom += 'from Products.PythonScripts.standard import html_quote\n'
          newCustom += 'request = container.REQUEST\n'
          newCustom += 'RESPONSE =  request.RESPONSE\n'
          newCustom += '\n'
          newCustom += '# Return a string identifying this script.\n'
          newCustom += 'print "This is the", script.meta_type, \'"%s"\' % script.getId(),\n'
          newCustom += 'if script.title:\n'
          newCustom += '    print "(%s)" % html_quote(script.title),\n'
          newCustom += 'print "in", container.absolute_url()\n'
          newCustom += 'return printed\n'
          newCustom += '\n'
          newCustom += '# --// EO '+ newId + ' //--\n'
      
      attr = {}
      attr['id'] = newId
      attr['name'] = newName
      attr['mandatory'] = newMandatory
      attr['multilang'] = newMultilang
      attr['repetitive'] = newRepetitive
      attr['type'] = newType
      attr['keys'] = newKeys
      attr['custom'] = newCustom
      attr['default'] = newDefault

      # Handle methods (i).
      if oldId is not None and id+'.'+oldId in self.Special_Objects.objectIds(['DTML Method']):
        self.Special_Objects.manage_delObjects(ids=[id+'.'+oldId])

      # Parse Dtml for Errors.
      message = ''
      if newType in [ 'method', 'DTML Method', 'DTML Document']:
        message = _globals.dt_parse( self, newCustom)
        if len( message) > 0:
          attr['errors'] = message
          message = '<div class="form-label">' + newId + '</div><div style="color:red; background-color:yellow; ">%s</div>'%message
        else:
          # Handle methods (ii).
          if newType in [ 'method']:
            self.Special_Objects.manage_addDTMLMethod( id+'.'+newId, newType+': '+newName, newCustom)
      
      # Replace
      ids = self.getMetaobjAttrIds(id)
      if oldId in ids:
        i = ids.index(oldId)
        attrs[i] = attr
      else:
        # Always append new methods at the end.
        if oldId == newId or newType in method_types:
          attrs.append( attr)
        # Insert new attributes before methods
        else:
          i = len( attrs)
          while i > 0 and attrs[ i - 1][ 'type'] in method_types:
            i -= 1
          if i < len(attrs):
            attrs.insert( i, attr)
          else:
            attrs.append( attr)
      ob['__obj_attrs__'] = attrs

      # Handle Zope-Objects.
      if newType in [ 'DTML Method', 'DTML Document', 'External Method', 'Script (Python)']:
        # Remove Zope-Object (deprecated use in document-element).
        container = self.getDocumentElement()
        if oldId in container.objectIds():
          container.manage_delObjects( ids=[ oldId])
          oldId = None
        # External Method.
        if newType == 'External Method':
          try:
            _fileutil.remove( INSTANCE_HOME+'/Extensions/'+oldId+'.py')
          except:
            pass
          newExternalMethod = INSTANCE_HOME+'/Extensions/'+newId+'.py'
          _fileutil.exportObj( newCustom, newExternalMethod)
        # Insert Zope-Object.
        container = self.getHome()
        if oldId is None or oldId == newId:
          if newId in container.objectIds():
            container.manage_delObjects( ids=[ newId])
          if newType == 'DTML Method':
            container.manage_addDTMLMethod( newId, newName, newCustom)
          elif newType == 'DTML Document':
            container.manage_addDTMLDocument( newId, newName, newCustom)
          elif newType == 'External Method':
            ExternalMethod.manage_addExternalMethod( container, newId, newName, newId, newId)
          elif newType == 'Script (Python)':
            PythonScript.manage_addPythonScript( container, newId)
        # Rename Zope-Object.
        elif oldId != newId:
          container.manage_renameObject( id=oldId, new_id=newId)
        # Change Zope-Object.
        obElmnt = getattr( container, newId)
        if newType in [ 'DTML Method', 'DTML Document' ]:
          obElmnt.manage_edit( title=newName, data=newCustom)
          obElmnt.manage_proxy( roles=[ 'Manager'])
          if newId.find( 'manage_') == 0:
            obElmnt.manage_role(role_to_manage='Authenticated',permissions=['View'])
            obElmnt.manage_acquiredPermissions([])
        elif newType == 'Script (Python)':
          params = obElmnt._params
          body = ''
          count = 0
          for s in newCustom.split( '\n'):
            if count == 0 and \
               s.find( '# --// BO %s('%newId) == 0 and \
               s.find( ') //--') > 0:
              params = s[s.find('(')+1:s.rfind(')')]
            while len(s) > 0 and ord(s[-1]) == 13:
              s = s[:-1]
            body += s + '\n'
            count += 1
          obElmnt.ZPythonScript_setTitle( newName)
          obElmnt.ZPythonScript_edit( params=params, body=body)
      
      # Assign Attributes to Meta-Object.
      ob['zms_system'] = zms_system
      obs =  getRawMetaobjs( self )
      obs[id] = ob
      self.setConfProperty( CONF_METAOBJS, obs.copy() )
      
      # Return with message.
      return message


    ############################################################################
    #  MetaobjManager.manage_changeMetaobjs:
    #
    #  Change Meta-Object definitions.
    ############################################################################
    def manage_changeMetaobjs(self, lang, btn='', key='all', REQUEST=None, RESPONSE=None):
        """ MetaobjManager.manage_changeMetaobjs """
        message = ''
        id = REQUEST.get('id','')
        target = 'manage_customizeMetaobjForm'
        
        try:
          
          # Delete.
          # -------
          # Delete Object.
          if key == 'obj' and btn == self.getZMILangStr('BTN_DELETE'):
            ids = [id]
            metaObj = self.getMetaobj( id)
            if metaObj['type'] == 'ZMSPackage':
              for pkgMetaObjId in self.getMetaobjIds():
                pkgMetaObj = self.getMetaobj( pkgMetaObjId)
                if pkgMetaObj[ 'package'] == metaObj[ 'id']:
                    ids.insert( 0, pkgMetaObjId)
            metaobj = findMetaobj( self, ids)
            if metaobj is None:
              for id in ids:
                delMetaobj( self, id )
              id = ''
              message = self.getZMILangStr('MSG_CHANGED')
            else:
              raise 'All instances of "%s" must be deleted before definition can be deleted: <a href="%s/manage_main#_%s">%s</a>!'%(id,metaobj.getParentNode().absolute_url(),metaobj.id,metaobj.absolute_url())
          # Delete Attribute.
          elif key == 'attr' and btn == 'delete':
            attr_id = REQUEST['attr_id']
            delMetaObjAttr( self, id, attr_id )
          
          # Change.
          # -------
          elif key == 'all' and btn == self.getZMILangStr('BTN_CHANGE'):
            savedAttrs = copy.copy(self.getMetaobj(id)['attrs'])
            # Change Object.
            id = REQUEST['id'].strip()
            newValue = {}
            newValue['acquired'] = 0
            newValue['name'] = REQUEST.get('obj_name').strip()
            newValue['type'] = REQUEST.get('obj_type').strip()
            newValue['package'] = REQUEST.get('obj_package').strip()
            newValue['__obj_attrs__'] = []
            newDtml = REQUEST.get('obj_dtml','')
            setMetaobj(self, id, newValue, newDtml, savedAttrs)
            # Change Attributes.
            for old_id in REQUEST.get('old_ids',[]):
              attr_id = REQUEST['attr_id_%s'%old_id].strip()
              newName = REQUEST['attr_name_%s'%old_id].strip()
              newMandatory = REQUEST.get( 'attr_mandatory_%s'%old_id, 0 )
              newMultilang = REQUEST.get( 'attr_multilang_%s'%old_id, 0 )
              newRepetitive = REQUEST.get( 'attr_repetitive_%s'%old_id, 0 )
              newType = REQUEST.get( 'attr_type_%s'%old_id )
              newKeys = self.string_list(REQUEST.get('attr_keys_%s'%old_id,''),'\n')
              newCustom = REQUEST.get('attr_custom_%s'%old_id,'')
              newDefault = REQUEST.get('attr_default_%s'%old_id,'')
              if isinstance(newCustom,ZPublisher.HTTPRequest.FileUpload):
                if len(getattr(newCustom,'filename','')) == 0:
                    savedAttr = filter(lambda x: x['id'] == old_id, savedAttrs)[0]
                    newCustom = savedAttr.get('custom',None)
                else:
                    newCustom = _blobfields.createBlobField( self,_globals.DT_FILE, newCustom, mediadbStorable=False)
              message += self._setMetaObjAttr( id, old_id, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault )
            # Return with message.
            message += self.getZMILangStr('MSG_CHANGED')
          
          # Copy.
          # -----
          elif btn == self.getZMILangStr('BTN_COPY'):
            metaOb = self.getMetaobj(id)
            if metaOb.get('acquired',0) == 1:
              masterRoot = getattr(self,self.getConfProperty('Portal.Master'))
              masterDocElmnt = masterRoot.content
              REQUEST.set('ids',[id])
              xml =  masterDocElmnt.manage_changeMetaobjs(lang, self.getZMILangStr('BTN_EXPORT'), key, REQUEST, RESPONSE)
              importXml(self,xml=xml)
              message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%id)
          
          # Export.
          # -------
          elif btn == self.getZMILangStr('BTN_EXPORT'):
            value = []
            ids = REQUEST.get('ids',[])
            for id in ids:
              metaObj = self.getMetaobj( id)
              if metaObj['type'] == 'ZMSPackage':
                for pkgMetaObjId in self.getMetaobjIds():
                    pkgMetaObj = self.getMetaobj( pkgMetaObjId)
                    if pkgMetaObj[ 'package'] == metaObj[ 'id']:
                      ids.append( pkgMetaObjId)
            keys = getRawMetaobjs(self).keys()
            keys.sort()
            for id in keys:
              if id in ids or len(ids) == 0:
                ob = self.__get_metaobj__(id).copy()
                if ob.has_key('zms_system'):
                    del ob['zms_system']
                docElmnt = self.getDocumentElement()
                dtml_id = getTemplateId(id)
                dtml_raw = ''
                dtml_method = getattr( docElmnt, dtml_id, None)
                if dtml_method is not None and dtml_method.meta_type == 'DTML Method':
                    dtml_raw = dtml_method.raw
                enabled = int(self.getConfProperty('%s.enabled'%id,1))
                # Value.
                value.append({'key':id,'value':ob,'dtml':dtml_raw,'enabled':enabled})
            # XML.
            if len(value)==1:
              value = value[0]
              filename = '%s.metaobj.xml'%ids[0]
            else:
              filename = 'export.metaobj.xml'
            content_type = 'text/xml; charset=utf-8'
            export = self.getXmlHeader() + self.toXmlString(value,1)
            
            RESPONSE.setHeader('Content-Type',content_type)
            RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
            return export
            
          # Insert.
          # -------
          elif btn == self.getZMILangStr('BTN_INSERT'):
            # Insert Object.
            if key == 'obj':
              id = REQUEST['_meta_id'].strip()
              newValue = {}
              newValue['acquired'] = 0
              newValue['name'] = REQUEST.get('_meta_name').strip()
              newValue['type'] = REQUEST.get('_meta_type').strip()
              newValue['__obj_attrs__'] = []
              newDtml = []
              newDtml.append('<!-- BO %s -->\n'%(getTemplateId(id)))
              newDtml.append('\n')
              if newValue['type'] == 'ZMSRecordSet':
                newDtml.append('  <h2><dtml-var "getTitlealt(REQUEST)"></h2>\n')
                newDtml.append('  <p class="description"><dtml-var "_.len(getObjProperty(getMetaobj(meta_id)[\'attrs\'][0][\'id\'],REQUEST))"> <dtml-var "getLangStr(\'ATTR_RECORDS\',lang)"></p>\n')
              newDtml.append('\n')
              newDtml.append('<!-- EO %s -->\n'%(getTemplateId(id)))
              newDtml = ''.join(newDtml)
              setMetaobj(self, id, newValue, newDtml)
              # Insert Attributes.
              if newValue['type'] == 'ZMSDocument':
                message += self._setMetaObjAttr(id,None,'titlealt',self.getZMILangStr('ATTR_TITLESHORT'),1,1,0,'string')
                message += self._setMetaObjAttr(id,None,'title',self.getZMILangStr('ATTR_TITLE'),1,1,0,'string')
              elif newValue['type'] == 'ZMSTeaserElement':
                message += self._setMetaObjAttr(id,None,'titlealt',self.getZMILangStr('ATTR_TITLESHORT'),1,1,0,'string')
                message += self._setMetaObjAttr(id,None,'attr_penetrance',self.getZMILangStr('ATTR_PENETRANCE'),1,1,0,'select',['this','sub_nav','sub_all'])
              elif newValue['type'] == 'ZMSRecordSet':
                message += self._setMetaObjAttr(id,None,'records',self.getZMILangStr('ATTR_RECORDS'),1,1,0,'list')
                message += self._setMetaObjAttr(id,None,'col_id','COL_ID',1,0,0,'identifier',[],0)
                message += self._setMetaObjAttr(id,None,'col_1','COL_1',0,0,0,'string',[],1)
                message += self._setMetaObjAttr(id,None,'col_2','COL_2',0,0,0,'string',[],1)
              elif newValue['type'] == 'ZMSModule':
                message += self._setMetaObjAttr(id,None,'zexp','ZEXP',0,0,0,'resource')
              message += self.getZMILangStr('MSG_INSERTED')%id
            # Insert Attribute.
            if key == 'attr':
              attr_id = REQUEST['attr_id'].strip()
              newName = REQUEST['attr_name'].strip()
              newMandatory = REQUEST.get('_mandatory',0)
              newMultilang = REQUEST.get('_multilang',0)
              newRepetitive = REQUEST.get('_repetitive',0)
              newType = REQUEST.get('_type','string')
              newKeys = REQUEST.get('_keys',[])
              newCustom = REQUEST.get('_custom','')
              newDefault = REQUEST.get('_default','')
              message += self._setMetaObjAttr( id, None, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault)
              message += self.getZMILangStr('MSG_INSERTED')%attr_id
          
          # Acquire.
          # --------
          elif btn == self.getZMILangStr('BTN_ACQUIRE'):
            id = REQUEST['aq_id']
            newValue = {}
            newValue['acquired'] = 1
            newValue['name'] = ''
            newValue['type'] = ''
            newValue['__obj_attrs__'] = []
            setMetaobj(self, id, newValue)
            # Return with message.
            message = self.getZMILangStr('MSG_INSERTED')%id
          
          # Import.
          # -------
          elif btn == self.getZMILangStr('BTN_IMPORT'):
            f = REQUEST['file']
            if f:
              filename = f.filename
              importXml(self,xml=f)
            else:
              filename = REQUEST['init']
              createIfNotExists = 1
              self.importConf(filename, REQUEST, createIfNotExists)
            message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
          
          # Move to.
          # --------
          elif key == 'attr' and btn == 'move_to':
            pos = REQUEST['pos']
            attr_id = REQUEST['attr_id']
            moveMetaObjAttr( self, id, attr_id, pos)
            message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%attr_id),(pos+1))
          
          ##### SYNCHRONIZE ####
          self.synchronizeObjAttrs()
          
        # Handle exception.
        except:
          _globals.writeException(self,"[manage_changeMetaobjs]")
          error = str( sys.exc_type)
          if sys.exc_value:
            error += ': ' + str( sys.exc_value)
          target = self.url_append_params( target, { 'manage_tabs_error_message':error})
        
        # Return with message.
        target = self.url_append_params( target, { 'lang':lang, 'id':id, 'attr_id':REQUEST.get('attr_id','')})
        if len( message) > 0:
          target = self.url_append_params( target, { 'manage_tabs_message':message})
        if REQUEST.has_key('inp_id_name'):
          target += '&inp_id_name=%s'%REQUEST.get('inp_id_name')
          target += '&inp_name_name=%s'%REQUEST.get('inp_name_name')
          target += '&inp_value_name=%s'%REQUEST.get('inp_value_name')
          target += '#Edit'
        return RESPONSE.redirect( target)

################################################################################
