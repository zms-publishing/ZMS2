################################################################################
# _textformatmanager.py
#
# $Id: _textformatmanager.py,v 1.11 2004/11/30 20:03:17 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.11 $
#
# Implementation of class TextFormatManager (see below).
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
import copy
import os
import urllib
# Product Imports.
import _globals
import _objattrs


# ------------------------------------------------------------------------------
#  _textformatmanager.importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, zms_system=0, createIfNotExists=1):
  fmts = getTextFormats(self)
  id = item['key']
  dict = item['value']
  if id in fmts:
    i = fmts.index(id)
    fmts[i+1] = dict
  else:
    fmts.append(id)
    fmts.append(dict)
  self.setConfProperty('ZMS.custom.textformats',copy.deepcopy(fmts))

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      _importXml(self,item,zms_system,createIfNotExists)
  else:
    _importXml(self,v,zms_system,createIfNotExists)


# ------------------------------------------------------------------------------
#  _textformatmanager.br_quote
# ------------------------------------------------------------------------------
def br_quote(text, subtag, REQUEST):
  if type(text) is not str:
    text = str(text)
  rtn = ''
  qcr = ''
  qtab = '&nbsp;' * 6
  if _globals.isManagementInterface(REQUEST):
    if not REQUEST.has_key('format'):
      qcr = '<span class="unicode">&crarr;</span>'
      qtab = '<span class="unicode">&rarr;</span>' + '&nbsp;' * 5
  if subtag == 'br':
    tmp = []
    for s in text.split('<%s>'%subtag):
      while len(s) > 0 and ord(s[0]) in [10,13]: s = s[1:]
      if len(tmp) > 0:
        tmp.append('\n')
      tmp.append(s)
    text = ''.join(tmp)
  ts = text.split('\n')
  ll = []
  c = 0
  for line in ts:
    if line.find( '\t* ') >= 0 or line.find( '\t# ') >= 0:
      i = 0
      while i < len( line) and line[ i] == '\t':
        i += 1
      if line[ i] in [ '*', '#']:
        level = i
        # open nested lists
        if level > len(ll):
          if line[ i] == '*':
            rtn += '<ul>'*(level-len(ll))
            ll.extend(['ul']*(level-len(ll)))
          elif line[ i] == '#':
            rtn += '<ol>'*(level-len(ll))
            ll.extend(['ol']*(level-len(ll)))
        # close nested lists
        elif level < len(ll):
          for li in range(len(ll)-level):
            rtn += '</%s>'%ll[-1]
            ll = ll[0:-1]
        rtn += '<li>%s</li>'%line[i+2:]
        line = None
    if line is not None:
      # close nested lists
      if len(ll) > 0:
        level = 0
        for li in range(len(ll)-level):
          rtn += '</%s>'%ll[-1]
          ll = ll[0:-1]
      i = 0
      while i < len( line) and line[ i] in [ ' ', '\t']:
        if line[ i] == ' ':
          rtn += '&nbsp;'
        elif line[ i] == '\t':
          rtn += qtab
        i += 1
      rtn += '\n'
      line = line[ i:].strip()
      if subtag == 'br':
        rtn += line+qcr
        if c < len( ts):
          rtn += '<%s />'%subtag
      elif len(line) > 0:
        rtn += '<%s'%subtag
        rtn += '>'
        rtn += line+qcr
        rtn += '</%s>'%subtag
      c += 1
  return rtn


# ------------------------------------------------------------------------------
#  _textformatmanager.delTextFormat:
# ------------------------------------------------------------------------------
def delTextFormat(self, id):
  fmts = getTextFormats(self)
  i = fmts.index(id)
  del fmts[i]
  del fmts[i]
  self.setConfProperty('ZMS.custom.textformats',copy.deepcopy(fmts))


# ------------------------------------------------------------------------------
#  _textformatmanager.setTextFormat:
# ------------------------------------------------------------------------------
def setTextFormat(self, id, newId, newDisplay, newZMILang, newTag='', newSubtag='', newAttrs='', newRichedit=0):
  fmts = getTextFormats(self)
  if id in fmts:
    i = fmts.index(id)
  else:
    i = len(fmts)
    fmts.append(newId)
    fmts.append({'display':{}})
  dict = fmts[i+1]
  dict['display'][newZMILang] = newDisplay
  dict['tag'] = newTag
  dict['subtag'] = newSubtag
  dict['attrs'] = newAttrs
  dict['richedit'] = newRichedit
  fmts[i] = newId
  fmts[i+1] = dict.copy()
  self.setConfProperty('ZMS.custom.textformats',copy.deepcopy(fmts))


