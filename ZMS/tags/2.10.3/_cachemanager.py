################################################################################
# _cachemanager.py
#
# $Id: _cachemanager.py,v 1.7 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.7 $
#
# Implementation of class CacheManager (see below).
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
import time
import urllib
# Product Imports.
import _globals 


dct_op = {'index':'','sitemap':'sitemap','index_print':'print'}


################################################################################
#
#   S T A T I C   C A C H E
#
################################################################################

# ------------------------------------------------------------------------------
# _getIdFromUrl
# ------------------------------------------------------------------------------
def _getIdFromUrl(REQUEST):
  id = REQUEST['URL']
  id = id[:-5]
  id = id[id.rfind('/')+1:]
  if id.find('_') < 0 and REQUEST.has_key('lang'):
    id = '%s_%s'%(id,REQUEST['lang'])
  return _getCacheId(id)


# ------------------------------------------------------------------------------
# _getCacheId
# ------------------------------------------------------------------------------
def _getCacheId(id):
  return 'cache_' + id + '_html'


# ------------------------------------------------------------------------------
# clearCachePage
# ------------------------------------------------------------------------------
def _clearCachePage(self, id):
  count = 0
  if not self.isPage():
    return _clearCachePage(self.getParentNode(),id)
  if id in self.objectIds():
    if _globals.debug( self): 
      _globals.writeLog( self, "[_clearCachePage]: Removing ID=%s"%id)
    self.manage_delObjects(ids=[id])
    count += 1
  return count


# ------------------------------------------------------------------------------
#  _refreshCachePage
# ------------------------------------------------------------------------------
def _refreshCachePage(self, id, REQUEST):
  if not self.isPage():
    return _refreshCachePage(self.getParentNode(),id,REQUEST)
  _clearCachePage(self,id)
  if _globals.debug( self): 
    _globals.writeLog( self, "[_refreshCachePage]: Generating ID=%s"%id)
  REQUEST.set('__cache__',1)
  title = '*** CACHE ***'
  raw = self.index_html(self,REQUEST)
  self.manage_addDTMLMethod(id,title,raw)
  self.setConfProperty('ZMS.cache.empty',0)


################################################################################
#
#   R E Q U E S T   B U F F E R
#
################################################################################

# ------------------------------------------------------------------------------
#  getReqBuffId:
#
#  Gets buffer-id in Http-Request.
#
#  @throws Exception
# ------------------------------------------------------------------------------
def getReqBuffId(self, key, REQUEST):
  id = '<%s at %s>_%s'%( self.meta_type, self.absolute_url(), key)
  lang = REQUEST.get( 'lang', None)
  if lang is not None:
    id = '%s_%s'%( id, lang)
  return id


# ------------------------------------------------------------------------------
#  getReqBuff:
#
#  Gets buffer from Http-Request.
#
#  @throws Exception
# ------------------------------------------------------------------------------
def getReqBuff(self, REQUEST):
  buff = REQUEST.get('__buff__',None)
  if buff == None:
    buff = _globals.MyClass()
  return buff


################################################################################
#
# ReqBuff
#
################################################################################
class ReqBuff:

    # --------------------------------------------------------------------------
    #  fetchReqBuff:
    #
    #  Fetch buffered value from Http-Request.
    #
    #  @throws Exception
    # --------------------------------------------------------------------------
    def fetchReqBuff(self, key, REQUEST, forced=False):
      if REQUEST.get('URL','/manage').find('/manage') < 0 or forced:
        buff = getReqBuff(self,REQUEST)
        reqBuffId = getReqBuffId(self,key,REQUEST)
        try:
          value = getattr(buff,reqBuffId)
          return value
        except:
          raise '%s not found in ReqBuff!'%reqBuffId
      raise 'ReqBuff is inactive!'
    
    # --------------------------------------------------------------------------
    #  storeReqBuff:
    #
    #  Returns value and stores it in buffer of Http-Request.
    # --------------------------------------------------------------------------
    def storeReqBuff(self, key, value, REQUEST, forced=False):
      try:
        if REQUEST.get('URL','/manage').find('/manage') < 0 or forced:
          buff = getReqBuff(self,REQUEST)
          reqBuffId = getReqBuffId(self,key,REQUEST)
          setattr(buff,reqBuffId,value)
          REQUEST.set('__buff__',buff)
      except:
        pass
      return value
    
    # --------------------------------------------------------------------------
    #  clearReqBuff:
    #
    #  Clears key from buffer of Http-Request.
    # --------------------------------------------------------------------------
    def clearReqBuff(self, key, REQUEST, forced=False):
      try:
        if REQUEST.get('URL','/manage').find('/manage') < 0 or forced:
          buff = getReqBuff(self,REQUEST)
          reqBuffId = getReqBuffId(self,key,REQUEST)
          delattr(buff,reqBuffId)
          REQUEST.set('__buff__',buff)
      except:
        pass
    
    
