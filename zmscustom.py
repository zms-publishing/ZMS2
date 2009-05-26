################################################################################
# zmscustom.py
#
# $Id: zmscustom.py,v 1.9 2004/11/30 20:04:16 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.9 $
#
# Implementation of class ZMSCustom (see below).
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
from types import StringTypes
import ZPublisher.HTTPRequest
import sys
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
from zmsobject import ZMSObject
import zmsteaserelement
import _blobfields
import _fileutil
import _globals
import _importable
import _metaobjmanager


# ------------------------------------------------------------------------------
#  zmscustom.parseXmlString
# ------------------------------------------------------------------------------
def parseXmlString(self, file):
  _globals.writeBlock( self, '[parseXmlString]')
  message = ''
  REQUEST = self.REQUEST
  lang = REQUEST.get( 'lang', self.getPrimaryLanguage())
  v = self.parseXmlString(file)
  metaObj = self.getMetaobj(self.meta_id)
  res_id = metaObj['attrs'][0]['id']
  res_abs = self.getObjProperty(res_id,REQUEST)
  res_abs.extend(v)
  self.setObjStateModified(REQUEST)
  self.setObjProperty(res_id,res_abs,lang)
  self.onChangeObj(REQUEST)
  return message


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################

manage_addZMSCustomForm = HTMLFile('manage_addzmscustomform', globals()) 
def manage_addZMSCustom(self, meta_id, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSCustom """
  
  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSCustom(self.getNewId(id_prefix),_sort_id+1,meta_id)
    self._setObject(obj.id, obj)
    
    redirect_self = False
    redirect_self = redirect_self or REQUEST.get('btn','') == '' 
    for attr in self.getMetaobj(meta_id)['attrs']:
      attr_type = attr['type']
      redirect_self = redirect_self or attr_type in self.dGlobalAttrs.keys()
      redirect_self = redirect_self or attr_type in self.getMetaobjIds()
      redirect_self = redirect_self or attr_type in ['*']
    redirect_self = redirect_self and not REQUEST.get('btn','') in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]
  
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
    obj.manage_changeProperties(lang,REQUEST,RESPONSE)
  
    ##### Normalize Sort-IDs ####
    self.normalizeSortIds(id_prefix)
  
    # Return with message.        
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    if redirect_self:
      RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,urllib.quote(message)))
    else:
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(self.absolute_url(),lang,urllib.quote(message),obj.id))

  else:
    RESPONSE.redirect('%s/manage_main?lang=%s'%(self.absolute_url(),lang))


################################################################################
################################################################################
###   
###   C l a s s
###   
################################################################################
################################################################################

class ZMSCustom(ZMSContainerObject): 
        
    # Properties.
    # -----------
    meta_type = "ZMSCustom"
    icon = "misc_/zms/zmsdocument.gif"
    icon_disabled = "misc_/zms/zmsdocument_disabled.gif"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',         'action': 'manage_main'},
	{'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'},
	{'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'},
	{'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_PREVIEW',      'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace','manage_checkout',
		'manage_addZMSFolder','manage_addZMSDocument','manage_addZMSTextarea','manage_addZMSGraphic','manage_addZMSTable','manage_addZMSFile','manage_addZMSTeaserContainer','manage_addZMSNote','manage_addZMSLinkContainer','manage_addZMSLinkElement','manage_addZMSSqlDb','manage_addZMSModule',
		'manage_changeProperties',
		'manage_deleteObjs','manage_undoObjs','manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm', 'manage_user',
		'manage_importexport', 'manage_import', 'manage_export',
		)
    __administratorPermissions__ = (
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		('ZMS Administrator', __administratorPermissions__),
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
        'change_history':{'datatype':'list','xml':False,'default':[]},
        'master_version':{'datatype':'int','xml':False,'default':0},
        'major_version':{'datatype':'int','xml':False,'default':0},
        'minor_version':{'datatype':'int','xml':False,'default':0},
        # Versioned by
        'work_uid':{'datatype':'string','multilang':True,'xml':False,'lang_inherit':False},
        'work_dt':{'datatype':'datetime','multilang':True,'xml':False,'lang_inherit':False},
        # Properties
        'active':{'datatype':'boolean','multilang':True},
        'attr_active_start':{'datatype':'datetime','multilang':True},
        'attr_active_end':{'datatype':'datetime','multilang':True},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/metaobj/manage_main', globals())
    manage_form = HTMLFile('dtml/metaobj/manage_form', globals())


    """
    ############################################################################    
    #
    #   CONSTRUCTOR
    #
    ############################################################################    
    """

    ############################################################################
    # ZMSCustom.__init__: 
    #
    # Constructor (initialise a new instance of ZMSCustom).
    ############################################################################
    def __init__(self, id='', sort_id='', meta_id=''): 
      """ ZMSCustom.__init__ """
      ZMSObject.__init__(self,id,sort_id)
      self.meta_id = meta_id


    # --------------------------------------------------------------------------
    #  ZMSCustom.meta_id_or_type:
    # --------------------------------------------------------------------------
    def meta_id_or_type(self):
      return self.meta_id


    """
    ############################################################################    
    ###
    ###   H t t p
    ###
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ZMSCustom.GET: 
    #
    #  Handle HTTP GET requests.
    # --------------------------------------------------------------------------
    def GET(self, REQUEST, RESPONSE):
      """Handle HTTP GET requests."""
      metaObjAttrs = self.getMetaobj(self.meta_id)['attrs']
      i = 0
      while 1:
        if i >= len(metaObjAttrs): break
        objAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrs[i]['id'])
        if objAttr['type'] in ['string','text']:
          lang = self.getPrimaryLanguage()
          REQUEST.set('lang',lang)
          REQUEST.set('preview','preview')
          return self.getObjProperty(objAttr['id'],REQUEST)
        i = i + 1
      return ''


    # --------------------------------------------------------------------------
    #  ZMSCustom.PUT: 
    #
    #  Handle HTTP PUT requests.
    # --------------------------------------------------------------------------
    def PUT(self, REQUEST, RESPONSE):
      """Handle HTTP PUT requests."""
      metaObjAttrs = self.getMetaobj(self.meta_id)['attrs']
      i = 0
      while 1:
        if i >= len(metaObjAttrs): break
        objAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrs[i]['id'])
        if objAttr['type'] in ['string','text']:
          lang = self.getPrimaryLanguage()
          REQUEST.set('lang',lang)
          self.setObjStateModified(REQUEST)
          self.setObjProperty(objAttr['id'],REQUEST.get('BODY', ''),lang)
          self.onChangeObj(REQUEST)
          break
        i = i + 1
      RESPONSE.setStatus(204)
      return RESPONSE


    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSCustom.manage_changeProperties: 
    #
    #  Change Custom properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE):
      """ ZMSCustom.manage_changeProperties """
      
      self._checkWebDAVLock()
      message = ''
      messagekey = 'manage_tabs_message'
      t0 = time.time()
      
      redirect_self = False
      redirect_self = redirect_self or REQUEST.get('btn','') == '' 
      for attr in self.getMetaobj(self.meta_id)['attrs']:
        attr_type = attr['type']
        redirect_self = redirect_self or attr_type in self.dGlobalAttrs.keys()
        redirect_self = redirect_self or attr_type in self.getMetaobjIds()
        redirect_self = redirect_self or attr_type in ['*']
      redirect_self = redirect_self and not REQUEST.get('btn','') in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]
      target_ob = self.getParentNode()
      if redirect_self:
        target_ob = self
      target = REQUEST.get( 'target', '%s/manage_main'%target_ob.absolute_url())
      
      if REQUEST.get('btn','') not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        try:
          
          ##### Object State #####
          self.setObjStateModified(REQUEST)
          
          ##### Resources #####
          if 'resources' in self.getMetaobjAttrIds( self.meta_id):
            resources = self.getObjProperty( 'resources', REQUEST)
            l = map( lambda x: 0, range( len( resources)))
            for key in self.getObjAttrs().keys():
              obj_attr = self.getObjAttr( key)
              el_name = self.getObjAttrName( obj_attr, lang)
              if REQUEST.has_key( el_name) and REQUEST.has_key( 'resource_%s'%el_name):
                el_value = REQUEST.get( el_name)
                if el_value is not None:
                  for i in range( len( resources)):
                    v = resources[ i]
                    if el_value.find( '/'+v.getFilename()) > 0:
                      l[ i] = l[ i] + 1
            c = 0 
            for i in range( len( resources)):
              v = resources[ c]
              if l[ i] == 0:
                del resources[ c]
              else:
                src_old = '%s/@%i/%s'%(self.id,i,v.getFilename())
                src_new = '%s/@%i/%s'%(self.id,c,v.getFilename())
                for key in self.getObjAttrs().keys():
                  obj_attr = self.getObjAttr( key)
                  el_name = self.getObjAttrName( obj_attr, lang)
                  if REQUEST.has_key( el_name) and REQUEST.has_key( 'resource_%s'%el_name):
                    el_value = REQUEST.get( el_name)
                    if el_value is not None:
                      el_value = el_value.replace( src_old, src_new)
                      REQUEST.set( el_name, el_value)
                c = c + 1
            for key in self.getObjAttrs().keys():
              obj_attr = self.getObjAttr( key)
              el_name = self.getObjAttrName( obj_attr, lang)
              if REQUEST.has_key( el_name) and REQUEST.has_key( 'resource_%s'%el_name):
                v = REQUEST.get( 'resource_%s'%el_name)
                if isinstance(v,ZPublisher.HTTPRequest.FileUpload):
                  if len(getattr(v,'filename',''))>0:
                    v = _blobfields.createBlobField(self,_globals.DT_FILE,v)
                    resources.append( v)
                    el_value = REQUEST.get( el_name)
                    if el_value is not None:
                      src_new = '%s/@%i/%s'%(self.absolute_url(),len(resources)-1,v.getFilename())
                      if v.getContentType().find( 'image/') == 0:
                        el_value = el_value + '<img src="%s" alt="" border="0" align="absmiddle"/>'%src_new
                      else:
                        el_value = el_value + '<a href="%s" target="_blank">%s</a>'%(src_new,v.getFilename())
                      REQUEST.set( el_name, el_value)
                      redirect_self = True
            self.setObjProperty( 'resources', resources, lang)
          
          ##### Properties #####
          for key in self.getObjAttrs().keys():
            if key != 'resources':
              self.setReqProperty(key,REQUEST)
          
          ##### Resource-Objects #####
          for objAttr in self.getMetaobj(self.meta_id)['attrs']:
            if objAttr['type'] in self.getMetaobjIds(sort=0) and \
               self.getMetaobj(objAttr['type'])['type']=='ZMSResource':
              for ob in self.getObjChildren(objAttr['id'],REQUEST):
                ob.setObjStateModified(REQUEST)
                for key in ob.getObjAttrs().keys():
                  ob.setReqProperty(key,REQUEST)
                ob.onChangeObj(REQUEST)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
          
          ##### Message ####
          message = self.getZMILangStr('MSG_CHANGED')
        
        except:
          tp, vl, tb = sys.exc_info()
          message = '<b>Error-Type:</b> '+str(tp)+'<br/><b>Error-Value:</b> '+str(vl)+'<br/>'
          messagekey = 'manage_tabs_error_message'
          _globals.writeException(self,"[manage_changeProperties]")
        
        message = message + ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      
      # Return with message.
      self.checkIn(REQUEST)
      target = self.url_append_params( target, { 'lang': lang, 'preview': 'preview',  messagekey: message})
      target = '%s#_%s'%( target, self.id)
      return RESPONSE.redirect( target)


    # --------------------------------------------------------------------------
    #  ZMSCustom.getMetaobjZMI:
    # 
    #  Returns Meta-Object Management Interface identified by ID.
    # --------------------------------------------------------------------------
    def getMetaobjZMI(self, id, REQUEST):
      return _metaobjmanager.getMetaobjZMI(self,id,REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSCustom.setMetaType:
    # --------------------------------------------------------------------------
    def setMetaType(self, new_meta_id):
      meta_id = self.meta_id
      metaObjAttrIds = self.getMetaobjAttrIds(meta_id)
      newMetaObjAttrIds = self.getMetaobjAttrIds(new_meta_id)
      for metaObjAttrId in metaObjAttrIds:
        if metaObjAttrId in newMetaObjAttrIds:
          metaObjAttr = self.getMetaobjAttr(meta_id,metaObjAttrId)
          newMetaObjAttr = self.getMetaobjAttr(new_meta_id,metaObjAttrId)
          if metaObjAttr['multilang']==1 and newMetaObjAttr['multilang']==0:
            lang = self.getPrimaryLanguage()
            for obj_vers in self.getObjVersions():
              metaObjAttrIdLang = '%s_%s'%(metaObjAttrId,lang)
              if hasattr(obj_vers,metaObjAttrIdLang):
                setattr(obj_vers,metaObjAttrId,getattr(obj_vers,metaObjAttrIdLang))
              for lang in self.getLangIds():
                metaObjAttrIdLang = '%s_%s'%(metaObjAttrId,lang)
                if hasattr(obj_vers,metaObjAttrIdLang):
                  try: delattr(obj_vers,metaObjAttrIdLang)
                  except: pass
          elif metaObjAttr['multilang']==0 and newMetaObjAttr['multilang']==1:
            lang = self.getPrimaryLanguage()
            for obj_vers in self.getObjVersions():
              metaObjAttrIdLang = '%s_%s'%(metaObjAttrId,lang)
              if hasattr(obj_vers,metaObjAttrId):
                setattr(obj_vers,metaObjAttrIdLang,getattr(obj_vers,metaObjAttrId))
              if hasattr(obj_vers,metaObjAttrId):
                try: delattr(obj_vers,metaObjAttrId)
                except: pass
      self.meta_id = new_meta_id


    # --------------------------------------------------------------------------
    #  ZMSCustom.isMetaType:
    # --------------------------------------------------------------------------
    def isMetaType(self, meta_type, REQUEST={}):
      if meta_type is None:
        return 1
      if not type(meta_type) is list:
        meta_type = [meta_type]
      b = self.meta_id in meta_type
      if not b:
        b = b or ZMSObject.isMetaType(self,meta_type,REQUEST)
      return b
    
    
    # --------------------------------------------------------------------------
    #  ZMSCustom.isPage:
    # --------------------------------------------------------------------------
    def isPage(self): 
      return self.getType() in [ 'ZMSDocument', 'ZMSReference']

    # --------------------------------------------------------------------------
    #  ZMSObject.isPageElement:
    # --------------------------------------------------------------------------
    def isPageElement(self): 
      return self.getType() in [ 'ZMSObject', 'ZMSRecordSet']

    # --------------------------------------------------------------------------
    #  ZMSCustom.getType
    # --------------------------------------------------------------------------
    def getType(self): 
      return self.getMetaobj(self.meta_id)['type']

    # --------------------------------------------------------------------------
    #  ZMSCustom.getDtmlTemplate
    # --------------------------------------------------------------------------
    def getDtmlTemplate(self): 
      return getattr(self,self.getMetaobj(self.meta_id)['tmplt'],None)

    # --------------------------------------------------------------------------
    #  ZMSCustom.getPenetrance
    # --------------------------------------------------------------------------
    def getPenetrance(self, REQUEST):
      penetrance = 0
      if 'attr_penetrance' in self.getObjAttrs().keys():
        i = self.getObjProperty('attr_penetrance',REQUEST)
        lst = zmsteaserelement.lstPenetrance
        if i in lst:
          penetrance = lst[lst.index(i)-1]
      return penetrance

    # --------------------------------------------------------------------------
    #	ZMSCustom.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt(self,REQUEST):
      s = ''
      if self.getType() in ['ZMSRecordSet']:
        s = self.display_type(REQUEST)
      if len(s) == 0:
        metaObjAttrs = self.getMetaobj(self.meta_id)['attrs']
        k = 0
        i = k
        while True:
          if i >= len(metaObjAttrs) or len(s) > 0:
            break
          objAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrs[i]['id'])
          if objAttr['type']=='string' or \
             (i==k and objAttr['type'] in [ 'method', 'constant'] and objAttr['id']=='titlealt') or \
             (i==k and objAttr['type'] in [ 'select']):
            v = self.getObjProperty(objAttr['id'],REQUEST)
            if type(v) in StringTypes:
              s = v
          i = i + 1
      if len(s) == 0: 
        s = self.display_type(REQUEST)
      s = self.getLevelnfc(REQUEST) + s
      return s

    # --------------------------------------------------------------------------
    #	ZMSCustom.getTitle
    # --------------------------------------------------------------------------
    def getTitle(self,REQUEST): 
      s = ''
      if self.getType() in ['ZMSRecordSet']:
        s = self.display_type(REQUEST)
      if len(s) == 0:
        metaObjAttrs = self.getMetaobj(self.meta_id)['attrs']
        k = 1
        i = k
        while True:
          if i >= len(metaObjAttrs) or len(s) > 0:
            break
          objAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrs[i]['id'])
          if objAttr['type']=='string' or \
             (i==k and objAttr['type'] in [ 'method', 'constant'] and objAttr['id']=='title') or \
             (i==k and objAttr['type'] in [ 'select']):
            v = self.getObjProperty(objAttr['id'],REQUEST)
            if type(v) in StringTypes:
              s = v
          i = i + 1
      if len(s) == 0: 
        s = self.display_type(REQUEST)
      s = self.getLevelnfc(REQUEST) + s
      return s


    """
    ############################################################################
    ###
    ###  H T M L - P r e s e n t a t i o n 
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSCustom._getBodyContent:
    #
    #  HTML presentation of Special Document. 
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      l = []
      v = ''
      dtml_tmplt = self.getDtmlTemplate()
      if dtml_tmplt is not None:
        v = dtml_tmplt(self,REQUEST)
        try:
          v = v.encode('utf-8')
        except UnicodeDecodeError:
          v = str(v)
      if self.getType()=='ZMSTeaserElement':
        l.append('<div')
        l.append(' class="ZMSTeaserElement"')
        if REQUEST.has_key('bgcolor_text'):
          l.append(' style="background-color:%s"'%self.get_colormap().get(REQUEST.get('bgcolor_text'),'transparent'))
        l.append('>\n')
        l.append(v)
        l.append('</div>\n')
      else:
        l.append(v)
      return ''.join(l)

    # --------------------------------------------------------------------------
    #  ZMSCustom.renderShort:
    #
    #  Renders short presentation of Special Document.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      html = ''
      try:
        if self.getType() in [ 'ZMSDocument', 'ZMSResource', 'ZMSReference']:
          html += '<h2>%s</h2>'%self.getTitlealt(REQUEST)
        else:
          html += self._getBodyContent(REQUEST)
        # Process html <form>-tags.
        html = _globals.form_quote(html,REQUEST)
      except:
        html += '[Exception in %s.renderShort]:<br/>'%(self.meta_id)
        html += '-  Type: <strong>%s</strong><br/>'%str(sys.exc_type)
        html += '-  Value: <strong>%s</strong><br/>'%str(sys.exc_value)
        html += '-  Traceback: <strong>%s</strong>'%str(sys.exc_traceback)
      # Return <html>.
      return html


    # --------------------------------------------------------------------------
    #  ZMSCustom.printHtml:
    #
    #  Renders print presentation of Special Document.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      html = ''
    
      # Title.
      sectionizer.processLevel( level)
      title = self.getTitle( REQUEST)
      title = '%s %s'%(str(sectionizer),title)
      REQUEST.set( 'ZMS_SECTIONIZED_TITLE', '<h%i>%s</h%i>'%( level, title, level))

      # pageregionBefore
      if self.getType() == 'ZMSDocument':
        attr = REQUEST.get( 'ZMS_PAGEREGION_BEFORE', 'pageregionBefore')
        if hasattr( self, attr):
          html += getattr( self, attr)( self, REQUEST)
        elif hasattr( self, 'bodyContent_PagePre'):
          html += getattr( self, 'bodyContent_PagePre')(self,REQUEST)
    
      # bodyContent
      html += self._getBodyContent(REQUEST)
        
      # pageregionAfter
      if self.getType() == 'ZMSDocument':
        attr = REQUEST.get( 'ZMS_PAGEREGION_AFTER', 'pageregionAfter')
        if hasattr( self, attr):
          html += getattr( self, attr)( self, REQUEST)
        elif hasattr( self ,'bodyContent_PagePost'):
          html += getattr( self ,'bodyContent_PagePost')(self,REQUEST)
        
      # Return <html>.
      return html


    """
    ############################################################################    
    ###
    ###   R e c o r d S e t
    ###
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Init:
    #
    #  Initializes RecordSet.
    # --------------------------------------------------------------------------
    def recordSet_Init(self, REQUEST):
      metaObj = self.getMetaobj(self.meta_id)

      res_id = metaObj['attrs'][0]['id']
      res = self.getObjProperty(res_id,REQUEST)
      
      REQUEST.set('res_id',res_id)
      REQUEST.set('res_abs',res)
      REQUEST.set('res',res)
      
      return res


    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Filter:
    #
    #  Filters RecordSet.
    # --------------------------------------------------------------------------
    def recordSet_Filter(self, REQUEST):
      metaObj = self.getMetaobj(self.meta_id)
      
      res_id = REQUEST['res_id']
      res_abs = REQUEST['res_abs']
      res = REQUEST['res']
      
      SESSION = REQUEST.SESSION
      
      # Filter (FK).
      filterattr='fk_key'
      filtervalue='fk_val'
      sessionattr='%s_%s'%(filterattr,self.id)
      sessionvalue='%s_%s'%(filtervalue,self.id)
      SESSION.set(sessionattr,REQUEST.form.get(filterattr,SESSION.get(sessionattr,'')))
      SESSION.set(sessionvalue,REQUEST.form.get(filtervalue,SESSION.get(sessionvalue,'')))
      if REQUEST.get('btn','')==self.getZMILangStr('BTN_RESET'):
        SESSION.set(sessionattr,'')
        SESSION.set(sessionvalue,'')
      if SESSION.get(sessionattr,'') != '' and \
         SESSION.get(sessionvalue,''):
        res = self.filter_list(res,SESSION.get(sessionattr),SESSION.get(sessionvalue),'==')
        masterType = filter(lambda x: x['id']==SESSION.get(sessionattr),metaObj['attrs'][1:])[0]['type']
	master = filter(lambda x: x.meta_id==masterType,self.getParentNode().objectValues(['ZMSCustom']))[0]
	masterMetaObj = self.getMetaobj(masterType)
	masterAttrs = masterMetaObj['attrs']
	masterRows = master.getObjProperty(masterAttrs[0]['id'],REQUEST)
	masterRows = self.filter_list(masterRows,masterAttrs[1]['id'],SESSION.get(sessionvalue),'==')
	REQUEST.set('masterMetaObj',masterMetaObj)
	REQUEST.set('masterRow',masterRows[0])
      
      # Filter (Custom).
      SESSION.set('qfilters',REQUEST.form.get('qfilters',SESSION.get('qfilters',1)))
      for i in range(SESSION['qfilters']):
        filterattr='filterattr%i'%i
        filtervalue='filtervalue%i'%i
        sessionattr='%s_%s'%(filterattr,self.id)
        sessionvalue='%s_%s'%(filtervalue,self.id)
        
        #-- Set filter parameters in Session
        if REQUEST.get('action','')=='':
          if REQUEST.get('btn','')==self.getZMILangStr('BTN_RESET'):
            SESSION.set(sessionattr,'')
            SESSION.set(sessionvalue,'')
          elif REQUEST.get('btn','')==self.getZMILangStr('BTN_REFRESH'):
            SESSION.set(sessionattr,REQUEST.form.get(filterattr,''))
            SESSION.set(sessionvalue,REQUEST.form.get(filtervalue,''))
        
        #-- Apply filter parameters 
        for attr in metaObj['attrs'][1:]:
          if attr.get('name','')!='':
            if SESSION.get(sessionattr,'') == attr['id'] and \
	       SESSION.get(sessionvalue,'') != '':
              attr['datatype_key'] = _globals.datatype_key(attr['type'])
              if attr['datatype_key'] in _globals.DT_NUMBERS:
                res = self.filter_list(res,attr['id'],self.formatObjAttrValue(attr,SESSION.get(sessionvalue,''),REQUEST['lang']))
              else:
                res = self.filter_list(res,attr['id'],SESSION.get(sessionvalue,''))
      
      REQUEST.set('res_id',res_id)
      REQUEST.set('res_abs',res_abs)
      REQUEST.set('res',res)
      
      return res


    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Sort:
    #
    #  Sorts RecordSet.
    # --------------------------------------------------------------------------
    def recordSet_Sort(self, REQUEST):
      metaObj = self.getMetaobj(self.meta_id)
      
      res = REQUEST['res']
      qorder = REQUEST.get('qorder','')
      qorderdir = REQUEST.get('qorderdir','asc')
      for attr in metaObj['attrs'][1:]:
        if attr['id'] == 'sort_id':
          qorder = attr['id']
        if qorder=='':
          if attr.get('type','') not in [ 'constant', 'file', 'image', 'resource'] and \
             attr.get('type','') not in self.getMetaobjIds() and \
             attr.get('name','') != '' and \
             attr.get('custom','') != '':
            qorder = attr['id']
            if attr.get('type','') in ['date','datetime']:
              qorderdir = 'desc'
      res = self.sort_list(res,qorder,qorderdir)
      
      REQUEST.set('res',res)
      REQUEST.set('qorder',qorder)
      REQUEST.set('qorderdir',qorderdir)
      
      return res


    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Export:
    #
    #  Export RecordSet to XML.
    # --------------------------------------------------------------------------
    def recordSet_Export(self, lang, qorder, qorderdir, qindex=[], REQUEST=None, RESPONSE=None):
      """ ZMSCustom.recordSet_Export """
      self.recordSet_Init(REQUEST)
      self.recordSet_Filter(REQUEST)
      self.recordSet_Sort(REQUEST)
      res=REQUEST['res']
      value = []
      for i in range(len(res)):
        if len(qindex)==0 or str(i) in qindex:
          value.append(res[i])
      RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
      RESPONSE.setHeader('Content-Disposition','inline;filename=recordSet_Export.xml')
      export = self.getXmlHeader() + self.toXmlString(value,True)
      return export


    ############################################################################    
    #  ZMSCustom.manage_import:
    #
    #  Import XML-file.
    ############################################################################    
    def manage_import(self, file, lang, REQUEST, RESPONSE):
      """ ZMSCustom.manage_import """
      message = ''
      
      # Import XML-file.
      if REQUEST.get('filter','') in self.getFilterIds():
        message += _importable.importFile( self, file, REQUEST, parseXmlString)
      else:
        message += parseXmlString( self, file)
      
      # Return with message.
      message = urllib.quote(message)
      return REQUEST.RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,message))

################################################################################
