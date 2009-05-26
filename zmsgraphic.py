################################################################################
# zmsgraphic.py
#
# $Id: zmsgraphic.py,v 1.7 2004/11/30 20:04:16 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.7 $
#
# Implementation of class ZMSGraphic (see below).
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
from Globals import HTMLFile
import sys
import time
import urllib
# Product Imports.
from zmstextarea import ZMSTextarea
import _fileutil
import _globals
import _metadata


################################################################################
################################################################################
###
###   Constructor(s)
###
################################################################################
################################################################################

manage_addZMSGraphicForm = HTMLFile('manage_addzmsgraphicform', globals()) 
def manage_addZMSGraphic(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSGraphic """
  
  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSGraphic(self.getNewId(id_prefix),_sort_id+1)
    self._setObject( obj.id, obj)
    
    obj = getattr( self, obj.id)
    ##### Object State ####
    obj.setObjStateNew( REQUEST)
    ##### Init Coverage ####
    coverage = self.getDCCoverage( REQUEST)
    if coverage.find( 'local.')==0:
      obj.setObjProperty( 'attr_dc_coverage', coverage)
    else:
      obj.setObjProperty( 'attr_dc_coverage', 'global.'+lang)
    ##### Init Properties ####
    obj.manage_changeProperties(lang,REQUEST,RESPONSE)
    ##### VersionManager ####
    obj.onChangeObj(REQUEST)
    
    ##### Normalize Sort-IDs ####
    self.normalizeSortIds( id_prefix)
    
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
class ZMSGraphic(ZMSTextarea):

    # Properties.
    # -----------
    meta_type = meta_id = 'ZMSGraphic'
    icon = 'misc_/zms/zmsgraphic.gif'
    icon_disabled = 'misc_/zms/zmsgraphic_disabled.gif'

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace','manage_checkout',
		'manage_moveObjUp','manage_moveObjDown',
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
        'format':{'datatype':'string'},
        'img':{'datatype':'image','multilang':True},
        'imghires':{'datatype':'image','multilang':True},
        'imgsuperres':{'datatype':'image','multilang':True},
        'text':{'datatype':'text','multilang':True,'type':'text','size':50},
        'align':{'datatype':'string','type':'select','default':'LEFT','options':['LEFT', 'LEFT', 'LEFT_FLOAT', 'LEFT_FLOAT', 'RIGHT', 'RIGHT', 'RIGHT_FLOAT', 'RIGHT_FLOAT', 'CENTER', 'CENTER']},
        'textalign':{'datatype':'string','type':'select','default':'LEFT','options':['LEFT','LEFT','RIGHT','RIGHT','CENTER','CENTER']},
        'displaytype':{'datatype':'int','default':2},
        'img_attrs_spec':{'datatype':'string','size':30,'default':'alt="" title=""'},
        'attr_url':{'datatype':'url','multilang':True},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }


    # Management Interface.
    # ---------------------
    manage_main = HTMLFile('dtml/zmsgraphic/manage_main', globals())


    """
    ############################################################################
    ###
    ###   Properties
    ###
    ############################################################################
    """

    ############################################################################
    #  ZMSGraphic.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE): 
      """ ZMSGraphic.manage_changeProperties """
      
      self._checkWebDAVLock()
      message = ''
      messagekey = 'manage_tabs_message'
      t0 = time.time()
      
      target_ob = self.getParentNode()
      if REQUEST.get( 'btn', '') == '':
        target_ob = self
      target = REQUEST.get( 'target', '%s/manage_main'%target_ob.absolute_url())
      
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        try:
          
           ##### Object State #####
          self.setObjStateModified(REQUEST)
          
          ##### Properties #####
          # Metadata.
          self.setMetadata(lang,REQUEST)
          # Attributes.
          self.setReqProperty('active',REQUEST)
          self.setReqProperty('attr_active_start',REQUEST)
          self.setReqProperty('attr_active_end',REQUEST)
          self.setReqProperty( 'text' ,REQUEST)
          self.setReqProperty( 'align' ,REQUEST)
          self.setReqProperty( 'textalign' ,REQUEST)
          self.setReqProperty( 'format' ,REQUEST)
          self.setReqProperty( 'img_attrs_spec' ,REQUEST)
          self.setReqProperty( 'displaytype' ,REQUEST)
          self.setReqProperty( 'img' ,REQUEST)
          self.setReqProperty( 'imghires' ,REQUEST)
          self.setReqProperty( 'imgsuperres' ,REQUEST)
          self.setReqProperty( 'attr_url' ,REQUEST)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
        
          ##### Message ####
          message = self.getZMILangStr('MSG_CHANGED')
        
        except:
          tp, vl, tb = sys.exc_info()
          message = '<b>Error-Type:</b> '+str(tp)+'<br/><b>Error-Value:</b> '+str(vl)+'<br/>'+str(tb)
          messagekey = 'manage_tabs_error_message'
          _globals.writeException(self,"[manage_changeProperties]")
      
      # Return with message.
      self.checkIn(REQUEST)
      target = self.url_append_params( target, { 'lang': lang, 'preview': 'preview', messagekey: message})
      target = '%s#_%s'%( target, self.id)
      return RESPONSE.redirect( target)


    # --------------------------------------------------------------------------
    #  ZMSGraphic.getImage
    # --------------------------------------------------------------------------
    def getImage(self,REQUEST): 
      return self.getObjProperty('img',REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSGraphic.getUrl
    # --------------------------------------------------------------------------
    def getUrl(self, REQUEST): 
      return self.getLinkUrl(self.getObjProperty('attr_url',REQUEST),REQUEST)


    """
    ############################################################################
    ###
    ###  Presentation 
    ###
    ############################################################################
    """

    ############################################################################
    #  ZMSGraphic.longdesc:
    #
    #  Change properties.
    ############################################################################
    def longdesc(self, REQUEST, RESPONSE): 
      """ ZMSGraphic.longdesc """
      l = []
      l.append('<html>\n')
      l.append('<body>\n')
      l.append(self.getObjProperty('attr_dc_description',REQUEST)+'\n')
      l.append('</body>\n')
      l.append('</html>\n')
      return ''.join(l)

    # --------------------------------------------------------------------------
    #  ZMSGraphic._getBodyContent:
    #
    #  HTML presentation of Graphic (and Caption).
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      # Retrieve properties.
      displaytype  = self.dctDisplaytype.get( str( self.getObjProperty( 'displaytype', REQUEST)), 'left')
      align        = self.getObjProperty('align',REQUEST)
      imgattr      = 'img'
      imghiresattr = 'imghires'
      imgalign     = ''
      imgurl       = self.getUrl(REQUEST)
      imgthumb     = _globals.isManagementInterface(REQUEST)
      imgspecial   = self.getObjProperty('img_attrs_spec',REQUEST)
      longdesc     = None
      if len(self.getObjProperty('attr_dc_description',REQUEST)) > 0:
        longdesc = 'longdesc?lang=%s'%REQUEST.get('lang',self.getPrimaryLanguage())
      imgclass     = 'img'
      text         = self.getRenderedText(REQUEST)
      textalign    = self.getObjProperty( 'textalign',REQUEST)
      textclass    = 'text'
      # Return body-content.
      bodyContent = self.renderDisplaytype( displaytype, imgattr, imghiresattr, imgurl, imgthumb, imgspecial, longdesc, imgclass, text, textalign, textclass, REQUEST)
      subclass = ''
      if align in [ 'LEFT', 'CENTER', 'RIGHT']:
        subclass = ' ' + align.lower()
      elif align in [ 'LEFT_FLOAT'] and displaytype in [ 'top', 'bottom']:
        subclass = ' floatleft'
      elif align in [ 'RIGHT_FLOAT'] and displaytype in [ 'top', 'bottom']:
        subclass = ' floatright'
      return '<div class="%s%s" id="%s">%s</div>'%( self.meta_type, subclass, self.id, bodyContent)

################################################################################
