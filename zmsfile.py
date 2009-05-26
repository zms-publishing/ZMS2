################################################################################
# zmsfile.py
#
# $Id: zmsfile.py,v 1.4 2004/11/23 23:04:45 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.4 $
#
# Implementation of class ZMSFile (see below).
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
from Globals import HTMLFile, Persistent
import sys
import time
import urllib
# Product imports.
from zmsobject import ZMSObject
import _fileutil
import _globals


################################################################################
################################################################################
###
###   Constructor(s)
###
################################################################################
################################################################################

manage_addZMSFileForm = HTMLFile('manage_addzmsfileform', globals()) 
def manage_addZMSFile(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSFile """
    
  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSFile(self.getNewId(id_prefix),_sort_id+1)
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
    obj.manage_changeProperties(lang,REQUEST,RESPONSE)

    ##### Normalize Sort-IDs ####
    self.normalizeSortIds(id_prefix)
    
    # Return with message.
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(self.absolute_url(),lang,urllib.quote(message),obj.id))
  
  else:
    RESPONSE.redirect('%s/manage_main?lang=%s'%(self.absolute_url(),lang))



################################################################################
################################################################################
###   
###   Class
###   
################################################################################
################################################################################
class ZMSFile(ZMSObject):
        
    # Properties.
    # -----------
    meta_type = meta_id = 'ZMSFile'
    icon = "misc_/zms/zmsfile.gif"
    icon_disabled = 'misc_/zms/zmsfile_disabled.gif'

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',       'action': 'manage_main'},
	{'label': 'TAB_REFERENCES', 'action': 'manage_RefForm'},
	{'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_PREVIEW',    'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace','manage_checkout',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_changeProperties',
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
        'title':{'datatype':'string','multilang':True,'size':40},
        'titleshort':{'datatype':'string','multilang':True,'size':20},
        'file':{'datatype':'file','multilang':True,'mandatory': True},
        'align':{'datatype':'string','type':'select','default':'NONE','options':['NONE', 'NONE', 'LEFT', 'LEFT', 'LEFT_FLOAT', 'LEFT_FLOAT', 'RIGHT', 'RIGHT', 'RIGHT_FLOAT', 'RIGHT_FLOAT']},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/zmsfile/manage_main',globals()) 


    """
    ############################################################################    
    #
    #   CONSTRUCTOR
    #
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ZMSFile.getLinkList: 
    #
    #  Returns ZMSFile as link-URL.
    #  @deprecated: use implementation that fits your own needs!
    # --------------------------------------------------------------------------
    def getLinkList(self,REQUEST, allow_none=0):
      print "[ZMSFile.getLinkList]: @deprecated: use implementation that fits your own needs!"
      rtn = []
      append = True
      append = append and self.isVisible(REQUEST)
      append = append and not self.isResource(REQUEST) # Object is not resource.
      if append:
        dct = {}
        dct['internal'] = 1
        dct['src'] = self
        dct['dst'] = self
        if self.getFile(REQUEST) is None:
          dct['url'] = ''
        else:
          dct['url'] = self.getFile(REQUEST).getHref(REQUEST)
        dct['title'] = self.getTitle(REQUEST)
        dct['description'] = _globals.nvl(self.getObjProperty('attr_dc_description',REQUEST),'')
        rtn.extend([dct])
      return rtn


    """
    ############################################################################    
    ###
    ###   Properties
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSFile.manage_changeProperties:
    #
    #  Change file properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE):
      """ ZMSFile.manage_changeProperties """
      
      self._checkWebDAVLock()
      message = ''
      messagekey = 'manage_tabs_message'
      t0 = time.time()
      
      redirect_self = False
      redirect_self = redirect_self or REQUEST.get('btn','') == '' 
      redirect_self = redirect_self and not REQUEST.get('btn','') in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]
      
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        try:
        
          ##### Object State ####
          self.setObjStateModified(REQUEST)
          
          ##### Properties ####
          # Metadata.
          self.setMetadata(lang,REQUEST)
          # Attributes.
          self.setReqProperty('active',REQUEST)
          self.setReqProperty('attr_active_start',REQUEST)
          self.setReqProperty('attr_active_end',REQUEST)
          self.setReqProperty('title',REQUEST)
          self.setReqProperty('titleshort',REQUEST)
          self.setReqProperty('align',REQUEST)
          # File.
          self.setReqProperty('file',REQUEST)
          file = self.getFile(REQUEST)
          if file is not None:
            if len(self.getObjProperty('title',REQUEST)) == 0:
              self.setObjProperty('title',getattr(file,'filename',''),lang)
            if len(self.getObjProperty('titleshort',REQUEST)) == 0:
              self.setObjProperty('titleshort',getattr(file,'filename',''),lang)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
          
          ##### Message ####
          message = self.getZMILangStr('MSG_CHANGED')
        
        except:
          tp, vl, tb = sys.exc_info()
          message = '<b>Error-Type:</b> '+str(tp)+'<br/><b>Error-Value:</b> '+str(vl)+'<br/>'
          messagekey = 'manage_tabs_error_message'
          _globals.writeException(self,"[manage_changeProperties]")
      
      
      # Return with message.
      if redirect_self:
        return RESPONSE.redirect('manage_main?lang=%s&%s=%s'%(lang,messagekey,urllib.quote(message)))
      else:
        self.checkIn(REQUEST)
        return RESPONSE.redirect('%s/manage_main?lang=%s&%s=%s#_%s'%(self.getParentNode().absolute_url(),lang,messagekey,urllib.quote(message),self.id))


    # --------------------------------------------------------------------------
    #   ZMSFile.isPageElement:
    # --------------------------------------------------------------------------
    def isPageElement(self): 
      return True

    # --------------------------------------------------------------------------
    #  ZMSFile.getTitle
    # --------------------------------------------------------------------------
    def getTitle(self,REQUEST): 
      return self.getObjProperty('title',REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSFile.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt(self,REQUEST): 
      return self.getObjProperty('titleshort',REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSFile.getFile
    # --------------------------------------------------------------------------
    def getFile(self,REQUEST): 
      return self.getObjProperty('file',REQUEST)


    """
    ############################################################################
    ###
    ###   HTML-Presentation
    ###
    ############################################################################
    """

    # preload display interface
    rendershort_default = HTMLFile('dtml/zmsfile/render_default', globals()) 
    rendershort_teaser = HTMLFile('dtml/zmsteaserelement/rendershort_default', globals())
    rendershort_print = HTMLFile('dtml/zmsfile/render_print', globals()) 

    # --------------------------------------------------------------------------
    #  ZMSFile._getBodyContent:
    #
    #  HTML presentation of File.
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      teaserCntnr = self.getParentNode()
      if teaserCntnr.meta_type == 'ZMSTeaserContainer':
        title = self.getTitlealt(REQUEST)
        if len(title) > 4 and title.startswith('__') and title.endswith('__'):
          url_title = title[2:-2]
          title = ''
        else:
          url_title = title
        has_title = len(title) > 0
        # Render file.
        file = self.getFile(REQUEST)
        url = ''
        target = ''
        target = '_blank'
        if file is not None:
          url = file.getHref(REQUEST)
          target = ' target="_blank"'
          if has_title:
            icon = '<img src="%s" title="%s (%s)" border="0" alt="Icon" align="absmiddle"/>'%(file.getMimeTypeIconSrc(),file.getContentType(),file.getDataSizeStr())
            title = '<a href="%s"%s>%s&nbsp;%s</a>'%( url, target, icon, title)
            title = '<div class="title">%s</div>'%title
        text = self.getObjProperty('attr_dc_description',REQUEST)
        bgcolor_title = REQUEST.get( 'bgcolor_title', teaserCntnr.getObjProperty( 'attr_bgcolor_title', REQUEST))
        bgcolor_text = REQUEST.get( 'bgcolor_text', teaserCntnr.getObjProperty( 'attr_bgcolor_text', REQUEST))
        return self.rendershort_teaser( self, url=url, url_title=url_title, target=target, title=title, text=text, bgcolor_title=bgcolor_title, bgcolor_text=bgcolor_text, REQUEST=REQUEST)
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
    #  ZMSFile.renderShort:
    #
    #  Renders short presentation of File.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      # Retrieve properties.
      file = self.getFile(REQUEST)
      url = None
      if file is not None:
        url = file.getHref(REQUEST)
      html = self.rendershort_default(self,url=url,REQUEST=REQUEST)
      # Process html <form>-tags.
      html = _globals.form_quote(html,REQUEST)
      # Return <html>.
      return html

    # --------------------------------------------------------------------------
    #  ZMSFile.printHtml:
    #
    #  Renders print presentation of a File.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      # Retrieve properties.
      file = self.getFile(REQUEST)
      url = None
      if file is not None:
        url = file.getHref(REQUEST)
      # Return <html>-presentation.
      return self.rendershort_print(self,url=url,REQUEST=REQUEST)


    """
    ############################################################################
    ###
    ###  ZMSTeaserElement
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSFile.getPenetrance
    # --------------------------------------------------------------------------
    def getPenetrance(self, REQUEST):
      penetrance = 0
      if 'attr_penetrance' in self.getObjAttrs().keys():
        penetrance = self.getObjProperty('attr_penetrance',REQUEST)
      return penetrance

################################################################################