# ------------------------------------------------------------------------------
#  _textformatmanager.setDefaultTextFormat:
# ------------------------------------------------------------------------------
def setDefaultTextFormat(self, id):
  if len(id) > 0:
    self.setConfProperty('ZMS.custom.textformats.default',id)


# ------------------------------------------------------------------------------
#  _textformatmanager.getTextFormats:
# ------------------------------------------------------------------------------
def getTextFormats(self):
  return self.getConfProperty('ZMS.custom.textformats',[])


################################################################################
################################################################################
###
###   class TextFormatObject:
###
################################################################################
################################################################################
class TextFormatObject:


    # --------------------------------------------------------------------------
    #  TextFormatObject.renderText:
    # --------------------------------------------------------------------------
    def renderText(self, format, key, text, REQUEST, id=None):
      # Process format.
      textformat = self.getTextFormat( format, REQUEST)
      if textformat is not None:
        text = textformat.renderText( text, REQUEST, id)
      # Process html <form>-tags.
      text = _globals.form_quote( text, REQUEST)
      # Custom hook.
      try:
        name = 'renderCustomText'
        if hasattr(self,name):
          text = getattr(self,name)(context=self,key=key,text=text,REQUEST=REQUEST)
      except:
        _globals.writeException( self, '[renderText]: can\'t %s'%name)
      # Return.
      return text


    ############################################################################
    #  TextFormatObject.manage_changeTextProperties:
    #
    #  Change text property from CONTENTEDITABLE paragraph.
    ############################################################################
    def manage_changeTextProperties(self, key, lang, REQUEST, RESPONSE): 
      """ TextFormatManager.manage_changeTextProperties """
      message = ''
      
      # Change.
      # -------
      text = REQUEST.get('custom').strip()
      text = _globals.unescape(text)
      #-- Get Textformat.
      if self.meta_type == 'ZMSTable':
        col = int(key[key.find('_')+1:key.rfind('_')])
        row = int(key[key.rfind('_')+1:])
        cell = self.getCell(row,col,REQUEST)
        format = cell['format']
      else:
        format = self.getObjProperty('format', REQUEST)
      textformat = self.getTextFormat(format, REQUEST)
      if textformat is not None:
        q = chr(182) # '&para;'
        tag = textformat.getTag().upper()
        subtag = textformat.getSubTag().upper()
        #-- Remove tags.
        if len(tag) > 0:
          startTag = '<' + tag
          if text.find(startTag) == 0: 
            text = text[text.find('>',text.find(startTag))+1:]
          text = text.replace(startTag+'>', '')
          endTag = '</' + tag
          if text.rfind(endTag) > 0 and text.rfind('>',text.rfind(endTag)) == len(text)-1: 
            text = text[:text.rfind(endTag)]
          text = text.replace(endTag+'>', '')
        #-- Remove subtags.
        if len(subtag) > 0:
          lines = []
          c = 0
          for line in text.split('<'+subtag+'>'):
            line = line.strip()
            endTag = '</' + subtag.upper() + '>'
            while len(line) > 0 and line.rfind(endTag) == len(line)-len(endTag):
              line = line[:line.rfind(endTag)]
              line = line.strip()
            if len(q) > 0:
              while len(line) > 0 and line.rfind(q) == len(line)-len(q):
                line = line[:line.rfind(q)]
                line = line.strip()
            if c > 0 or len(line) > 0:
              lines.append(line+'\n')
            c += 1
          text = ''.join(lines)
        while len(text) > 0 and text[-1] == '\n':
          text = text[:-1].strip()
      text = _objattrs.utf8(text)
      #-- Set property.
      self.setObjStateModified(REQUEST)
      if self.meta_type == 'ZMSTable':
        self.setCell(col, row, cell['tag'], text, cell['format'], REQUEST)
      else:
        self.setObjProperty(key, text, lang)
      self.onChangeObj(REQUEST)
      #-- Message.
      message += self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      self.checkIn(REQUEST)
      url = REQUEST.get('HTTP_REFERER')
      i = url.find('?')
      if i >= 0:
        url = url[:i]
      url = self.url_append_params(url,{'lang':lang,'preview':'preview','manage_tabs_message':message,})
      if url.find('/manage') >= 0:
        url += '#_'+self.id
      else:
        url += '#'+self.id
      return RESPONSE.redirect(url)


