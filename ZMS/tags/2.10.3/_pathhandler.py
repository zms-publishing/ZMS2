################################################################################
# _pathhandler.py
#
# $Id: _pathhandler.py,v 1.6 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.6 $
#
# Implementation of class PathHandler (see below).
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
from OFS.CopySupport import absattr
import copy
# Product Imports.
import _blobfields
import _globals


# ------------------------------------------------------------------------------
#  _pathhandler.validateId:
#
#  Validates id against list of possible declarative id.
# ------------------------------------------------------------------------------
def validateId(self, id, REQUEST):
  if id == self.id:
    return True
  if self.getConfProperty( 'ZMS.pathhandler', 0) != 0:
    lang = REQUEST.get( 'lang')
    if lang is None:
      langs = []
      for lang in self.getLanguages():
        req={ 'lang': lang, 'preview': REQUEST.get('preview','')}
        if id == self.getDeclId( req):
          langs.append( lang)
      if len( langs) == 1:
        REQUEST.set( 'lang', langs[0])
      return len( langs) > 0
    else:
      return id == self.getDeclId( REQUEST)
  return False


# ------------------------------------------------------------------------------
#  _pathhandler.handleBlobAttrs:
#
#  If the object has blob-fields find by filename and display data.
# ------------------------------------------------------------------------------
def handleBlobAttrs(self, name, REQUEST):
  if _globals.debug( self):
    _globals.writeLog( self, '[__bobo_traverse__]: If the object has blob-fields find by filename and display data.')
  for key in self.getObjAttrs().keys():
    obj_attr = self.getObjAttr(key)
    datatype = obj_attr['datatype_key']
    if datatype in _globals.DT_BLOBS:
      lang = self.getLanguageFromName( REQUEST['URL'])
      REQUEST.set( 'lang', lang)
      value = self.getObjProperty( key, REQUEST)
      if value is not None:
        href = value.getHref( REQUEST)
        langfilename = href.split( '/')[ -1]
        if langfilename.find( '?') > 0:
          langfilename = langfilename[ :langfilename.find( '?')]
        if langfilename == name:
          return value
  return None