################################################################################
################################################################################
###
###   C l a s s   C a c h e a b l e O b j e c t :
###
################################################################################
################################################################################
class CacheableObject(ReqBuff):

    # --------------------------------------------------------------------------
    # CacheableObject.clearCachePage: 
    # --------------------------------------------------------------------------
    def clearCachePage(self):
      count = 0
      for s_lang in self.getLangIds():
        for s_op in dct_op.keys():
          id = _getCacheId('%s_%s'%(s_op,s_lang))
          count += _clearCachePage(self,id)
      return count


    # --------------------------------------------------------------------------
    # CacheableObject.clearCachePages: 
    # --------------------------------------------------------------------------
    def clearCachePages(self, max_depth=999, cur_depth=0):
      count = 0
      if self.isPage() and self.meta_type != 'ZMSSysFolder':
        count += self.clearCachePage()
        if cur_depth < max_depth:
          for ob in self.getChildNodes():
            count += ob.clearCachePages( max_depth, cur_depth+1)
      return count


    # --------------------------------------------------------------------------
    # CacheableObject.clearCache: 
    # --------------------------------------------------------------------------
    def clearCache(self):
      if self.isPage() and self.meta_type != 'ZMSSysFolder':
        self.clearCachePages()
        self.setConfProperty('ZMS.cache.cleared.time',time.time())
        self.setConfProperty('ZMS.cache.empty',1)


    # --------------------------------------------------------------------------
    # CacheableObject.synchronizeCachePage: 
    # --------------------------------------------------------------------------
    def synchronizeCachePage(self, REQUEST):
    
      # PAGES.
      # ------
      if self.getConfProperty('ZMS.cache.active')==1:
        s_lang = REQUEST.get('lang',self.getPrimaryLanguage())
        if self.isPageElement():
          _clearCachePage(self,_getCacheId('index_%s'%s_lang))
          _clearCachePage(self,_getCacheId('index_print_%s'%s_lang))
        elif self.isPage():
          if self.getConfProperty('ZMS.cache.synchronize.onpagechange')==1:
            self.synchronizeCache()
          else:
            _clearCachePage(self,_getCacheId('index_%s'%s_lang))
            _clearCachePage(self,_getCacheId('index_print_%s'%s_lang))
            _clearCachePage(self,_getCacheId('sitemap_%s'%s_lang))
        elif self.isMetaType(['ZMSTeaserContainer','ZMSTeaserElement'],REQUEST):
          self.getParentNode().synchronizeCachePage(REQUEST)


    # --------------------------------------------------------------------------
    # CacheableObject.isCachedPage:
    # --------------------------------------------------------------------------
    def isCachedPage(self, REQUEST):
      if not self.isPage():
        parent = self.getParentNode()
        if parent is not None and isinstance( parent, CacheableObject):
          return parent.isCachedPage(REQUEST)
      id = _getIdFromUrl(REQUEST)
      found = False
      for s_lang in self.getLangIds():
        for s_op in dct_op.keys():
          if id == _getCacheId('%s_%s'%(s_op,s_lang)):
            found = True
      rtn = True
      rtn = rtn and found
      rtn = rtn and ('attr_cacheable' not in self.getObjAttrs().keys() or self.getObjProperty('attr_cacheable',REQUEST) in [ 1, True])
      rtn = rtn and self.getConfProperty('ZMS.cache.active')==1
      rtn = rtn and not _globals.isPreviewRequest(REQUEST)
      rtn = rtn and not _globals.isCacheRequest(REQUEST)
      try: rtn = rtn and not len(filter( lambda x: x != '-C', REQUEST.form.keys())) > 0
      except: pass
      return rtn


    # --------------------------------------------------------------------------
    # CacheableObject.getCachedPages:
    # --------------------------------------------------------------------------
    def getCachedPages(self, REQUEST, max_depth=999, cur_depth=0):
      count = 0
      if self.isPage() and self.meta_type != 'ZMSSysFolder':
        self.getCachedPage( REQUEST)
        count += 1
        if cur_depth < max_depth:
          for ob in self.filteredChildNodes( REQUEST, self.PAGES):
            count += ob.getCachedPages( REQUEST, max_depth, cur_depth+1)
      return count


    # --------------------------------------------------------------------------
    # CacheableObject.getCachedPage:
    # --------------------------------------------------------------------------
    def getCachedPage(self, REQUEST):
      if not self.isPage():
        return self.getParentNode().getCachedPage(REQUEST)
      id = _getIdFromUrl(REQUEST)
      # Clear cache at least daily.
      if self.getConfProperty('ZMS.cache.synchronize.onpagechange')==1:
        t0 = self.getConfProperty('ZMS.cache.cleared.time',time.time())
        t1 = time.time()
        if _globals.compareDate(t0,t1,accuracy_time=0)==1:
          self.clearCache()
      # Refresh cache.
      if not id in self.objectIds(['DTML Method']):
        _refreshCachePage(self,id,REQUEST)
      # Return cache.
      for ob in self.objectValues(['DTML Method']):
        if ob.id() == id:
	  return ob.raw


    ############################################################################
    #  CacheableObject.manage_getCachedPages:
    #
    #  Get cached pages.
    ############################################################################
    def manage_getCachedPages(self, lang, manage_lang, REQUEST, RESPONSE): 
      """ CacheableObject.manage_getCachedPages """

      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      max_depth = REQUEST.get('attr_cacheable_levels',999)
      
      ##### Clear cached pages ####
      count = self.clearCachePages( max_depth)
      message += self.getLangStr('MSG_DELETED',manage_lang)%count

      ##### Get cached pages ####
      REQUEST.set( 'URL', REQUEST['URL1'] + '/index_%s.html'%lang)
      count = self.getCachedPages( REQUEST, max_depth)
      message += '<br/>' + self.getLangStr('MSG_INSERTED',manage_lang)%(str(count)+' '+self.getLangStr('ATTR_OBJECTS',manage_lang))
      
      # Return with message.
      message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      target = REQUEST.get('target','manage_properties')
      return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_lang=%s&manage_tabs_message=%s'%(target,lang,manage_lang,urllib.quote(message)))


    ############################################################################
    #  CacheableObject.manage_clearCachePages:
    #
    #  Clear cached pages.
    ############################################################################
    def manage_clearCachePages(self, lang, manage_lang, REQUEST, RESPONSE): 
      """ CacheableObject.manage_clearCachePages """

      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      max_depth = REQUEST.get('attr_cacheable_levels',999)
      
      ##### Clear cached pages ####
      count = self.clearCachePages( max_depth)
      message += self.getLangStr('MSG_DELETED',manage_lang)%count

      # Return with message.
      message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      target = REQUEST.get('target','manage_properties')
      return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_lang=%s&manage_tabs_message=%s'%(target,lang,manage_lang,urllib.quote(message)))
      