################################################################################
################################################################################
###
###   class TextFormatManager:
###
################################################################################
################################################################################
class TextFormatManager: 


    # Management Interface.
    # ---------------------
    manage_customizeTextFormatForm = HTMLFile('dtml/zms/manage_customizetextformatform', globals()) 


    # --------------------------------------------------------------------------
    #  TextFormatManager.getRichttextFormatIds:
    # --------------------------------------------------------------------------
    def getRichtextFormatIds(self):
      ids = []
      filepath = package_home(globals())+'/plugins/rte/'
      for filename in os.listdir(filepath):
        path = filepath + os.sep + filename
        if os.path.isdir(path):
          ids.append(filename)
      return ids


    # --------------------------------------------------------------------------
    #  TextFormatManager.getTextFormatIds:
    # --------------------------------------------------------------------------
    def getTextFormatIds(self, REQUEST):
      return map(lambda ob: ob.getId(),self.getTextFormats(REQUEST))


    # --------------------------------------------------------------------------
    #  TextFormatManager.getTextFormat:
    # --------------------------------------------------------------------------
    def getTextFormat(self, format, REQUEST):
      obs = getTextFormats(self)
      if format in obs:
        return TextFormat(self,format,obs[obs.index(format)+1],REQUEST)
      return None


    # --------------------------------------------------------------------------
    #  TextFormatManager.getTextFormats:
    # --------------------------------------------------------------------------
    def getTextFormats(self, REQUEST):
      l_sort = []
      obs = getTextFormats(self.getDocumentElement())
      for i in range(len(obs)/2):
        id = obs[i*2+0] 
        ob = obs[i*2+1]
        textformat = TextFormat(self,id,ob,REQUEST)
        l_sort.append((textformat.getDisplay(),textformat))
      l_sort.sort()
      return map(lambda ob: ob[1],l_sort)


    # --------------------------------------------------------------------------
    #  TextFormatManager.getTextFormatDefault:
    # --------------------------------------------------------------------------
    def getTextFormatDefault(self, REQUEST={}):
      return self.getConfProperty('ZMS.custom.textformats.default','body')


    ############################################################################
    #  TextFormatManager.manage_customizeTextFormat:
    #
    #  Change text-formats.
    ############################################################################
    def manage_customizeTextFormat(self, lang, REQUEST, RESPONSE): 
      """ TextFormatManager.manage_customizeTextFormat """
      message = ''
      id = REQUEST.get('id','')
      
      # Change.
      # -------
      if REQUEST['btn'] == self.getZMILangStr('BTN_CHANGE'):
        old_id = REQUEST['id']
        id = REQUEST['new_id'].strip()
        display = REQUEST['new_display'].strip()
        tag = REQUEST['new_tag'].strip()
        subtag = REQUEST['new_subtag'].strip()
        attrs = REQUEST['new_attrs'].strip()
        richedit = REQUEST.get('new_richedit',0)
        setTextFormat(self,old_id,id,display,self.get_manage_lang(),tag,subtag,attrs,richedit)
        if REQUEST.has_key('new_default'): 
          setDefaultTextFormat(self,REQUEST['new_default'])
        id = ""
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_DELETE'):
        id = REQUEST['id']
        delTextFormat(self,id) 
        id = ""
        message = self.getZMILangStr('MSG_DELETED')%int(1)
      
      # Insert.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
        id = REQUEST['_id'].strip()
        display = REQUEST['_display'].strip()
        setTextFormat(self,'',id,display,self.get_manage_lang())
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Export.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_EXPORT'):
        value = []
        ids = REQUEST.get('ids',[])
        fmts = getTextFormats(self)
        for i in range(len(fmts)/2):
          id = fmts[i*2]
          ob = fmts[i*2+1]
          if id in ids or len(ids) == 0:
            value.append({'key':id,'value':ob})
        if len(value)==1:
          value = value[0]
        content_type = 'text/xml; charset=utf-8'
        filename = 'export.textfmt.xml'
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

      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeTextFormatForm?lang=%s&manage_tabs_message=%s&id=%s#form0'%(lang,message,id))


