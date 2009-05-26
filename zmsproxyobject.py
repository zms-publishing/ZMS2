################################################################################
# zmsproxyobject.py
#
# $Id: zmsproxyobject.py,v 1.7 2004/11/23 23:04:47 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.7 $
#
# Implementation of class ZMSProxyObject (see below).
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
from types import StringTypes
# Product Imports.
from zmsobject import ZMSObject
from zmscontainerobject import ZMSContainerObject


################################################################################
################################################################################
###   
###   C l a s s
###   
################################################################################
################################################################################

class ZMSProxyObject(ZMSContainerObject):


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.__init__: 
    # --------------------------------------------------------------------------
    def __init__(self, root, base, url_base, id, proxy, recursive=False):
      """ Constructor """
      self.__root__ = root
      self.base = base
      self.url_base = url_base
      self.meta_type = proxy.meta_type
      if self.meta_type == 'ZMSCustom':
        self.meta_id = proxy.meta_id
      self.dGlobalAttrs = proxy.dGlobalAttrs
      self.REQUEST = proxy.REQUEST
      self.id = id
      self.proxy = proxy
      self.recursive = recursive


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.__proxy__:
    # --------------------------------------------------------------------------
    def __proxy__(self):
      return self


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getProxy
    # --------------------------------------------------------------------------
    def getProxy(self):
      return self


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.__request__ 
    # --------------------------------------------------------------------------
    def __request__(self, REQUEST):
      proxy = self.proxy
      if type( REQUEST) in StringTypes:
        return proxy.REQUEST
      return REQUEST


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.absolute_url
    # --------------------------------------------------------------------------
    def absolute_url(self):
      url_base = self.url_base
      rtn = url_base
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getMetaobjIds:
    # --------------------------------------------------------------------------
    def getMetaobjIds(self, sort=1):
      proxy = self.proxy
      rtn = proxy.getMetaobjIds( sort)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getMetaobjAttrIds:
    # --------------------------------------------------------------------------
    def getMetaobjAttrIds(self, meta_id):
      proxy = self.proxy
      rtn = proxy.getMetaobjAttrIds( meta_id)
      return rtn


    # --------------------------------------------------------------------------
    #  MetaobjManager.getMetaobjAttr:
    # --------------------------------------------------------------------------
    def getMetaobjAttr(self, meta_id, key):
      proxy = self.proxy
      rtn = proxy.getMetaobjAttr( meta_id, key)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getConfProperty
    # --------------------------------------------------------------------------
    def getConfProperty(self, key, default=None):
      proxy = self.proxy
      rtn = proxy.getConfProperty( key, default)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getObjAttrs
    # --------------------------------------------------------------------------
    def getObjAttrs(self, meta_type=None):
      proxy = self.proxy
      rtn = proxy.getObjAttrs( meta_type)
      return rtn
      
      
    # --------------------------------------------------------------------------
    #  ZMSProxyObject._getObjAttrValue
    # --------------------------------------------------------------------------
    def _getObjAttrValue(self, obj_attr, obj_vers, lang):
      proxy = self.proxy
      rtn = proxy._getObjAttrValue( obj_attr, obj_vers, lang)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getObjAttrValue
    # --------------------------------------------------------------------------
    def getObjAttrValue(self, obj_attr, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getObjAttrValue( obj_attr, req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getDocumentElement
    # --------------------------------------------------------------------------
    def getDocumentElement(self):
      base = self.base
      rtn = base.getDocumentElement( )
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getHome
    # --------------------------------------------------------------------------
    def getHome(self):
      base = self.base
      rtn = base.getHome( )
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getDCCoverage
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}):
      proxy = self.proxy
      rtn = proxy.getDCCoverage( REQUEST)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getDCType
    # --------------------------------------------------------------------------
    def getDCType(self, REQUEST):
      proxy = self.proxy
      rtn = proxy.getDCType( REQUEST)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getDCDescription
    # --------------------------------------------------------------------------
    def getDCDescription(self, REQUEST):
      proxy = self.proxy
      rtn = proxy.getDCDescription( REQUEST)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getUserAttr:
    #
    #  Overrides AccessManager.getUserAttr.
    # --------------------------------------------------------------------------
    def getUserAttr(self, user, name, default, flag=0):
      proxy = self.proxy
      rtn = proxy.getUserAttr( user, name, default, flag)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getPageExt
    # --------------------------------------------------------------------------
    def getPageExt(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getPageExt( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getTitle
    # --------------------------------------------------------------------------
    def getTitle(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getTitle( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getTitlealt:
    # --------------------------------------------------------------------------
    def getTitlealt(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getTitlealt( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getPenetrance:
    # --------------------------------------------------------------------------
    def getPenetrance(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getPenetrance( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getTeaserElements:
    # --------------------------------------------------------------------------
    def getTeaserElements(self, REQUEST, current=None):
      rtn = []
      recursive = self.recursive
      if recursive:
        proxy = self.proxy
        req = self.__request__( REQUEST)
        if hasattr( proxy, 'getTeaserElementsPROXY'):
          rtn = proxy.getTeaserElementsPROXY( proxy, req, current)
        else:
          rtn = proxy.getTeaserElements( req, current)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getChildNodes:
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST={}, meta_types=None):
      rtn = []
      recursive = self.recursive
      if recursive:
        proxy = self.proxy
        req = self.__request__( REQUEST)
        if hasattr( proxy, 'getChildNodesPROXY'):
          rtn = map( lambda x: ZMSProxyObject( self.__root__, self, self.absolute_url()+'/'+x.id, x.id, x, recursive), proxy.getChildNodesPROXY( proxy, req, meta_types))
        else:
          rtn = map( lambda x: ZMSProxyObject( self.__root__, self, self.absolute_url()+'/'+x.id, x.id, x, recursive), proxy.getChildNodes( req, meta_types))
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getLevelnfc
    # --------------------------------------------------------------------------
    def getLevelnfc(self, REQUEST):
      proxy = self.proxy
      rtn = proxy.getLevelnfc( REQUEST)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getLevel
    # --------------------------------------------------------------------------
    def getLevel(self):
      proxy = self.proxy
      base = self.base
      rtn = base.getLevel( ) + 1
      recursive = self.recursive
      if proxy is not None and proxy is ZMSProxyObject:
        if hasattr( proxy, 'getLevelPROXY'):
          rtn = proxy.getLevelPROXY( proxy)
        else:
          rtn = proxy.getLevel()
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getObjProperty
    # --------------------------------------------------------------------------
    def getObjProperty(self, key, REQUEST={}, default=None):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      if hasattr( proxy, 'getObjPropertyPROXY'):
        rtn = proxy.getObjPropertyPROXY( proxy, key, req, default)
      else:
        rtn = proxy.getObjProperty( key, req, default)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getParentNode
    # --------------------------------------------------------------------------
    getParentNode__roles__ = None
    def getParentNode(self):
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      rtn = self.base
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getType
    # --------------------------------------------------------------------------
    def getType(self):
      proxy = self.proxy
      if proxy.meta_type == 'ZMSCustom':
        rtn = proxy.getType( )
      else:
        rtn = None
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.isActive
    # --------------------------------------------------------------------------
    def isActive(self, REQUEST):
      proxy = self.proxy
      rtn = proxy.isActive( REQUEST)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.isMetaType:
    # --------------------------------------------------------------------------
    def isMetaType(self, meta_type, REQUEST={'preview':'preview'}):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.isMetaType( meta_type, req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.isResource:
    # --------------------------------------------------------------------------
    def isResource(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.isResource( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.isPage:
    # --------------------------------------------------------------------------
    def isPage(self):
      proxy = self.proxy
      rtn = proxy.isPage( )
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.isPageElement:
    # --------------------------------------------------------------------------
    def isPageElement(self):
      proxy = self.proxy
      rtn = proxy.isPageElement( )
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.isVisible:
    # --------------------------------------------------------------------------
    def isVisible(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.isVisible( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject._getBodyContent:
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy._getBodyContent( req)
      return rtn
    
    
    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getBodyContent:
    # --------------------------------------------------------------------------
    def getBodyContent(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getBodyContent( req)
      return rtn

    
    # --------------------------------------------------------------------------
    #  ZMSProxyObject.display_icon:
    # --------------------------------------------------------------------------
    def display_icon(self, REQUEST, meta_type=''): 
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.display_icon( req, meta_type)
      return rtn
    
    
    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getLangIds:
    # --------------------------------------------------------------------------
    def getLangIds(self, sort=1):
      proxy = self.proxy
      rtn = proxy.getLangIds( sort)
      return rtn


    # --------------------------------------------------------------------------
    #	ZMSProxyObject.get_manage_lang:
    # --------------------------------------------------------------------------
    def get_manage_lang(self):
      proxy = self.proxy
      rtn = proxy.get_manage_lang( )
      return rtn


    # --------------------------------------------------------------------------
    #	ZMSProxyObject.getZMILangStr:
    # --------------------------------------------------------------------------
    def getZMILangStr(self, key):
      proxy = self.proxy
      rtn = proxy.getZMILangStr( key)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getLangStr:
    # --------------------------------------------------------------------------
    def getLangStr(self, key, lang=None):
      proxy = self.proxy
      rtn = proxy.getLangStr( key, lang)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getMetadictAttrs:
    # --------------------------------------------------------------------------
    def getMetadictAttrs(self, meta_type=None):
      proxy = self.proxy
      rtn = proxy.getMetadictAttrs( meta_type)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getMetadictAttr:
    # --------------------------------------------------------------------------
    def getMetadictAttr(self, key):
      proxy = self.proxy
      rtn = proxy.getMetadictAttr( key)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getPrimaryLanguage:
    # --------------------------------------------------------------------------
    def getPrimaryLanguage(self):
      proxy = self.proxy
      rtn = proxy.getPrimaryLanguage()
      return rtn
    

    # --------------------------------------------------------------------------
    #  ZMSProxyObject.hasAccess:
    # --------------------------------------------------------------------------
    def hasAccess(self, REQUEST):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.hasAccess( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getObjVersion:
    # --------------------------------------------------------------------------
    def getObjVersion(self, REQUEST={}):
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getObjVersion( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.breadcrumbs_obj_path:
    # --------------------------------------------------------------------------
    def breadcrumbs_obj_path(self):
      proxy = self.proxy
      base = self.base
      rtn = base.breadcrumbs_obj_path( ) + [ self]
      recursive = self.recursive
      if proxy is not None and proxy is ZMSProxyObject:
        if hasattr( proxy, 'breadcrumbs_obj_pathPROXY'):
          rtn = proxy.breadcrumbs_obj_pathPROXY( proxy)
        else:
          rtn = proxy.breadcrumbs_obj_path()
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getDeclUrl:
    # --------------------------------------------------------------------------
    def getDeclUrl(self, REQUEST={}):
      if self.getConfProperty('ZMS.pathhandler',0) == 0:
        rtn = self.absolute_url()
      else:
        base = self.base
        req = self.__request__( REQUEST)
        rtn = base.getDeclUrl( req)
        rtn += '/' + self.getDeclId( req)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.getHref2IndexHtml:
    # --------------------------------------------------------------------------
    def getHref2IndexHtml(self, REQUEST, deep=1): 
      proxy = self.proxy
      rtn = ZMSObject.getHref2IndexHtml( self, REQUEST, deep)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSProxyObject.printHtml:
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      proxy = self.proxy
      rtn = proxy.printHtml( level, sectionizer, REQUEST, deep)
      return rtn

################################################################################
