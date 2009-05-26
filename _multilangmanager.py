################################################################################
# _multilangmanager.py
#
# $Id: _multilangmanager.py,v 1.9 2004/11/30 20:03:17 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.9 $
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
import urllib
# Product Imports.
import _globals

# ------------------------------------------------------------------------------
#  Constants
# ------------------------------------------------------------------------------
STYLESHEET_CSS = \
	'<dtml-call "REQUEST.RESPONSE.setHeader(\'Cache-Control\',\'public, max-age=3600\')">' + \
	'<dtml-var f_standard_html_request>' + \
	'<dtml-var f_css_defaults>' + \
	'<dtml-var "_[\'stylesheet.css\']">'


# ------------------------------------------------------------------------------
#  importXml
# ------------------------------------------------------------------------------
def _importXml(self, item, zms_system=0, createIfNotExists=1):
  if createIfNotExists:
    key = item['key']
    lang_dict = self.get_lang_dict()
    lang_dict[key] = {}
    for s_lang in self.getLangIds():
      lang_dict[key][s_lang] = item[s_lang]
    self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  value = self.parseXmlString(xml)
  if type(value) is list:
    for item in value:
      _importXml( self, item, zms_system, createIfNotExists)
  else:
    _importXml( self, value, zms_system, createIfNotExists)


# ------------------------------------------------------------------------------
#  _multilangmanager.getDescLangs
# ------------------------------------------------------------------------------
def getDescLangs(self, id, langs):
  obs = []
  # Primary language is always the first item in the sorted list.
  if id == self.getPrimaryLanguage():
    label = '*'
  elif langs.has_key(id):
    label = langs[id]['label']
  else:
    label = id
  obs.append((label,id))
  # Iterate descending languages.
  for key in langs.keys():
    if langs[key]['parent'] == id:
      obs.extend(getDescLangs(self,key,langs))
  return obs


# ------------------------------------------------------------------------------
#  _multilangmanager.setMethod:
# 
#  Set/add DTML-Method (e.g. index_lang.html) for specified language.
# ------------------------------------------------------------------------------
def setMethod(self, id, raw):
  # delete method (if already exists)
  delMethod(self, id)
  # add method
  title = '*** DO NOT DELETE OR MODIFY ***'
  self.manage_addDTMLMethod(id,title,raw)


# ------------------------------------------------------------------------------
#  _multilangmanager.delMethod:
# 
#  Delete DTML-Method (e.g. index_lang.html) for specified language.
# ------------------------------------------------------------------------------
def delMethod(self, id):
  try: 
    self.manage_delObjects(ids=[id])
  except:
    pass


################################################################################
################################################################################
###
###   C l a s s   M u l t i L a n g u a g e O b j e c t
###
################################################################################
################################################################################
class MultiLanguageObject:

    # --------------------------------------------------------------------------
    #  MultiLanguageObject.getLanguages: 
    #
    #  Returns list of Ids of languages (primary language 1st).
    # --------------------------------------------------------------------------
    def getLanguages(self, REQUEST=None):
    
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'getLanguages'
      try:
        value = self.fetchReqBuff( reqBuffId, REQUEST)
        return value
      except:
        
        #-- Get value.
        value = ['*']
        if REQUEST is not None:
          value = self.getUserLangs(str(REQUEST['AUTHENTICATED_USER']))
        value = filter(lambda x: ('*' in value) or (x in value), self.getLangIds())
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)


    # --------------------------------------------------------------------------
    #  MultiLanguageObject.getDescendantLanguages: 
    #
    #  Returns IDs of descendant languages.
    # --------------------------------------------------------------------------
    def getDescendantLanguages(self, id, REQUEST=None):
      obs = []
      user_langs = ['*']
      if REQUEST is not None:
        user_langs = self.getUserLangs(REQUEST['AUTHENTICATED_USER'])
      langs = self.getLangs()
      obs = getDescLangs(self,id,langs)
      if not '*' in user_langs:
        obs = filter(lambda x: x[1] in user_langs,obs)
      obs.sort()
      return map(lambda ob: ob[1],obs)


