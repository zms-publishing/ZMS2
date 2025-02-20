################################################################################
# _multilangmanager.py
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
from App.special_dtml import HTMLFile
from App.Common import package_home
import OFS.misc_
import copy
import urllib
import zope.interface
# Product Imports.
import IZMSLocale
import _fileutil
import _globals
import _xmllib
import cgi


# ------------------------------------------------------------------------------
#  importXml
# ------------------------------------------------------------------------------
def _importXml(self, item, zms_system=0, createIfNotExists=1):
  if createIfNotExists:
    key = item['key']
    lang_dict = self.get_lang_dict()
    lang_dict[key] = {}
    for langId in self.getLangIds():
      if item.has_key(langId):
        lang_dict[key][langId] = item[langId]
    self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  if type(xml) is not str:
    xml = xml.read()
  value = self.parseXmlString(xml)
  if value is None:
    value = []
    builder = _xmllib.XmlBuilder()
    nWorkbook = builder.parse(xml)
    for nWorksheet in _xmllib.xmlNodeSet(nWorkbook,'Worksheet'):
      for nTable in _xmllib.xmlNodeSet(nWorksheet,'Table'):
        r = 0
        keys = []
        for nRow in _xmllib.xmlNodeSet(nTable,'Row'):
          c = 0
          for nCell in _xmllib.xmlNodeSet(nRow,'Cell'):
            for nData in _xmllib.xmlNodeSet(nCell,'Data'):
              if r == 0:
                if c == 0:
                  key = 'key'
                else:
                  key = nData.get('cdata','')
                keys.append(key)
              else:
                if c == 0:
                  value.append({})
                value[-1][keys[c]] = nData.get('cdata','')
              c += 1
          r += 1
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
#  _multilangmanager.setLangMethod:
# 
#  Set/add DTML-Method (e.g. index_lang.html) for specified language.
# ------------------------------------------------------------------------------
def setLangMethod(self, id, raw):
  # delete method (if already exists)
  delLangMethod(self, id)
  # add method
  title = '*** DO NOT DELETE OR MODIFY ***'
  self.manage_addDTMLMethod(id,title,raw)


# ------------------------------------------------------------------------------
#  _multilangmanager.delLangMethod:
# 
#  Delete DTML-Method (e.g. index_lang.html) for specified language.
# ------------------------------------------------------------------------------
def delLangMethod(self, id):
  try: 
    self.manage_delObjects(ids=[id])
  except:
    pass


################################################################################
################################################################################
###
###   class lamgdict:
###
################################################################################
################################################################################
class langdict:

    def __init__(self, filename='_language.xml'):
      """
      Constructor 
      """
      manage_langs = []
      lang_dict = {}
      filepath = package_home(globals())+'/import/'
      xmlfile = open(_fileutil.getOSPath(filepath+filename),'rb')
      builder = _xmllib.XmlBuilder()
      nWorkbook = builder.parse(xmlfile)
      for nWorksheet in _xmllib.xmlNodeSet(nWorkbook,'Worksheet'):
        for nTable in _xmllib.xmlNodeSet(nWorksheet,'Table'):
          for nRow in _xmllib.xmlNodeSet(nTable,'Row'):
            lRow = []
            currIndex = 0
            for nCell in _xmllib.xmlNodeSet(nRow,'Cell'):
              ssIndex = int(nCell.get('attrs',{}).get('ss:Index',currIndex+1))
              currData = None
              for i in range(currIndex+1,ssIndex):
                lRow.append(currData)
              for nData in _xmllib.xmlNodeSet(nCell,'Data'):
                currData = nData['cdata']
              lRow.append(currData)
              currIndex = ssIndex
            if len(manage_langs) == 0:
              del lRow[0]
              manage_langs = lRow
            else:
              if len(lRow) > 0:
                key = lRow[0]
                value = {}
                for i in range(len(manage_langs)):
                  if i+1 < len(lRow):
                    if lRow[i+1] is not None:
                      value[manage_langs[i]] = lRow[i+1] # unicode(lRow[i+1],'utf-8').encode('utf-8')
                lang_dict[key] = value
      xmlfile.close()
      self.manage_langs = manage_langs
      self.langdict = lang_dict

    def get_manage_langs(self):
      """
      Returns list of manage-languages.
      """
      return self.manage_langs

    def get_langdict(self):
      """
      Returns list of manage-languages.
      """
      return self.langdict


