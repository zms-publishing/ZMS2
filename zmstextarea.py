################################################################################
# zmstextarea.py
#
# $Id: zmstextarea.py,v 1.6 2004/11/23 23:19:31 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.6 $
#
# Implementation of class ZMSTextarea (see below).
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
from Globals import HTML, HTMLFile
import sys
import time
import urllib
# Product Imports.
from zmsobject import ZMSObject
import _globals
import _metadata


################################################################################
################################################################################
###
###   Constructor(s)
###
################################################################################
################################################################################

manage_addZMSTextareaForm = HTMLFile('manage_addzmstextareaform', globals()) 
def manage_addZMSTextarea(self, lang, manage_lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSTextarea """
    
  if REQUEST['btn'] == self.getLangStr('BTN_INSERT',manage_lang):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSTextarea(self.getNewId(id_prefix),_sort_id+1)
    self._setObject( obj.id, obj)
    
    obj = getattr( self, obj.id)
    ##### Object State ####
    obj.setObjStateNew( REQUEST)
    ##### Init Coverage ####
    coverage = self.getDCCoverage( REQUEST)
    if coverage.find( 'local.')==0:
      obj.setObjProperty( 'attr_dc_coverage' ,coverage)
    else:
      obj.setObjProperty( 'attr_dc_coverage' ,'global.'+lang)
    ##### Init Properties ####
    obj.manage_changeProperties(lang,manage_lang,REQUEST,RESPONSE)
    ##### VersionManager ####
    obj.onChangeObj(REQUEST)
  
    ##### Normalize Sort-IDs ####
    self.normalizeSortIds( id_prefix)
  
    # Return with message.
    message = self.getLangStr('MSG_INSERTED',manage_lang)%obj.display_type(REQUEST)
    RESPONSE.redirect('%s/manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s#_%s'%(self.absolute_url(),lang,manage_lang,urllib.quote(message),obj.id))
                
  else:         
    RESPONSE.redirect('%s/manage_main?lang=%s&manage_lang=%s'%(self.absolute_url(),lang,manage_lang))


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSTextarea(ZMSObject, _metadata.Metadata):

    # Properties.
    # -----------
    meta_type = 'ZMSTextarea'
    icon = 'misc_/zms/zmstextarea.gif'
    icon_disabled = 'misc_/zms/zmstextarea_disabled.gif'

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
		'manage','manage_main','manage_workspace',
		'manage_changeProperties',
		'manage_moveObjUp','manage_moveObjDown',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
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
        'format':{'datatype':'string'},
        'text':{'datatype':'text','multilang':True,'type':'text','size':50},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries        
        '$metadict':{'datatype':'MetaDict'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/zmstextarea/manage_main', globals())
    epoz_toolbox = HTMLFile('dtml/zmstextarea/epoz_toolbox', globals())


    """
    ############################################################################    
    ###
    ###   Properties
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSTextarea.manage_changeProperties: 
    #
    #  Change Textarea properties.
    ############################################################################
    def manage_changeProperties(self, lang, manage_lang, REQUEST, RESPONSE): 
      """ ZMSTextarea.manage_changeProperties """
      
      self._checkWebDAVLock()
      message = ''
      messagekey = 'manage_tabs_message'
      t0 = time.time()
      
      target_ob = self.getParentNode()
      if REQUEST.get( 'btn', '') == '':
        target_ob = self
      target = REQUEST.get( 'target', '%s/manage_main'%target_ob.absolute_url())

      if REQUEST.get('btn','') not in  [ self.getLangStr('BTN_CANCEL',manage_lang), self.getLangStr('BTN_BACK',manage_lang)]:
        try:
        
          ##### Object State ####
          self.setObjStateModified(REQUEST)
          
          ##### Properties ####
          # Metadata.
          self.setMetadata(lang,manage_lang,REQUEST)
          # Attributes.
          for key in self.getObjAttrs().keys():
            self.setReqProperty(key,REQUEST)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
          
          ##### Message ####
          message = self.getLangStr('MSG_CHANGED',manage_lang)

        except:
          type, val, tb = sys.exc_info()
          message = '<b>Error-Type:</b> '+type+'<br/><b>Error-Value:</b> '+val+'<br/>'
          messagekey = 'manage_tabs_error_message'
          _globals.writeException(self,"[manage_changeProperties]")

        message = message + ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      
      # Return with message.
      self.checkIn(REQUEST)
      target = self.url_append_params( target, { 'lang': lang, 'manage_lang': manage_lang, 'preview': 'preview',  messagekey: message})
      target = '%s#_%s'%( target, self.id)
      return RESPONSE.redirect( target)


    # --------------------------------------------------------------------------
    #  ZMSTextarea.isPageElement
    # --------------------------------------------------------------------------
    def isPageElement(self):
      return True

    # --------------------------------------------------------------------------
    #  ZMSTextarea.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt(self,REQUEST): 
      return self.display_type(REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTextarea.getText
    # --------------------------------------------------------------------------
    def getText(self,REQUEST): 
      text = self.getObjProperty('text',REQUEST)
      # Number headlines
      levelnfc = self._getLevelnfc(REQUEST)
      if len(levelnfc) > 0:
        text = levelnfc + ' ' + text
      return text

    # --------------------------------------------------------------------------
    #  ZMSTextarea.getFormat
    # --------------------------------------------------------------------------
    def getFormat(self,REQUEST):
      format = self.getObjProperty('format',REQUEST)
      if format is None or len(format) == 0:
        format = self.getTextFormatDefault(REQUEST)
      return format


    """
    ############################################################################
    ###
    ###  Presentation 
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSTextarea.getLevelnfc
    # --------------------------------------------------------------------------
    def _getLevelnfc(self, REQUEST):
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      parent = self.getParentNode()
      reqBuffId = '_getLevelnfc'
      try:
        s = parent.fetchReqBuff( '%s_%s'%(reqBuffId,self.id), REQUEST, forced=True)
        return s
      except:
        s = ''
        textformat = self.getFormat(REQUEST)
        if textformat.find('headline') == 0:
          levelnfc = parent.getObjProperty('levelnfc',REQUEST)
          if len(levelnfc) > 0:
            parent_levelnfc = parent._getLevelnfc(REQUEST)
            sectionizer = _globals.MySectionizer()
            for sibling in parent.filteredChildNodes(REQUEST,['ZMSTextarea']):
              textformat = sibling.getFormat(REQUEST)
              if textformat.find('headline')==0:
                level = int(textformat[len(_globals.id_prefix(textformat)):])-1
                sectionizer.processLevel(level)
                parent.storeReqBuff( '%s_%s'%(reqBuffId,sibling.id), parent_levelnfc + str(sectionizer), REQUEST, forced=True)
                if self == sibling:
                  s = parent_levelnfc + str(sectionizer)
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return s

    # --------------------------------------------------------------------------
    #	ZMSTextarea._getBodyContent:
    #
    #	HTML presentation of Textarea. 
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      # Retrieve properties.
      text = self.getText(REQUEST)
      format = self.getFormat(REQUEST)
      textformat = self.getTextFormat( format, REQUEST)
      # Render HTML presentation.
      text = self.renderText( format, text, REQUEST, self.id)
      text = self.renderContentEditable( 'text', text, REQUEST)
      # Return body-content.
      return text

    # --------------------------------------------------------------------------
    #	ZMSTextarea.renderShort:
    #
    #	Renders short presentation of Textarea.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      return self._getBodyContent(REQUEST)

################################################################################
