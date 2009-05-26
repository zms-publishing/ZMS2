################################################################################
# zmsteaserelement.py
#
# $Id: zmsteaserelement.py,v 1.5 2004/11/23 23:04:51 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.5 $
#
# Implementation of class ZMSTeaserElement (see below).
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
import urllib
# Product Imports.
from zmsobject import ZMSObject
import _globals


################################################################################
################################################################################
###   
###   constructor ZMSTeaserElement
###   
################################################################################
################################################################################
def manage_addZMSTeaserElement(self, lang, _sort_id, REQUEST):
  """ manage_addZMSTeaserElement """
  
  ##### Create ####
  id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
  obj = ZMSTeaserElement(self.getNewId(id_prefix),_sort_id+1)
  self._setObject(obj.id, obj)
    
  obj = getattr(self,obj.id)
  ##### VersionManager ####
  obj.setObjStateNew(REQUEST)
  ##### Init Coverage ####
  coverage = self.getDCCoverage(REQUEST)
  if coverage.find('local.')==0:
    obj.setObjProperty('attr_dc_coverage',coverage)
  else:
    obj.setObjProperty('attr_dc_coverage','global.'+lang)
  ##### Init Properties ####
  obj.setObjProperty('active',1,lang)
  ##### VersionManager ####
  obj.onChangeObj(REQUEST)
            
  ##### Normalize Sort-IDs ####
  self.normalizeSortIds(id_prefix)
        
  # Return with message.
  if REQUEST.RESPONSE:
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    target = REQUEST.get( 'target', '%s/%s/manage_main'%( self.absolute_url(), obj.id))
    REQUEST.RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


################################################################################

lstPenetrance = [
  0,'this',
  1,'sub_nav',
  2,'sub_all'
]