################################################################################
################################################################################
###
###   C l a s s   M u l t i L a n g u a g e M a n a g e r
###
################################################################################
################################################################################
class MultiLanguageManager:

    # Management Interface.
    # ---------------------
    manage_customizeLanguagesForm = HTMLFile('dtml/zms/manage_customizelanguagesform', globals()) 

    """
    ############################################################################
    #	P R I M A R Y   L A N G U A G E
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  MultiLanguageManager.setPrimaryLanguage: 
    #
    #  Sets ID of the primary language.
    # --------------------------------------------------------------------------
    def setPrimaryLanguage(self, lang):
      self.language_primary = lang


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getPrimaryLanguage: 
    #
    #  Returns ID of the primary language.
    # --------------------------------------------------------------------------
    def getPrimaryLanguage(self):
      return self.language_primary


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getParentLanguage: 
    #
    #  Returns ID of parent language.
    # --------------------------------------------------------------------------
    def getParentLanguage(self, id):
      parent = None
      langs = self.getLangs()
      if langs.has_key(id):
        lang = langs[id]
        parent = lang['parent']
      return parent


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getParentLanguages: 
    #
    #  Returns IDs of parent languages.
    # --------------------------------------------------------------------------
    def getParentLanguages(self, id):
      obs = []
      langs = self.getLangs()
      if not langs.has_key(id):
        id = self.getPrimaryLanguage()
      parent = id
      while 1:
        parent = langs[parent]['parent']
        if parent:
          obs.append(parent)
        else:
          break
      return obs


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getManageLanguage: 
    #
    #  Returns ID of the preferred language for the management interface.
    # --------------------------------------------------------------------------
    def getManageLanguage(self, id):
      languages = self.getLangs().get(id)
      if type(languages) is dict and languages.has_key('manage'):
        rtn = languages['manage']
      elif id in self.getManageLanguages():
        rtn = id
      elif id in ['de','at']:
        rtn = 'ger'
      elif id in ['fr']:
        rtn = 'fra'
      else:
        rtn = 'eng'
      return rtn


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLanguageLabel: 
    #
    #  Returns language-label of specified ID.
    # --------------------------------------------------------------------------
    def getLanguageLabel(self, id):
      label = id
      langs = self.getLangs()
      if langs.has_key(id):
        label = langs[id]['label']
      return label


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLangs:
    # 
    #  Returns dictionary of languages.
    # --------------------------------------------------------------------------
    def getLangs(self):
      return getattr(self,'attr_languages',{})


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLang: 
    # --------------------------------------------------------------------------
    def getLang(self, id):
      return self.getLangs()[id]


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLangIds: 
    #
    #  Returns list of Ids of languages (primary language 1st).
    # --------------------------------------------------------------------------
    def getLangIds(self, sort=1):
      obs = []
      langs = self.getLangs()
      for key in langs.keys():
        if key == self.getPrimaryLanguage(): 
          label = '*'
        else: 
          label = langs[key]['label']
        obs.append((label,key))
      obs.sort()
      return map(lambda ob: ob[1],obs)


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLanguageFromName: 
    # --------------------------------------------------------------------------
    def getLanguageFromName(self, name): 
      lang = None
      i = name.rfind('.')
      if i > 0:
        name = name[:i]
        j = name.rfind('_')
        if j > 0:
          suffix = name[j+1:]
          langs = self.getLangIds()
          if suffix in langs:
            lang = suffix
      return lang


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLanguage: 
    #
    #  Get requested language of specified URL (used by index_html).
    # --------------------------------------------------------------------------
    def getLanguage(self, REQUEST): 
      lang = REQUEST.get('lang',None)
      langs = self.getLangIds()
      if lang not in langs:
        url = REQUEST.get('URL')
        path = url
        i = url.rfind('.')
        if i > 0:
          path = url[:i]
        j = path.rfind('_')
        if j > 0:
          suffix = path[j+1:]
          if suffix in langs:
            lang = suffix
      if lang not in langs:
        lang = self.getHttpAcceptLanguage( REQUEST)
      if lang not in langs:
        lang = self.getPrimaryLanguage()
      return lang


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getHttpAcceptLanguage: 
    # --------------------------------------------------------------------------
    def getHttpAcceptLanguage(self, REQUEST): 
      lang = None
      langs = self.getLangIds()
      if self.getConfProperty('ZMS.http_accept_language',0)==1:
        accept = REQUEST.get('HTTP_ACCEPT_LANGUAGE','')
        if accept.find( ';') >= 0:
          accept = accept[ : accept.find( ';')]
        m = { 'de' : 'ger', 'en' : 'eng', 'fr' : 'fra', 'ru' : 'rus', 'es' : 'esp', 'it' : 'ita', 'nl' : 'nld', 'sv' : 'swe'}
        for l in accept.split( ','):
          if l.find( '-') > 0:
            l = l[ : l.find( '-')]
          if l in langs:
            lang = l
            break
          elif l in m.keys() and m[ l] in langs:
            lang = m[ l]
            break
      return lang


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.setLanguage: 
    # 
    #  Set/add language with specified values.
    # --------------------------------------------------------------------------
    def setLanguage(self, lang, label, parent, newManage=None):
      
      if len(parent) == 0:
        primLangOld = self.getPrimaryLanguage()
        for id in self.getLangs().keys():
          if id != lang and self.getParentLanguage(id) == '':
            attr_languages = self.getLangs()
            attr_languages[id]['parent'] = lang
            self.attr_languages = attr_languages.copy()
        self.setPrimaryLanguage(lang)
      
      #-- Set/Add language.
      attr_languages = self.getLangs()
      attr_languages[lang] = {}
      attr_languages[lang]['label'] = label
      attr_languages[lang]['parent'] = parent
      if newManage is not None: attr_languages[lang]['manage'] = newManage
      self.attr_languages = attr_languages.copy()
      
      #-- Set/Add Standard DTML-Methods.
      self.setLangMethods(lang)
      
      #-- Recreate catalog.
      self.recreateCatalog()


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.setLangMethods: 
    # 
    #  Set/Add Standard DTML-Methods.
    # --------------------------------------------------------------------------
    def setLangMethods(self, lang):
      setMethod(self,'stylesheet_%s.css'%lang,STYLESHEET_CSS)
      pageexts = ['.html']
      if 'attr_pageext' in self.getMetadictAttrs():
        metadictAttr = self.getMetadictAttr('attr_pageext')
        if metadictAttr.has_key('keys') and len(metadictAttr.get('keys')) > 0:
          pageexts = metadictAttr.get('keys')
      for pageext in pageexts:
        setMethod(self,'index_%s%s'%(lang,pageext),'<dtml-var index_html>')
        setMethod(self,'sitemap_%s%s'%(lang,pageext),'<dtml-call "REQUEST.set(\'op\',\'sitemap\')"><dtml-var index_html>')
        setMethod(self,'index_print_%s%s'%(lang,pageext),'<dtml-call "REQUEST.set(\'op\',\'print\')"><dtml-var index_html>')
        setMethod(self,'search_%s%s'%(lang,pageext),'<dtml-call "REQUEST.set(\'op\',\'search\')"><dtml-var index_html>')


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.delLanguage: 
    # 
    #  Delete language.
    # --------------------------------------------------------------------------
    def delLanguage(self, lang):
      
      #-- Delete language.
      dctLanguages = self.getLangs()
      self.attr_languages = {}
      for id in dctLanguages.keys():
        if id != lang:
          self.attr_languages[id] = dctLanguages[id]
      self.attr_languages = self.attr_languages.copy()
      
      #-- Delete Standard DTML-Methods.
      delMethod(self,'stylesheet_%s.css'%lang)
      pageexts = ['.html']
      if 'attr_pageext' in self.getMetadictAttrs():
        metadictAttr = self.getMetadictAttr('attr_pageext')
	pageexts = metadictAttr.get('keys',pageexts)
      for pageext in pageexts:
        delMethod(self,'index_%s%s'%(lang,pageext))
        delMethod(self,'sitemap_%s%s'%(lang,pageext))
        delMethod(self,'index_print_%s%s'%(lang,pageext))
        delMethod(self,'search_%s%s'%(lang,pageext))
      
      #-- Recreate catalog.
      self.recreateCatalog()


    ############################################################################
    #  MultiLanguageManager.manage_changeLanguages:
    #
    #  Change languages.
    ############################################################################
    def manage_changeLanguages(self, lang, manage_lang, REQUEST, RESPONSE):
        """ MultiLanguageManager.manage_changeLanguages """
        
        # Delete.
        # -------
        if REQUEST['btn'] == self.getLangStr('BTN_DELETE',manage_lang):
          ids = REQUEST.get('ids',[])
          for id in ids:
            self.delLanguage(id) 
        
        # Change.
        # -------
        elif REQUEST['btn'] == self.getLangStr('BTN_CHANGE',manage_lang):
          for id in self.getLangIds():
            newLabel = REQUEST.get('%s_label'%id).strip()
            newParent = REQUEST.get('%s_parent'%id).strip()
            newManage = REQUEST.get('%s_manage'%id).strip()
            self.setLanguage(id, newLabel, newParent, newManage)
        
        # Insert.
        # -------
        elif REQUEST['btn'] == self.getLangStr('BTN_INSERT',manage_lang):
          id = REQUEST['language_id']
          newLabel = REQUEST.get('language_label').strip()
          if len(self.getLangIds()) == 0:
            newParent = ''
          else:
            newParent = REQUEST.get('language_parent').strip()
          newManage = REQUEST.get('language_manage').strip()
          self.setLanguage(id, newLabel, newParent, newManage)
        
        # Return with message.
        message = urllib.quote(self.getLangStr('MSG_CHANGED',manage_lang))
        return RESPONSE.redirect('manage_customizeLanguagesForm?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(lang,manage_lang,message))


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.get_lang_dict:
    #
    #  Returns language-dictionary.
    # --------------------------------------------------------------------------
    def get_lang_dict(self):
      d = {}
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        masterLangDict = portalMaster.get_lang_dict()
        for key in masterLangDict.keys():
          d[key] = masterLangDict[key].copy()
          d[key]['acquired'] = self.concat_list(d[key].get('acquired',[]),d[key].keys())
      langDict = self.getConfProperty('ZMS.custom.langs.dict',{})
      for key in langDict.keys():
        if d.has_key(key):
          for langKey in langDict[key].keys():
            d[key][langKey] = langDict[key][langKey]
        else:
          d[key] = langDict[key].copy()
      return d


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLangDict:
    #
    #  Returns list of entries from language-dictionary (ordered by key).
    # --------------------------------------------------------------------------
    def getLangDict(self):
      lang_dict = self.get_lang_dict()
      lang_list = []
      keys = lang_dict.keys()
      keys.sort()
      for key in keys:
        d = lang_dict[key]
        d['key'] = key
        lang_list.append(d)
      return lang_list


    ############################################################################
    #  MultiLanguageManager.manage_changeLangDictProperties:
    #
    #  Change property of language-dictionary.
    ############################################################################
    def manage_changeLangDictProperties(self, lang, manage_lang, REQUEST, RESPONSE):
        """ MultiLanguageManager.manage_changeLangDictProperties """
        
        # Delete.
        # -------
        if REQUEST['btn'] == self.getLangStr('BTN_DELETE',manage_lang):
          ids = REQUEST.get('ids',[])
          dict = self.get_lang_dict()
          lang_dict = {}
          for id in dict.keys():
            if not id in ids:
              lang_dict[id] = dict[id]
          self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())
        
        # Change.
        # -------
        elif REQUEST['btn'] == self.getLangStr('BTN_CHANGE',manage_lang):
          d = self.get_lang_dict()
          lang_dict = {}
          for key in d.keys():
            lang_dict[key] = {}
            for s_lang in self.getLangIds():
              enabled = s_lang not in d[key].get('acquired',[])
	      if enabled:
                lang_dict[key][s_lang] = REQUEST['%s_value_%s'%(key,s_lang)].strip()
          self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())
        
        # Insert.
        # -------
        elif REQUEST['btn'] == self.getLangStr('BTN_INSERT',manage_lang):
          id = ''
          key = REQUEST['%s_key'%(id)].strip()
          lang_dict = self.get_lang_dict()
          lang_dict[key] = {}
          for s_lang in self.getLangIds():
            lang_dict[key][s_lang] = REQUEST['%s_value_%s'%(id,s_lang)].strip()
          self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())
        
        # Export.
        # -------
        elif REQUEST['btn'] == self.getLangStr('BTN_EXPORT',manage_lang):
          value = []
          ids = REQUEST.get('ids',[])
          dict = self.get_lang_dict()
          for id in dict.keys():
            item = dict[id].copy()
            item['key'] = id
            if id in ids or len(ids) == 0:
              value.append(item)
          if len(value)==1:
            value = value[0]
          content_type = 'text/xml; charset=utf-8'
          filename = 'export.langdict.xml'
          export = self.getXmlHeader() + self.toXmlString(value,1)
          RESPONSE.setHeader('Content-Type',content_type)
          RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
          return export
        
        # Import.
        # -------
        elif REQUEST['btn'] == self.getLangStr('BTN_IMPORT',manage_lang):
          f = REQUEST['file']
	  if f:
	    filename = f.filename
            importXml(self,xml=f)
	  else:
            filename = REQUEST['init']
	    createIfNotExists = 1
	    self.importConf(filename, REQUEST, createIfNotExists)
          message = self.getLangStr('MSG_IMPORTED',manage_lang)%('<i>%s</i>'%filename)
        
        # Return with message.
        message = urllib.quote(self.getLangStr('MSG_CHANGED',manage_lang))
        return RESPONSE.redirect('manage_customizeLanguagesForm?lang=%s&manage_lang=%s&manage_tabs_message=%s#langdict'%(lang,manage_lang,message))

################################################################################