################################################################################
################################################################################
###
###   class PathHandler:
###
###   Based on the Zope-Product PathHandler
###   http://www.zope.org/Members/NIP/PathHandler).
###
################################################################################
################################################################################
class PathHandler: 

    # --------------------------------------------------------------------------
    #  PathHandler.base_url
    # --------------------------------------------------------------------------
    def base_url(self):
      rtn = None
      try:
        if  self.getConfProperty( 'ZMS.pathcoherence', 1) == 1:
          rtn = self.REQUEST.get('BASE0') + ''.join( map( lambda x: '/'+x, list( self.getVirtualRootPhysicalPath( self, True))))
      except:
        pass
      if rtn is None:
        rtn = self.absolute_url()
      return rtn


    # --------------------------------------------------------------------------
    #  PathHandler.getVirtualRootPhysicalPath
    # --------------------------------------------------------------------------
    def getVirtualRootPhysicalPath(self, ob, url_base=False):
      l = []
      dump = False
      try:
        while True:
          ob_id = absattr( ob.id)
          if len( ob_id) > 0:
            if ob_id in l:
              if dump: print "l=l[",l.index( ob_id),":]=",l[ l.index( ob_id):]   
              l = l[ l.index( ob_id):]
            else:
              if dump: print "l=",ob_id,"+",l   
              l.insert( 0, ob_id)
          if url_base and hasattr( ob, 'url_base') and str( ob).find( 'ZMSProxyObject') > 0:
            if ob_id in l:
              if dump: print "l=l[",l.index( ob_id),":]=",l[ l.index( ob_id):]   
              l = l[ l.index( ob_id):]
            ids = ob.url_base[ len(self.REQUEST.get( 'BASE0')) + 1:].split( '/')
            if dump: print "ids=",ids
            ids.reverse()
            for id in ids:
              if id not in l:
                if dump: print "l=",id,"+",l   
                l.insert( 0, id)
            break
          ob = ob.aq_parent
      except:
        pass
      return tuple( l)


    # --------------------------------------------------------------------------
    #  PathHandler.__bobo_traverse__
    # --------------------------------------------------------------------------
    def __bobo_traverse__(self, TraversalRequest, name):
      # If this is the first time this __bob_traverse__ method has been called
      # in handling this traversal request, store the path_to_handle
      req = self.REQUEST
      
      if not TraversalRequest.has_key('path_to_handle'):
      
          # Make a reversed copy of the TraversalRequestNameStack
          TraversalRequestNameStackReversed=copy.copy(TraversalRequest['TraversalRequestNameStack'])
          TraversalRequestNameStackReversed.reverse()
          
          # Set path_to_handle in the TraversalRequest.
          TraversalRequest['path_to_handle']=[name]+TraversalRequestNameStackReversed
          
          # Set path_to_handle for VirtualHosts.
          if '/' in TraversalRequest[ 'path_to_handle']:
            VirtualRootPhysicalPath = self.REQUEST.get( 'VirtualRootPhysicalPath', self.getVirtualRootPhysicalPath( self.getDocumentElement()))
            if len( VirtualRootPhysicalPath) > 1:
              b = TraversalRequest[ 'path_to_handle'].index( '/')
              TraversalRequest[ 'path_to_handle'] = TraversalRequest[ 'path_to_handle'][ b+1:]
              for i in range( 1, len( VirtualRootPhysicalPath)):
                TraversalRequest[ 'path_to_handle'].insert( i-1, VirtualRootPhysicalPath[ i])

      # Set language.
      lang = self.REQUEST.get( 'lang')
      if lang is None:
        lang = self.getLanguageFromName( TraversalRequest['path_to_handle'][-1])
      if lang is not None:
        self.REQUEST.set( 'lang', lang)
     
      # If the name is in the list of attributes, call it.
      ob = getattr( self, name, None)
      if ob is None:
        obs = self.objectValues( self.dGlobalAttrs.keys())
        filtered_obs = filter( lambda x: validateId( x, name, req), obs)
        if len( filtered_obs) == 1:
          ob = filtered_obs[0]
      if ob is not None:
        if getattr(ob,'meta_type',None) in self.dGlobalAttrs.keys():
          if self.REQUEST.get('URL','').find('/manage') < 0 and \
             TraversalRequest['path_to_handle'][-1] == name:
            ob = _globals.getPageWithElements( ob, req)

        # Set language.
        if self.REQUEST.get('URL','').find('/manage') < 0 and \
           TraversalRequest['path_to_handle'][-1] == name:
          lang = self.REQUEST.get( 'lang')
          if lang is None:
            lang = self.getHttpAcceptLanguage( self.REQUEST)
          if lang is not None:
            self.REQUEST.set( 'lang', lang)

        return ob
      
      # otherwise do some 'magic'
      else:
        if _globals.debug( self):
          _globals.writeLog( self, '[__bobo_traverse__]: otherwise do some magic')

        if req.get( 'URL', '').find( '/manage') < 0 or \
           req.get( 'ZMS_PATH_HANDLER', False):

          thisOb = self
          obs = self.objectValues( self.dGlobalAttrs.keys())
          filtered_obs = filter( lambda x: ( x.id == name or x.getDeclId( req) == name) and x.isPage(), obs)
          if len( filtered_obs) == 1:
            thisOb = filtered_obs[0]

          # Recursive inclusions.
          if thisOb.meta_type == 'ZMSLinkElement':
            recursive = thisOb.isEmbeddedRecursive( req)
            if recursive:
              ob = thisOb.getRefObj()
              proxy = thisOb.initProxy( thisOb.aq_parent, thisOb.absolute_url(), ob, recursive)
              c = 0
              l = TraversalRequest[ 'path_to_handle']
              if thisOb.id in l:
                i = l.index( thisOb.id) + 1
              elif thisOb.getDeclId( req) in l:
                i = l.index( thisOb.getDeclId( req)) + 1
              for k in range( i, len(l)):
                newOb = None
                obs = ob.getChildNodes( req)
                filtered_obs = filter( lambda x: ( x.id == l[k] or x.getDeclId( req) == l[k]), obs)
                if len( filtered_obs) == 1:
                  newOb = filtered_obs[0]
                try:
                  if newOb.meta_type not in self.dGlobalAttrs.keys():
                    newOb = None
                except:
                  pass
                if newOb is None:
                  break
                ob = newOb
                proxy = thisOb.initProxy( proxy, proxy.absolute_url()+'/'+ob.id, ob, recursive)
                c += 1
              if c > 0:
                req.set( 'ZMS_PROXY_%s'%self.id, proxy)
            if req.get( 'ZMS_PROXY_%s'%self.id) and req.get( 'ZMS_PROXY_%s'%self.id).id != TraversalRequest[ 'path_to_handle'][-1]:
              v = handleBlobAttrs( req.get( 'ZMS_PROXY_%s'%self.id).proxy, TraversalRequest[ 'path_to_handle'][-1], req)
              if v is not None: 
                return v
            return thisOb

        # Declarative Urls.
        lang = self.getPrimaryLanguage()
        index = TraversalRequest['path_to_handle'][-1]
        i = index.rfind('_')
        j = index.rfind('.')
        if i > 0 and i < j:
          lang = index[i+1:j]
          if lang in self.getLangIds():
            self.REQUEST.set('lang',lang)
        ob = self.pathob([name],self.REQUEST)
        if ob is not None:
          if getattr(ob,'meta_type',None) in self.dGlobalAttrs.keys():
            if self.REQUEST.get('URL','').find('/manage') < 0 and name == TraversalRequest['path_to_handle'][-1]:
              ob = _globals.getPageWithElements( ob, self.REQUEST)
          return ob
        
        # If the object is record-set and has blob-fields find by filename and 
        # display data.
        if name.find( '@') == 0:
          if self.meta_type == 'ZMSCustom' and \
             self.getType()=='ZMSRecordSet':
            try:
              i = int( name[1:])
              r = self.getObjProperty( self.getMetaobj( self.meta_id)['attrs'][0]['id'], self.REQUEST)
              d = r[i]
              for key in d.keys():
                value = d[key]
                if isinstance(value,_blobfields.MyImage) or isinstance(value,_blobfields.MyFile):
                  value = value._getCopy()
                  value.aq_parent = self
                  value.key = key
                  value.lang = req.get('lang', self.getPrimaryLanguage())
                  langfilename = value.getHref( req).split( '/')[ -1]
                  if langfilename.find( '?') > 0:
                    langfilename = langfilename[ :langfilename.find( '?')]
                  if langfilename == TraversalRequest['path_to_handle'][-1]:
                    return value
            except:
              _globals.writeException( self)
          else:
            try:
              i = int( name[1:])
              obj_attrs = self.getObjAttrs()
              for key in self.getObjAttrs().keys():
                obj_attr = obj_attrs[ key]
                if obj_attr['datatype_key'] == _globals.DT_LIST and \
                   obj_attr['repetitive']:
                  r = self.getObjProperty( key, self.REQUEST)
                  value = r[i]
                  value = value._getCopy()
                  value.aq_parent = self
                  value.key = key
                  value.lang = req.get('lang', self.getPrimaryLanguage())
                  langfilename = value.getHref( req).split( '/')[ -1]
                  if langfilename.find( '?') > 0:
                    langfilename = langfilename[ :langfilename.find( '?')]
                  if langfilename == TraversalRequest['path_to_handle'][-1]:
                    return value
            except:
              _globals.writeException( self)
                
        
        # If the object has resource-fields of special-object find by filename 
        # and display data.
        if self.meta_type == 'ZMSCustom':
          for key in self.getMetaobjAttrIds( self.meta_id):
             metaObjAttr = self.getMetaobjAttr( self.meta_id, key)
             if metaObjAttr['type'] == 'resource':
                value = metaObjAttr.get('custom',None)
                if value is not None:
                  value = value._getCopy()
                  value.mediadbfile = None
                  value.aq_parent = self
                  value.key = key
                  value.lang = None
                  filename = value.getFilename()
                  if filename == name:
                    return value
        
        # If the object has blob-fields find by filename and display data.
        v = handleBlobAttrs( self, name, req)
        if v is not None: return v
        
        # If there's no more names left to handle, return the path handling 
        # method to the traversal machinery so it gets called next
        exc_value='<h2>Site-Error</h2><b>Sorry, there is no web page matching your request.</b> It is possible you typed the address incorrectly, or that the page no longer exists.<hr><b>Resource<b> <i>'+name+'</i> '+''.join(map(lambda x: x+'/',TraversalRequest['path_to_handle']))+' GET'
        return self.standard_error_message( self, 
        	exc_type='Resource not found', 
        	exc_value=exc_value, 
        	REQUEST=self.REQUEST)


    # --------------------------------------------------------------------------
    #  PathHandler.pathob
    # --------------------------------------------------------------------------
    def pathob(self, path_to_handle, REQUEST):
      langs = self.getLangIds()
      path_ob = self
      path_index = 0
      while True:
        if path_index == len(path_to_handle):
          return path_ob
        path_item = path_to_handle[path_index].lower()
        if path_index == 0 and path_item in langs:
          REQUEST.set('lang',path_item)
        else:
          obs = path_ob.getChildNodes( REQUEST ,self.PAGES)
          path_ob = None
          for ob in obs:
            if validateId( self, path_item, REQUEST):
              path_ob = ob
          if path_ob is None: 
            break
        path_index = path_index + 1
      return None

################################################################################
