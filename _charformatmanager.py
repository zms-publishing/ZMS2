################################################################################
# _charformatmanager.py
#
# $Id:$
# $Name:$
# $Author:$
# $Revision:$
#
# Implementation of class CharFormatManager (see below).
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
import ZPublisher.HTTPRequest
import copy
import urllib
# Product Imports.
import _blobfields
import _globals


# ------------------------------------------------------------------------------
#  _charformatmanager.importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, zms_system=0, createIfNotExists=1):
  if createIfNotExists == 1:
    fmts = getCharFormats(self)
    fmts.append(item)
    self.setConfProperty('ZMS.custom.charformats',copy.deepcopy(fmts))

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      _importXml(self,item,zms_system,createIfNotExists)
  else:
    _importXml(self,v,zms_system,createIfNotExists)


# ------------------------------------------------------------------------------
#  _charformatmanager.moveCharFormat:
# ------------------------------------------------------------------------------
def moveCharFormat(self, id, pos):
  fmts = getCharFormats(self)
  fmt = fmts[id]
  fmts.remove(fmt)
  fmts.insert(pos,fmt)
  self.setConfProperty('ZMS.custom.charformats',copy.deepcopy(fmts))


# ------------------------------------------------------------------------------
#  _charformatmanager.delCharFormat:
# ------------------------------------------------------------------------------
def delCharFormat(self, id):
  fmts = getCharFormats(self)
  del fmts[id]
  self.setConfProperty('ZMS.custom.charformats',copy.deepcopy(fmts))


# ------------------------------------------------------------------------------
#  _charformatmanager.setCharFormat:
# ------------------------------------------------------------------------------
def setCharFormat(self, id, newBtn, newDisplay, newTag='', newAttrs='', newJS=''):
  fmts = getCharFormats(self)
  if id == len(fmts):
    fmts.append({})
  fmt = fmts[id]
  fmt['btn'] = newBtn
  fmt['display'] = newDisplay
  fmt['tag'] = newTag
  fmt['attrs'] = newAttrs
  fmt['js'] = newJS
  self.setConfProperty('ZMS.custom.charformats',copy.deepcopy(fmts))


# ------------------------------------------------------------------------------
#  _charformatmanager.getCharFormats:
# ------------------------------------------------------------------------------
def getCharFormats(self):
  return self.getConfProperty('ZMS.custom.charformats',[])


################################################################################
################################################################################
###
###   class CharFormatManager:
###
################################################################################
################################################################################
class CharFormatManager: 


    # --------------------------------------------------------------------------
    #  CharFormatManager.getCharFormats:
    # --------------------------------------------------------------------------
    def getCharFormats(self):
      return getCharFormats(self.getDocumentElement())


    ############################################################################
    #  CharFormatManager.manage_customizeCharFormat:
    #
    #  Change char-formats.
    ############################################################################
    def manage_customizeCharFormat(self, lang, REQUEST, RESPONSE): 
      """ CharFormatManager.manage_customizeCharFormat """
      message = ''
      id = REQUEST.get('id','')
      
      # Change.
      # -------
      if REQUEST['btn'] == self.getZMILangStr('BTN_CHANGE'):
        fmts = self.getCharFormats()
        id = int(id)
        fmt = fmts[ id]
        btn = REQUEST.get('new_btn','')
        if isinstance(btn,ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(btn,'filename',''))==0:
            btn = fmt.get('btn',None)
          else:
            btn = _blobfields.createBlobField(self,_globals.DT_IMAGE,btn)
        display = REQUEST['new_display'].strip()
        tag = REQUEST['new_tag'].strip()
        attrs = REQUEST['new_attrs'].strip()
        js = REQUEST['new_js'].strip()
        setCharFormat(self,id,btn,display,tag,attrs,js)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif REQUEST['btn'] in [ self.getZMILangStr('BTN_DELETE'), 'delete']:
        id = int(id)
        delCharFormat(self,id) 
        message = self.getZMILangStr('MSG_DELETED')%int(1)
        id = ''
      
      # Insert.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
        fmts = self.getCharFormats()
        id = len(fmts)
        fmt = {}
        btn = REQUEST.get('_btn','')
        if isinstance(btn,ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(btn,'filename',''))==0:
            btn = fmt.get('btn',None)
          else:
            btn = _blobfields.createBlobField(self,_globals.DT_IMAGE,btn)
        display = REQUEST['_display'].strip()
        setCharFormat(self,id,btn,display)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Export.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_EXPORT'):
        value = []
        ids = REQUEST.get('ids',[])
        fmts = getCharFormats(self)
        for id in range(len(fmts)):
          if str(id) in ids or len(ids) == 0:
            value.append(fmts[id])
        if len(value)==1:
          value = value[0]
        content_type = 'text/xml; charset=utf-8'
        filename = 'export.charfmt.xml'
        export = self.getXmlHeader() + self.toXmlString(value,1)
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
        return export

      # Import.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_IMPORT'):
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
      elif REQUEST['btn'] == 'move_to':
        pos = REQUEST['pos']
        id = int(id)
        moveCharFormat( self, id, pos)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%str(id)),(pos+1))
        id = ''

      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeTextFormatForm?lang=%s&manage_tabs_message=%s&id=%s#form1'%(lang,message,str(id)))

################################################################################