################################################################################
################################################################################
###
###   C l a s s   C a c h e M a n a g e r :
###
################################################################################
################################################################################
class CacheManager(CacheableObject): 

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
                'manage_changeCacheProperties',
                )
    __ac_permissions__=(
                ('ZMS Administrator', __administratorPermissions__),
                )


    # --------------------------------------------------------------------------
    # CacheManager.synchronizeCache: 
    #	IN:   forced_update	0= not forced (update once a day), 
    #				1= forced (call from management-interface).
    # --------------------------------------------------------------------------
    def synchronizeCache(self, forced_update=0):
      if self.getConfProperty('ZMS.cache.empty',0)==0 or forced_update:
        self.clearCache()


    ############################################################################
    #  CacheManager.manage_changeCacheProperties:
    #
    #  Change cache properties.
    ############################################################################
    def manage_changeCacheProperties(self, btn, lang, manage_lang, REQUEST): 
      """ CacheManager.manage_changeCacheProperties """

      cache_before = self.getConfProperty('ZMS.cache.active')
        
      # Change.
      # -------
      self.setConfProperty('ZMS.cache.active',REQUEST.has_key('cache_active'))
        
      # Clear.
      # ------
      cache_after = self.getConfProperty('ZMS.cache.active')
      if (cache_before != cache_after and cache_before) or \
         (btn == 'Clear'):
        self.synchronizeCache(forced_update=1)
            
      # Return with message.
      message = urllib.quote(self.getLangStr('MSG_CHANGED',manage_lang))
      return REQUEST.RESPONSE.redirect('manage_customize?lang=%s&manage_lang=%s&manage_tabs_message=%s#_cache'%(lang,manage_lang,message))

################################################################################