################################################################################
################################################################################
###   
###   Class
###   
################################################################################
################################################################################
class ZMSTeaserElement(ZMSObject): 
        
    # Properties.
    # -----------
    meta_type = meta_id = "ZMSTeaserElement"
    icon = "misc_/zms/zmsteaser.gif"
    icon_disabled = "misc_/zms/zmsteaser_disabled.gif"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',    'action': 'manage_main'},
	{'label': 'TAB_HISTORY', 'action': 'manage_UndoVersionForm'},
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace','manage_checkout',
		'manage_changeProperties',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
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
        'title':{'datatype':'string','multilang':True,'size':40},
        'text':{'datatype':'text','multilang':True,'type':'text','size':50},
        'displaytype':{'datatype':'int','default':2},
        'attr_penetrance':{'datatype':'int','type':'select','options':lstPenetrance},
        'attr_url':{'datatype':'url','multilang':True},
        'attr_img':{'datatype':'image','multilang':True},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }


    # Management Interface.
    # ---------------------
    manage_form = HTMLFile('dtml/zmsteaserelement/manage_form',globals()) 
    manage_main = HTMLFile('dtml/zmsteaserelement/manage_main',globals()) 


    """
    ############################################################################
    ###
    ###   Properties
    ###
    ############################################################################
    """

    ############################################################################
    #  ZMSTeaserElement.manage_changeProperties: 
    #
    #  Change Teaser properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE): 
      """ ZMSTeaserElement.manage_changeProperties """

      target_ob = self.getParentNode()
      if REQUEST.get( 'btn', '') == '':
        target_ob = self
      target = REQUEST.get( 'target', '%s/manage_main'%target_ob.absolute_url())
      message = ''
      
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        
        ##### Object State #####
        self.setObjStateModified(REQUEST)
        
        ##### Properties #####
        # Metadata.
        self.setMetadata(lang,REQUEST)
        # Attributes.
        for key in self.getObjAttrs().keys():
          self.setReqProperty(key,REQUEST)
        
        ##### VersionManager ####
        self.onChangeObj(REQUEST)
        
        ##### Message #####
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      self.checkIn(REQUEST)
      target = self.url_append_params( target, { 'lang': lang, 'preview': 'preview', 'manage_tabs_message': message})
      target = '%s#_%s'%( target, self.id)
      return RESPONSE.redirect( target)


    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getPenetrance
    # --------------------------------------------------------------------------
    def getPenetrance(self, REQUEST): return self.getObjProperty('attr_penetrance',REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getTitle
    # --------------------------------------------------------------------------
    def getTitle(self, REQUEST): return self.getObjProperty('title',REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getAbstract
    # --------------------------------------------------------------------------
    def getAbstract(self, REQUEST): return self.search_quote(self.getText(REQUEST))

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getText
    # --------------------------------------------------------------------------
    def getText(self, REQUEST): 
      text = self.getObjProperty('text',REQUEST)
      # Process html <form>-tags.
      text = _globals.form_quote(text,REQUEST)
      # Return.
      return text

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getImg
    # --------------------------------------------------------------------------
    def getImg(self, REQUEST): 
      return self.getObjProperty('attr_img',REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getUrl
    # --------------------------------------------------------------------------
    def getUrl(self, REQUEST): 
      return self.getLinkUrl(self.getObjProperty('attr_url',REQUEST),REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getTitlealt:
    # --------------------------------------------------------------------------
    def getTitlealt(self,REQUEST): 
      return self.display_type(REQUEST)


    """
    ############################################################################
    ###
    ###   HTML-Presentation
    ###
    ############################################################################
    """

    # preload display interface
    rendershort_default = HTMLFile('dtml/zmsteaserelement/rendershort_default', globals())
    
    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.getBodyContent:
    #
    #  HTML presentation in BodyContent.
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      # Render title.
      title = self.getObjProperty('title', REQUEST)
      if len(title) > 4 and title.startswith('__') and title.endswith('__'):
        url_title = title[2:-2]
        title = ''
      else:
        url_title = title
      has_title = len(title) > 0
      displaytype  = self.dctDisplaytype.get( str( self.getObjProperty( 'displaytype', REQUEST)), 'left')
      imgattr = 'attr_img'
      imghiresattr = None
      url = _globals.nvl( self.getUrl( REQUEST), '')
      target = ''
      if url is not None and not url.find( REQUEST[ 'BASE0']) == 0:
        target = ' target="_blank"'
      imgthumb = True
      imgspecial = 'title="%s" alt="%s"'%(title,title)
      longdesc = ''
      imgclass = 'title'
      textalign = None
      textclass = 'title'
      if has_title or self.getImg( REQUEST) is not None:
        if has_title and url is not None and len( url) > 0: 
          title = '<a href="%s"%s>%s</a>'%( url, target, title)
        title = self.renderDisplaytype( displaytype, imgattr, imghiresattr, url, imgthumb, imgspecial, longdesc, imgclass, title, textalign, textclass, REQUEST)
      # Render text.
      text = self.getObjProperty('text', REQUEST)
      has_text = (len(text) > 0)
      teaserCntnr = self.getParentNode()
      bgcolor_title = REQUEST.get( 'bgcolor_title', teaserCntnr.getObjProperty( 'attr_bgcolor_title', REQUEST))
      bgcolor_text = REQUEST.get( 'bgcolor_text', teaserCntnr.getObjProperty( 'attr_bgcolor_text', REQUEST))
      if not (has_text or has_title):
        url = ''
      # Return <html>-presentation.
      return self.rendershort_default( self, url=url, url_title=url_title, target=target, title=title, text=text, bgcolor_title=bgcolor_title, bgcolor_text=bgcolor_text, REQUEST=REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTeaserElement.renderShort:
    #
    #  Renders short presentation of Teaser-Element.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      teaserCntnr = self.getParentNode()
      l = []
      l.append('<div id="teaser">')
      l.append('<div')
      l.append(' class="%s"'%teaserCntnr.meta_type)
      bgcolor_border = teaserCntnr.getObjProperty('attr_bgcolor_border',REQUEST)
      if bgcolor_border:
        l.append(' style="border: 1px solid %s;"'%self.get_colormap().get(bgcolor_border,'black'))
      l.append('>')
      l.append(self._getBodyContent(REQUEST))
      l.append('</div>')
      l.append('</div>')
      return ''.join(l)

################################################################################
