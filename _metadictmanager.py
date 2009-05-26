################################################################################
# _metadictmanager.py
#
# $Id: _metadictmanager.py,v 1.8 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.8 $
#
# Implementation of class MetadictManager (see below).
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
import copy
import sys
# Product Imports.
import _globals


"""
################################################################################
#
#   X M L   I M / E X P O R T
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _metadictmanager.importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, zms_system=0, createIfNotExists=1):
  id = item['id']
  metaDicts = self.dict_list(self.__get_metadicts__())
  ids = metaDicts.keys()
  ids = filter(lambda x: metaDicts[x].get('zms_system',0)==1,metaDicts.keys())
  if createIfNotExists == 1 or id in ids:
    newId = id
    newAcquired = 0
    newName = item['name']
    newType = item['type']
    newMandatory = item.get('mandatory',0)
    newMultilang = item.get('multilang',1)
    newRepetitive = item.get('repetitive',0)
    newKeys = item.get('keys',[])
    newCustom = item.get('custom','')
    newDstMetaTypes = item.get('dst_meta_types',[])
    setMetadictAttr(self, None, newId, newAcquired, newName, newType, \
      newMandatory, newMultilang, newRepetitive, newCustom, newKeys, \
      newDstMetaTypes, zms_system )

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      _importXml(self,item,zms_system,createIfNotExists)
  else:
    _importXml(self,v,zms_system,createIfNotExists)
  self.synchronizeObjAttrs()


# ------------------------------------------------------------------------------
#  _metadictmanager.getAttrName
# ------------------------------------------------------------------------------
def getAttrName(id):
  s_attr = id
  s_attr = s_attr.lower()
  s_attr = s_attr.replace('.','_')
  s_attr = 'attr_%s'%s_attr
  return s_attr


################################################################################
################################################################################

# ------------------------------------------------------------------------------
#  _metadictmanager.renameMetadictAttrs
# ------------------------------------------------------------------------------
def renameMetadictAttrs(self, old_attr, new_attr):
  if self.meta_type[:3] == 'ZMS':
    for obj_vers in self.getObjVersions():
      for s_lang in self.getLangIds():
        old_lang_attr = "%s_%s"%(old_attr,s_lang)
        new_lang_attr = "%s_%s"%(new_attr,s_lang)
        if hasattr(obj_vers,old_lang_attr):
          try:
            setattr(obj_vers,new_lang_attr,copy.deepcopy(getattr(obj_vers,old_lang_attr)))
          except:
            pass
    # Process children.
    for ob in self.objectValues():
      renameMetadictAttrs(ob,old_attr,new_attr)

# ------------------------------------------------------------------------------
#  _metadictmanager.dropMetadictAttrs
# ------------------------------------------------------------------------------
def dropMetadictAttrs(self, attr):
  if self.meta_type[:3] == 'ZMS':
    for s_lang in self.getLangIds():
      lang_attr = "%s_%s"%(attr,s_lang)
      if hasattr(self,lang_attr):
        try:
          delattr(self,lang_attr)
        except:
          pass
    # Process children.
    for ob in self.objectValues():
      dropMetadictAttrs(ob,attr)


################################################################################
################################################################################

# ------------------------------------------------------------------------------
#  _metadictmanager.delMetadictAttr:
# 
#  Delete Meta-Attribute specified by given attr.
# ------------------------------------------------------------------------------
def delMetadictAttr(self, attr):
  # Delete.
  obs = self.__get_metadicts__()
  i = obs.index(attr)
  # Update attribute.
  del obs[i] # Attribute
  del obs[i] # Values
  self.setConfProperty('ZMS.custom.metas',copy.deepcopy(obs))
  # Return with empty attr.
  return ''


# ------------------------------------------------------------------------------
#  _metadictmanager.setMetadictAttr:
# 
#  Set/add Meta-Attribute with specified values.
# ------------------------------------------------------------------------------
def setMetadictAttr(self, attr, newId, newAcquired, newName='', newType='', \
      newMandatory=0, newMultilang=1, newRepetitive=0, newCustom='', \
      newKeys=[], newDstMetaTypes=[], zms_system=0):
  obs = self.__get_metadicts__()
  # Remove exisiting entry.
  if attr is None:
    attr = getAttrName(newId)
  if attr in obs:
    i = obs.index(attr)
    del obs[i] 
    del obs[i] 
  else: 
    i = len(obs)
  # Attribute.
  attr = getAttrName(newId)
  # Values.
  newValues = {}
  newValues['id'] = newId
  newValues['acquired'] = newAcquired
  newValues['name'] = newName
  newValues['type'] = newType
  newValues['mandatory'] = newMandatory
  newValues['multilang'] = newMultilang
  newValues['repetitive'] = newRepetitive
  newValues['keys'] = newKeys
  newValues['custom'] = newCustom
  newValues['dst_meta_types'] = newDstMetaTypes
  newValues['zms_system'] = zms_system
  # Update attribute.
  obs.insert(i,newValues)
  obs.insert(i,attr)
  self.setConfProperty('ZMS.custom.metas',copy.deepcopy(obs))
  # Return with new attr.
  return attr


# ------------------------------------------------------------------------------
#  _metadictmanager.moveMetadictAttr:
#
#  Moves Meta-Attribute specified by given attr to specified position.
# ------------------------------------------------------------------------------
def moveMetadictAttr(self, attr, pos):
  # Move.
  obs = self.__get_metadicts__()
  i = obs.index(attr)
  attr = obs[i]
  values = obs[i+1]
  del obs[i] 
  del obs[i] 
  obs.insert(pos*2, values)
  obs.insert(pos*2, attr)
  # Update attribute.
  self.setConfProperty('ZMS.custom.metas',copy.deepcopy(obs))
  # Return with empty attr.
  return ''


################################################################################
################################################################################
###
###   class MetadictManager
###
################################################################################
################################################################################
class MetadictManager: 

    # Management Interface.
    # ---------------------
    manage_customizeMetadictForm = HTMLFile('dtml/metadict/manage_customizeform', globals()) 
    manage_BigPictureMetadictForm = HTMLFile('dtml/metadict/manage_bigpicture', globals()) 


    # --------------------------------------------------------------------------
    #  MetadictManager.__get_metadicts__:
    # 
    #  Returns list of DC.Metadictionaries.
    # --------------------------------------------------------------------------
    def __get_metadicts__(self):
      return self.getConfProperty('ZMS.custom.metas',[])


    # --------------------------------------------------------------------------
    #  MetadictManager.getMetadictAttrs:
    # 
    #  Returns list of attributes of DC.Metadictionaries.
    # --------------------------------------------------------------------------
    def getMetadictAttrs(self, meta_type=None, exclude_types=[]):
      attrs = []
      obs = self.__get_metadicts__()
      for i in range(len(obs)/2):
        key = obs[i*2]
        append = True
        value = self.getMetadictAttr( key)
        if value is not None and \
           value['type'] not in exclude_types:
          if meta_type is None or \
             meta_type in value['dst_meta_types']:
            attrs.append(key)
      # ZMSLinkElement must always have attr_dc_description!
      if meta_type == 'ZMSLinkElement':
        if not 'attr_dc_description' in attrs:
          attrs.insert(0,'attr_dc_description')
      # Return attributes.
      return attrs


    # --------------------------------------------------------------------------
    #  MetadictManager.getMetadictAttr:
    # 
    #  Get Attribute for Meta-Dictionary specified by key.
    # --------------------------------------------------------------------------
    def getMetadictAttr(self, key):
      obs = self.__get_metadicts__()
      if key in obs:
        ob = obs[obs.index(key)+1].copy()
      # ZMSLinkElement must always have attr_dc_description!
      elif key == 'attr_dc_description':
        manage_lang = self.getManageLanguage( self.getPrimaryLanguage())
        ob = {}
        ob['id'] = 'DC.Description'
        ob['name'] = self.getLangStr('ATTR_DC_DESCRIPTION',manage_lang)
        ob['type'] = 'text'
        ob['dst_meta_types'] = [self.meta_type]
      # Not found!
      else:
        return None
      # Acquire from parent.
      if ob.get('acquired',0)==1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          ob = portalMaster.getMetadictAttr(key)
          if ob is None:
            return None
          ob = ob.copy()
          ob['acquired'] = 1
      ob['key'] = getAttrName(ob['id'])
      ob['mandatory'] = ob.get('mandatory',0)
      ob['multilang'] = ob.get('multilang',1)
      ob['keys'] = ob.get('keys',[])
      ob['custom'] = ob.get('custom','')
      ob['dst_meta_types'] = ob.get('dst_meta_types',['ZMS','ZMSFolder','ZMSDocument'])
      ob['size'] = ob.get('size',35)
      return ob


    ############################################################################
    #  MetadictManager.manage_changeMetadicts:
    #
    #  Change Meta-Attributes.
    ############################################################################
    def manage_changeMetadicts(self, btn, lang, manage_lang, REQUEST, RESPONSE=None):
        """ MetadictManager.manage_changeMetadicts """        
        message = ''
        attr = REQUEST.get('attr','')
        target = 'manage_customizeMetadictForm'
        
        try:
          
          # Acquire.
          # --------
          if btn == self.getLangStr('BTN_ACQUIRE', manage_lang):
            newId = REQUEST['aq_id']
            newAcquired = 1
            attr = setMetadictAttr(self, None, newId, newAcquired)
            message = self.getLangStr('MSG_INSERTED', manage_lang)%attr
          
          # Change.
          # -------
          elif btn == self.getLangStr('BTN_CHANGE', manage_lang): 
            oldAttr = attr
            newId = REQUEST['id'].strip()
            newAcquired = 0
            newName = REQUEST['name'].strip()
            newType = REQUEST['metatype'].strip()
            newMandatory = REQUEST.get('mandatory', 0)
            newMultilang = REQUEST.get('multilang', 0)
            newRepetitive = REQUEST.get('repetitive', 0)
            newKeys = self.string_list(REQUEST.get('keys',''), '\n')
            newCustom = REQUEST.get('custom', '')
            newDstMetaTypes = REQUEST.get('dst_meta_types',[])
            attr = setMetadictAttr(self, oldAttr, newId, newAcquired, newName, newType, newMandatory, newMultilang, newRepetitive, newCustom, newKeys, newDstMetaTypes )
            if oldAttr != attr:
              renameMetadictAttrs(self, oldAttr, attr)
              dropMetadictAttrs(self, oldAttr)
            message = self.getLangStr('MSG_CHANGED', manage_lang)
          
          # Copy.
          # -----
          elif btn == self.getLangStr('BTN_COPY',manage_lang):
            metaOb = self.getMetadictAttr(attr)
            if metaOb.get('acquired',0) == 1:
              masterRoot = getattr(self,self.getConfProperty('Portal.Master'))
              masterDocElmnt = masterRoot.objectValues(['ZMS'])[0]
              REQUEST.set('attrs',[attr])
              xml =  masterDocElmnt.manage_changeMetadicts(self.getLangStr('BTN_EXPORT',manage_lang), lang, manage_lang, REQUEST, RESPONSE)
              importXml(self,xml=xml)
              message = self.getLangStr('MSG_IMPORTED',manage_lang)%('<i>%s</i>'%attr)

          # Delete.
          # -------
          elif btn in ['delete',self.getLangStr('BTN_DELETE', manage_lang)]:
            oldAttr = attr
            attr = delMetadictAttr(self, oldAttr)
            dropMetadictAttrs(self, oldAttr)
            message = self.getLangStr('MSG_DELETED', manage_lang)%int(1)
          
          # Export.
          # -------
          elif btn == self.getLangStr('BTN_EXPORT', manage_lang):
            value = []
            attrs = REQUEST.get('attrs',[])
            metadicts = self.__get_metadicts__()
            for i in range(len(metadicts)/2):              
              id = metadicts[i*2]
              dict = metadicts[i*2+1].copy()
              if id in attrs or len(attrs) == 0:
                if dict.has_key('zms_system'):
                    del dict['zms_system']
                value.append(dict)
            if len(value) == 1:
              value = value[0]
            content_type = 'text/xml; charset=utf-8'
            filename = 'export.metadict.xml'
            export = self.getXmlHeader() + self.toXmlString(value,1)
            RESPONSE.setHeader('Content-Type',content_type)
            RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
            return export
          
          # Import.
          # -------
          elif btn == self.getLangStr('BTN_IMPORT', manage_lang):
            f = REQUEST['file']
            if f:
              filename = f.filename
              importXml(self,xml=f)
            else:
              filename = REQUEST['init']
              createIfNotExists = 1
              self.importConf(filename, REQUEST, createIfNotExists)
            message = self.getLangStr('MSG_IMPORTED',manage_lang)%('<i>%s</i>'%filename)
          
          # Insert.
          # -------
          elif btn == self.getLangStr('BTN_INSERT', manage_lang):
            newId = REQUEST['_id'].strip()
            newAcquired = 0
            newName = REQUEST['_name'].strip()
            newType = REQUEST['_type'].strip()
            newMandatory = REQUEST.get('_mandatory',0)
            newMultilang = REQUEST.get('_multilang',0)
            newRepetitive = REQUEST.get('_repetitive',0)
            newCustom = ''
            if newType == 'method':
              newCustom += '<!--// BO %s //-->\n\n'%newId
              newCustom += '<!--// EO %s //-->\n'%newId
            attr = setMetadictAttr(self, None, newId, newAcquired, newName, newType, newMandatory, newMultilang, newRepetitive, newCustom)
            message = self.getLangStr('MSG_INSERTED', manage_lang)%attr
          
          # Move to.
          # --------
          elif btn == 'move_to':
            pos = REQUEST['pos']
            oldAttr = attr
            attr = moveMetadictAttr(self, oldAttr, pos)
            message = self.getLangStr('MSG_MOVEDOBJTOPOS', manage_lang)%(("<i>%s</i>"%oldAttr),(pos+1))
          
          ##### Page-Extension ####
          if attr == 'attr_pageext':
            for langId in self.getLangIds():
              self.setLangMethods( langId)
            
          ##### SYNCHRONIZE ####
          self.synchronizeObjAttrs()
        
        # Handle exception.
        except:
          error = str( sys.exc_type)
          if sys.exc_value:
            error += ': ' + str( sys.exc_value)
          target = self.url_append_params( target, { 'manage_tabs_error_message':error})
        
        # Return with message.
        target = self.url_append_params( target, { 'lang':lang, 'manage_lang':manage_lang, 'attr':attr})
        if len( message) > 0:
          target = self.url_append_params( target, { 'manage_tabs_message':message})
        return RESPONSE.redirect( target)

################################################################################