################################################################################
################################################################################
###
###   class TextFormat:
###
################################################################################
################################################################################
class TextFormat:

  # ----------------------------------------------------------------------------
  #  TextFormat.__init__:
  #
  #  Constructor.
  # ----------------------------------------------------------------------------
  def __init__(self, owner, id, ob, REQUEST):
    self.setOwner(owner)
    self.setId(id)
    if REQUEST is not None and \
       REQUEST.has_key('manage_lang') and \
       ob['display'].has_key(REQUEST['manage_lang']):
      self.setDisplay(ob['display'][REQUEST['manage_lang']])
    else:
      self.setDisplay(id)
    self.setTag(ob['tag'])
    self.setSubTag(ob['subtag'])
    self.setAttrs(ob['attrs'])
    richedit = 0
    if ob.has_key('richedit'):
      richedit = ob['richedit']
    self.setRichedit(richedit)
    

  # ----------------------------------------------------------------------------
  #  Get/Set Owner.
  # ----------------------------------------------------------------------------
  getOwner__roles__ = None
  def getOwner(self): return self.owner
  def setOwner(self, owner): self.owner = owner

  # ----------------------------------------------------------------------------
  #  Get/Set Id.
  # ----------------------------------------------------------------------------
  getId__roles__ = None
  def getId(self): return self.id
  def setId(self, id): self.id = id

  # ----------------------------------------------------------------------------
  #  Get/Set Display.
  # ----------------------------------------------------------------------------
  getDisplay__roles__ = None
  def getDisplay(self): return self.display
  def setDisplay(self, display): self.display = display

  # ----------------------------------------------------------------------------
  #  Get/Set <Tag>.
  # ----------------------------------------------------------------------------
  getTag__roles__ = None
  def getTag(self): return self.tag
  def setTag(self, tag): self.tag = tag

  # ----------------------------------------------------------------------------
  #  Assemble <Start-Tag>.
  # ----------------------------------------------------------------------------
  getStartTag__roles__ = None
  def getStartTag(self, id=None): 
    html = ''
    tag = self.getTag()
    if len(tag) > 0:
      html += '<%s'%tag
      if id is not None:
        html += ' id="%s"'%id
      attrs = self.getAttrs()
      if len(attrs) > 0:
        html += ' ' + attrs
      html += '>'
    return html

  # ----------------------------------------------------------------------------
  #  Assemble <End-Tag>.
  # ----------------------------------------------------------------------------
  getEndTag__roles__ = None
  def getEndTag(self): 
    html = ''
    tag = self.getTag()
    if len(tag) > 0:
      html += '</%s'%tag
      html += '>'
    return html

  # ----------------------------------------------------------------------------
  #  Get/Set <Sub-Tag>.
  # ----------------------------------------------------------------------------
  getSubTag__roles__ = None
  def getSubTag(self): return self.subtag
  def setSubTag(self, subtag): self.subtag = subtag

  # ----------------------------------------------------------------------------
  #  Get/Set <Tag>-Attributes.
  # ----------------------------------------------------------------------------
  getAttrs__roles__ = None
  def getAttrs(self): return self.attrs
  def setAttrs(self, attrs): self.attrs = attrs

  # ----------------------------------------------------------------------------
  #  Get/Set Richedit.
  # ----------------------------------------------------------------------------
  getRichedit__roles__ = None
  def getRichedit(self): return self.richedit
  def setRichedit(self, richedit): self.richedit = richedit

  # ----------------------------------------------------------------------------
  #  HTML.
  # ----------------------------------------------------------------------------
  getHtml__roles__ = None
  def getHtml(self): 
    html = ''
    # Open tag.
    if len(self.getTag()) > 0:
      html += '&lt;'
      html += self.getTag()
      if len(self.getAttrs()) > 0:
        html += ' ' + self.getAttrs()
      html += '&gt;'
      html += '<br />'
    # Sub tag.
    subtag = self.getSubTag()
    if len(subtag)>0:
      if subtag == 'br':
        html += '&nbsp;&nbsp;...&lt;' + subtag + ' /&gt;'
      else:
        html += '&nbsp;&nbsp;&lt;' + subtag + '&gt;...&lt;/' + subtag + '&gt;'
      html += '<br />'
    else:
      html += '...'
    # Close tag.
    if len(self.getTag()) > 0:
      html += '&lt;/'
      html += self.getTag()
      html += '&gt;'
      html += '<br />'
    # Default.
    if len(html)==0:
      html += '&nbsp;'
    return html

  # ----------------------------------------------------------------------------
  #  Render text.
  # ----------------------------------------------------------------------------
  renderText__roles__ = None
  def renderText(self, text, REQUEST, id=None):
    html = ''
    tag = self.getTag()
    subtag = self.getSubTag()
    # Open tag.
    html += self.getStartTag( id)
    # Sub tag.
    if len( subtag) > 0:
      text = br_quote( text, subtag, REQUEST)
    try:
      html += str( text)
    except:
      html += text
    # Close tag.
    html += self.getEndTag()
    # Default.
    if len(html)==0:
      html = '&nbsp;'
    # Return.
    return html

################################################################################