################################################################################
################################################################################
###
###   C l a s s   M u l t i L a n g u a g e O b j e c t
###
################################################################################
################################################################################
class MultiLanguageObject:

    def getLanguages(self, REQUEST=None):
      """
      Returns IDs of languages (primary language 1st)
      """
      
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


    def getDescendantLanguages(self, id, REQUEST=None):
      """
      Returns IDs of descendant languages
      """
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
    zope.interface.implements(
        IZMSLocale.IZMSLocale)

    def get_manage_langs(self):
      """
      Returns list of manage-languages.
      """
      return OFS.misc_.misc_.zms['langdict'].get_manage_langs()

    def get_manage_lang(self):
      """
      Returns preferred of manage-language for current content-language.
      """
      manage_lang = None
      req = getattr( self, 'REQUEST', None)
      if req is not None:
        sess = _globals.get_session(self)
        if req.form.has_key('manage_lang'):
          manage_lang = req.get('manage_lang')
        else:
          if sess is not None and not req.form.has_key('reset_manage_lang'):
            manage_lang = sess.get('manage_lang')
          if manage_lang is None:
            lang = req.get('lang')
            if lang in self.getLangIds():
              manage_lang = self.getLang(lang).get('manage')
        if sess is not None:
          sess.set('manage_lang',manage_lang)
      if manage_lang is None:
        manage_lang = 'eng'
      return manage_lang

    def getZMILangStr(self, key, REQUEST=None, RESPONSE=None):
      """
      Returns language-string for current manage-language.
      """
      lang_str = self.getLangStr( key, self.get_manage_lang())
      if RESPONSE is not None:
        if REQUEST.get('nocache'):
          RESPONSE.setHeader('Cache-Control','no-cache')
          RESPONSE.setHeader('Pragma', 'no-cache')
        else:
          RESPONSE.setHeader('Cache-Control','public, max-age=3600')
        RESPONSE.setHeader('Content-Type', 'text/plain; charset=utf-8')
      return lang_str

    def getLangStr(self, key, lang=None):
      """
      Returns language-string for current content-language.
      """
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      
      # Return custom value.
      try:
        d = self.get_lang_dict(forcedReqBuff=True)
        if d.has_key(key):
          if d[key].has_key(lang):
            return d[key][lang]
      except:
        pass
      
      # Return system value.
      d = OFS.misc_.misc_.zms['langdict'].get_langdict()
      if d.has_key(key):
        if not d[key].has_key(lang):
          lang = 'eng'
        if d[key].has_key(lang):
          return d[key][lang]
      
      return cgi.escape(key)


    def getPrimaryLanguage(self):
      """
      Get id of primary-language
      """
      return self.language_primary

    def setPrimaryLanguage(self, v):
      """
      Set id of primary-language
      """
      self.language_primary = v


    def getLangs(self):
      """
      Get language-dictionary
      """
      return getattr(self,'attr_languages',{})

    def setLangs(self, v):
      """
      Set language-dictionary
      """
      self.attr_languages = v.copy()


    def getParentLanguage(self, id):
      """
      Returns label of language specified by ID.
      """
      return self.getLang(id).get('parent')


    def getLanguageLabel(self, id):
      """
      Returns label of language specified by ID.
      """
      return self.getLang(id).get('label',id)


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
    #  MultiLanguageManager.getLang: 
    # --------------------------------------------------------------------------
    def getLang(self, id):
      return self.getLangs().get(id,{})


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLangTree:
    #
    #  Returns list of Ids of languages (primary language 1st).
    # --------------------------------------------------------------------------
    def getLangTree(self, base=None):
      if base is None:
        base = self.getPrimaryLanguage()
      l = [(base,self.getLang(base))]
      for langId in self.getLangIds():
        lang = self.getLang(langId)
        if lang['parent'] == base:
          l.extend(self.getLangTree(langId))
      return l


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.getLangIds:
    #
    #  Returns list of Ids of languages (primary language 1st).
    # --------------------------------------------------------------------------
    def getLangIds(self, sort=False):
      obs = []
      langs = self.getLangs()
      if sort:
        for key in langs.keys():
          if key == self.getPrimaryLanguage(): 
            label = '*'
          else: 
            label = langs[key]['label']
          obs.append((label,key))
        obs.sort()
        return map(lambda ob: ob[1],obs)
      return langs.keys()


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
    def setLanguage(self, lang, label, parent, newManage):
      
      if len(parent) == 0:
        for id in self.getLangs().keys():
          if id != lang and self.getParentLanguage(id) == '':
            attr_languages = self.getLangs()
            attr_languages[id]['parent'] = lang
            self.setLangs( attr_languages)
        self.setPrimaryLanguage(lang)
      
      #-- Set/Add language.
      attr_languages = self.getLangs()
      attr_languages[lang] = {}
      attr_languages[lang]['label'] = label
      attr_languages[lang]['parent'] = parent
      attr_languages[lang]['manage'] = newManage
      self.setLangs( attr_languages)
      
      #-- Set/Add Standard DTML-Methods.
      self.setLangMethods(lang)


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.setLangMethods: 
    # 
    #  Set/Add Standard DTML-Methods.
    # --------------------------------------------------------------------------
    def setLangMethods(self, lang):
      pageexts = ['.html']
      if 'attr_pageext' in self.getObjAttrs().keys():
        obj_attr = self.getObjAttr('attr_pageext')
        if obj_attr.has_key('keys') and len(obj_attr.get('keys')) > 0:
          pageexts = obj_attr.get('keys')
      for pageext in pageexts:
        setLangMethod(self,'index_%s%s'%(lang,pageext),'<dtml-var index_html>')
        setLangMethod(self,'sitemap_%s%s'%(lang,pageext),'<dtml-call "REQUEST.set(\'op\',\'sitemap\')"><dtml-var index_html>')
        setLangMethod(self,'index_print_%s%s'%(lang,pageext),'<dtml-call "REQUEST.set(\'op\',\'print\')"><dtml-var index_html>')
        setLangMethod(self,'search_%s%s'%(lang,pageext),'<dtml-call "REQUEST.set(\'op\',\'search\')"><dtml-var index_html>')


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.delLanguage: 
    # 
    #  Delete language.
    # --------------------------------------------------------------------------
    def delLanguage(self, lang):
      
      #-- Delete language.
      attr_languages = self.getLangs()
      del attr_languages[lang]
      self.setLangs( attr_languages)
      
      #-- Delete Standard DTML-Methods.
      pageexts = ['.html']
      if 'attr_pageext' in self.getObjAttrs().keys():
        obj_attr = self.getObjAttr('attr_pageext')
        pageexts = obj_attr.get('keys',pageexts)
      for pageext in pageexts:
        delLangMethod(self,'index_%s%s'%(lang,pageext))
        delLangMethod(self,'sitemap_%s%s'%(lang,pageext))
        delLangMethod(self,'index_print_%s%s'%(lang,pageext))
        delLangMethod(self,'search_%s%s'%(lang,pageext))


    ############################################################################
    #  MultiLanguageManager.manage_changeLanguages:
    #
    #  Change languages.
    ############################################################################
    def manage_changeLanguages(self, lang, REQUEST, RESPONSE):
      """ MultiLanguageManager.manage_changeLanguages """
      
      # Delete.
      # -------
      if REQUEST['btn'] == self.getZMILangStr('BTN_DELETE'):
        ids = REQUEST.get('ids',[])
        for id in ids:
          self.delLanguage(id) 
      
      # Change.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_SAVE'):
        for id in self.getLangIds():
          newLabel = REQUEST.get('%s_label'%id).strip()
          newParent = REQUEST.get('%s_parent'%id).strip()
          newManage = REQUEST.get('%s_manage'%id).strip()
          self.setLanguage(id, newLabel, newParent, newManage)
        # Insert
        newId = REQUEST.get('language_id').strip()
        if len(newId) > 0:
          newLabel = REQUEST.get('language_label').strip()
          if len(self.getLangIds()) == 0:
            newParent = ''
          else:
            newParent = REQUEST.get('language_parent').strip()
          newManage = REQUEST.get('language_manage').strip()
          self.setLanguage(newId, newLabel, newParent, newManage)
      
      # Return with message.
      message = urllib.quote(self.getZMILangStr('MSG_CHANGED'))
      return RESPONSE.redirect('manage_customizeLanguagesForm?lang=%s&manage_tabs_message=%s'%(lang,message))


    # --------------------------------------------------------------------------
    #  MultiLanguageManager.get_lang_dict:
    #
    #  Returns language-dictionary.
    # --------------------------------------------------------------------------
    def get_lang_dict(self, forcedReqBuff=False):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'get_lang_dict'
      try:
        d = self.fetchReqBuff( reqBuffId, self.REQUEST, forced=forcedReqBuff)
        return d
      except:
        
        #-- Get value.
        d = {}
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          lang_dict = portalMaster.get_lang_dict()
          for key in lang_dict.keys():
            d[key] = lang_dict[key].copy()
            lang_ids = lang_dict[key].keys()
            d[key]['acquired'] = self.concat_list(d[key].get('acquired',[]),lang_ids)
        lang_dict = self.getConfProperty('ZMS.custom.langs.dict',{})
        for key in lang_dict.keys():
          if d.has_key(key):
            lang_ids = lang_dict[key].keys()
            for lang_id in lang_ids:
              if lang_id not in d[key].get('acquired',[]):
                d[key][lang_id] = lang_dict[key][lang_id]
          else:
            d[key] = lang_dict[key].copy()
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, d, self.REQUEST)


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
    def manage_changeLangDictProperties(self, lang, REQUEST, RESPONSE):
        """ MultiLanguageManager.manage_changeLangDictProperties """
        
        # Delete.
        # -------
        if REQUEST['btn'] == self.getZMILangStr('BTN_DELETE'):
          ids = REQUEST.get('ids',[])
          dict = self.get_lang_dict()
          lang_dict = {}
          for id in dict.keys():
            if not id in ids:
              lang_dict[id] = dict[id]
          self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())
        
        # Change.
        # -------
        elif REQUEST['btn'] == self.getZMILangStr('BTN_SAVE'):
          d = self.get_lang_dict()
          lang_dict = {}
          for key in d.keys():
            for lang_id in self.getLangIds():
              lang_dict[key] = lang_dict.get(key,{})
              enabled = lang_id not in d[key].get('acquired',[])
              if enabled:
                lang_dict[key][lang_id] = REQUEST['%s_value_%s'%(key,lang_id)].strip()
          # Insert
          key = REQUEST['_key'].strip()
          if len(key) > 0:
            lang_dict = self.get_lang_dict()
            lang_dict[key] = {}
            for lang_id in self.getLangIds():
              lang_dict[key][lang_id] = REQUEST['_value_%s'%lang_id].strip()
          self.setConfProperty('ZMS.custom.langs.dict',lang_dict.copy())
        
        # Export.
        # -------
        elif REQUEST['btn'] == self.getZMILangStr('BTN_EXPORT'):
          value = []
          ids = REQUEST.get('ids',[])
          dict = self.get_lang_dict()
          for id in dict.keys():
            item = dict[id].copy()
            item['key'] = id
            if id in ids or len(ids) == 0:
              value.append(item)
          REQUEST.set('context',self)
          REQUEST.set('value',value)
          tmplt = HTMLFile('dtml/ZMS/manage_exportlanguages', globals())
          export = tmplt(self,REQUEST)
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
        message = urllib.quote(self.getZMILangStr('MSG_CHANGED'))
        return RESPONSE.redirect('manage_customizeLanguagesForm?lang=%s&manage_tabs_message=%s#langdict'%(lang,message))

################################################################################
