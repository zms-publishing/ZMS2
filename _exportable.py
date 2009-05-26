################################################################################
# _exportable.py
#
# $Id: _exportable.py,v 1.9 2004/11/30 20:03:17 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.9 $
#
# Implementation of class Exportable (see below).
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
from App.Common import package_home
from OFS.Image import Image
import copy
import urllib
import tempfile
import os
import re
# Product Imports.
import _blobfields
import _fileutil
import _filtermanager
import _globals
import _xmllib


# ------------------------------------------------------------------------------
#  _exportable.exportFolder:
# ------------------------------------------------------------------------------
def exportFolder(self, root, path, id, REQUEST):
  if hasattr(root,id):
    folder = getattr(root,id)
    if folder.meta_type == 'Folder':
      for ob in folder.objectValues():
        if ob.meta_type == 'Folder':
          ob_id = ob.id
          exportFolder(self, ob,'%s/%s'%(path,id),ob_id,REQUEST)
        else:
          try:
            ob_id = ob.id()
          except:
            ob_id = str(ob.id)
          if ob.meta_type in [ 'DTML Document', 'DTML Method']:
            ob = _globals.dt_html(self,ob.raw,REQUEST)
          _fileutil.exportObj(ob,'%s/%s/%s'%(path,id,ob_id))


# ------------------------------------------------------------------------------
#  _exportable.findDelimiter:
# ------------------------------------------------------------------------------
def findDelimiter(s, delimiters=['"',"'"]):
  rtn = -1
  for delimiter in delimiters:
    i = s.find(delimiter)
    if rtn == -1:
      rtn = i
    elif i >= 0:
      rtn = min(rtn,i)
  return rtn


# ------------------------------------------------------------------------------
#  _exportable.rfindDelimiter:
# ------------------------------------------------------------------------------
def rfindDelimiter(s, delimiters=['"',"'"]):
  rtn = -1
  for delimiter in delimiters:
    i = s.rfind(delimiter)
    rtn = max(rtn,i)
  return rtn


# ------------------------------------------------------------------------------
#  _exportable.localHtml:
# ------------------------------------------------------------------------------
def localHtml(self, obj, html, REQUEST):
  
  # Process relative links to JavaScript.
  for js in [ 'comlib', 'datelib', 'formlib', 'zmilib', 'styleswitcher']:
    html = re.sub( '"(.*?)\_js(|\?lang=(.*?))"', '"\\1.js"', html)
  
  return html


# ------------------------------------------------------------------------------
#  _exportable.localIndexHtml:
# ------------------------------------------------------------------------------
def localIndexHtml(self, obj, level, html, REQUEST):
   
   sRoot = ''
   for i in range(level):
     sRoot = '../%s'%sRoot
     
   # Process absolute URLs
   s_new = '%s'%sRoot
   s_old = '%s/'%self.absolute_url()
   html = html.replace( s_old, s_new)
   s_old = '%s/'%self.getDocumentElement().absolute_url()
   html = html.replace( s_old, s_new)
   s_old = '%s/'%self.getHome().absolute_url()
   html = html.replace( s_old, s_new)
   
   # Process links to resource-folders: images and assets.
   for id in [ 'common', 'instance']:
     if hasattr( self, id):
       s_new = '"%s%s/'%(sRoot,id)
       s_old = '"./%s/'%(id)
       html = html.replace(s_old,s_new)
       s_old = '"%s/'%(id)
       html = html.replace(s_old,s_new)
   
   # Process links to product-folder: images and assets.
   s_new = '"%smisc_/zms/'%sRoot
   s_old = '"/misc_/zms/'
   html = html.replace(s_old,s_new)
   s_old = '"misc_/zms/'
   html = html.replace(s_old,s_new)
   # starting with '(' (in styles)
   s_new = '(%smisc_/zms/'%sRoot
   s_old = '(/misc_/zms/'
   html = html.replace(s_old,s_new)
   s_old = '(misc_/zms/'
   html = html.replace(s_old,s_new)
   
   # Process preview parameters.
   if not REQUEST.get('ZMS_PREVIEW_PRESERVE',False):
     html = re.sub('(\?|&)preview=preview','',html)
   
   # Process declarative URLs
   if self.getConfProperty('ZMS.pathhandler',0) != 0 and \
      self.getConfProperty('ZMS.export.pathhandler',0) == 1:
     newTmp = '..\\'
     oldTmp = '../'
     # Save links to root.
     html = html.replace( oldTmp, newTmp)
     # Replace 'index' in declarative URLs
     pageexts = ['.html']
     if 'attr_pageext' in self.getMetadictAttrs():
       metadictAttr = self.getMetadictAttr('attr_pageext')
       if metadictAttr.has_key('keys') and len(metadictAttr.get('keys')) > 0:
         pageexts = metadictAttr.get('keys')
     for pageext in pageexts:
       s_new = pageext
       s_old = '/index_%s%s'%(REQUEST['lang'],pageext)
       html = html.replace( s_old, s_new)
       # Replace 'index_print' & 'sitemap' in declarative URLs
       if obj.getLevel() > 0:
         for key in [ 'index_print', 'sitemap']:
           s_old = '"%s_%s%s'%(key,REQUEST['lang'],pageext)
           s_new = '"%s/%s_%s%s'%(obj.getDeclId(REQUEST),key,REQUEST['lang'],pageext)
           html = html.replace( s_old, s_new)
     # Restore links to root.
     html = html.replace( newTmp, oldTmp)
   
   return html


################################################################################
################################################################################
###
###   class Exportable
###
################################################################################
################################################################################
class Exportable:

    ############################################################################    
    #  Exportable.manage_export:
    #
    #  Exports ZMS-object.
    ############################################################################    
    def manage_export(self, export_format, lang, REQUEST, RESPONSE):
      """ Exportable.manage_export """
      
      title = self.getHome().id + '_' + _globals.id_quote( self.getTitlealt( REQUEST))
      
      # Get export format.
      try:
        export_format = int( export_format)
      except:
        pass
      
      get_data = REQUEST.get( 'download', 1) == 1
      
      # ZEXP.
      if export_format == 0:
        filename = '%s.zexp'%self.id
        export = self.aq_parent.manage_exportObject( id=self.id, download=1)
        content_type = 'application/data'
      
      # HTML.
      elif export_format == 1:
        filename = '%s_html.zip'%title
        export = self.toZippedHtml( REQUEST, get_data)
        content_type = 'application/zip'
      
      # XML.
      elif export_format in [ 2, 4]: 
        incl_embedded = export_format == 4
        filename = '%s_xml.zip'%title
        export = self.toZippedXml( REQUEST, get_data, incl_embedded)
        content_type = 'application/zip'
      
      # myXML.
      elif export_format == 3: 
        instance_home = INSTANCE_HOME
        software_home = os.path.join(SOFTWARE_HOME, '..%s..' % os.sep)
        software_home = os.path.normpath(software_home)  
        REQUEST.set( 'ZMS_FILTER_SOFTWARE_HOME', software_home)
        REQUEST.set( 'ZMS_FILTER_INSTANCE_HOME', instance_home)
        REQUEST.set( 'ZMS_FILTER_PACKAGE_HOME', package_home(globals()))
        filename = '%s.xml'%title
        export = self.getXmlHeader() + getattr( self, 'getObjToXml_DocElmnt')(context=self)
        content_type = 'text/xml'
      
      # Export Filter.
      elif export_format in self.getFilterIds():
        filename, export, content_type = _filtermanager.exportFilter(self, export_format, REQUEST)
      
      # return export for download to browser
      if get_data:
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
        return export
      else:
        message = 'Exported to %s (%s)'%(export,content_type)
        url = '%s/manage_importexport'%self.absolute_url()
        url = self.url_append_params( url, { 'lang': lang, 'manage_tabs_message': message})
        RESPONSE.redirect( url)


    ############################################################################    
    #  Exportable.pub_export:
    #
    #  Exports ZMS-object.
    ############################################################################    
    def pub_export(self, export_format, lang, REQUEST, RESPONSE):
      """ Exportable.pub_export """
      self.f_standard_html_request( self, REQUEST)
      return self.manage_export( export_format, lang, REQUEST, RESPONSE)


    # --------------------------------------------------------------------------
    #  Exportable.getObjToXml:
    #
    #  myXML
    # --------------------------------------------------------------------------
    def getObjToXml(self):
      xml = []
      method = getattr( self, 'getObjToXml_%s'%self.meta_id_or_type(), None)
      if method is not None:
        xml.append( method( context=self))
      return ''.join(xml)

    # --------------------------------------------------------------------------
    #  Exportable.getObjChildrenToXml:
    #
    #  myXML
    # --------------------------------------------------------------------------
    def getObjChildrenToXml(self):
      REQUEST = self.REQUEST
      xml = []
      for context in self.filteredChildNodes(REQUEST):
        xml.append( context.getObjToXml())
      return ''.join(xml)
          

    # --------------------------------------------------------------------------
    #  Exportable.toXhtml:
    #
    #  (X)HTNL
    # --------------------------------------------------------------------------
    def toXhtml(self, REQUEST, deep=True):
      if _globals.debug( self):
        _globals.writeLog( self, '[toXhtml]')
      level = 0
      html = ''
      if REQUEST.has_key( 'ZMS_PAGE_HTML_HEADER'):
        html += getattr( self, REQUEST.get( 'ZMS_PAGE_HTML_HEADER'))( self, REQUEST)
      else:
        html += '<html>\n'
        html += '<head>\n'
        html += self.f_headMeta_Locale( self, REQUEST)
        html += '<title>%s</title>\n'%self.getTitle(REQUEST)
        html += '</head>\n'
        html += '<body>\n'
      html += self.printHtml( level, _globals.MySectionizer(), REQUEST, deep)
      if REQUEST.has_key( 'ZMS_PAGE_HTML_FOOTER'):
        html += getattr( self, REQUEST.get( 'ZMS_PAGE_HTML_FOOTER'))( self, REQUEST)
      else:
        html += '</body>\n'
        html += '</html>\n'
      html = localHtml( self, self, html, REQUEST)
      html = localIndexHtml( self, self, level, html, REQUEST)
      return html


    # --------------------------------------------------------------------------
    #  Exportable.toXml:
    # --------------------------------------------------------------------------
    def toXml(self, REQUEST, incl_embedded=False, deep=True, data2hex=False):
      xml = ''
      xml += _xmllib.xml_header()
      xml += _xmllib.getObjToXml( self, REQUEST, incl_embedded, deep, base_path='', data2hex=data2hex)
      return xml 


    # --------------------------------------------------------------------------
    #  Exportable.exportRessources:
    #
    #  Returns list of exported resources (Images, StyleSheets, etc.)
    # --------------------------------------------------------------------------
    def exportRessources(self, tempfolder, REQUEST, from_content=True, from_zms=False, from_common=False, incl_embedded=False):
      ressources = []
      
      if from_zms:
        folder = 'misc_/zms'
        for obj_id in self.misc_.zms._d.keys():
          _fileutil.exportObj(self.misc_.zms[obj_id],'%s/%s/%s'%(tempfolder,folder,obj_id))
      
      if from_common:
        for id in [ 'common', 'instance']:
          exportFolder( self, self.getHome(), tempfolder, id, REQUEST)
      
      if from_content:
        ressources.extend( self.exportContentRessources( tempfolder, REQUEST, incl_embedded))
      
      return ressources


    # --------------------------------------------------------------------------
    #  Exportable.exportContentRessources:
    #
    #  Returns list of exported resources (Images, StyleSheets, etc.)
    # --------------------------------------------------------------------------
    def exportContentRessources(self, tempfolder, REQUEST, incl_embedded):
      
      if REQUEST is not None:
      
        #-- JavaScript
        for js in [ 'comlib', 'formlib', 'datelib', 'formlib', 'zmilib', 'styleswitcher']:
          data = getattr(self,'%s_js'%(js))(self,REQUEST)
          filename = '%s.js'%js
          ressource = '%s/%s'%(tempfolder,filename)
          _fileutil.exportObj( data, ressource)
      
      # Download ressources (images & files)
      return _blobfields.recurse_downloadRessources( self, tempfolder+'/', REQUEST, incl_embedded)


    # --------------------------------------------------------------------------
    #	Exportable.exportExternalResources
    # --------------------------------------------------------------------------
    def exportExternalResources(self, obj, html, path, REQUEST):
      domains = []
      for domain in self.getConfProperty('ZMS.export.domains','').split(','):
        domain = domain.strip()
        if len( domain) > 0:
          domains.append( domain)
      if len( domains) == 0:
        return html
      for http_prefix in [ 'http:']:
        i = html.find( http_prefix)
        while i > 0:
          d = rfindDelimiter(html[:i]) # search delimiter ' or "
          k = rfindDelimiter(html[:d],'=') # search equal-sign between attribute name
          t = rfindDelimiter(html[:k],'<') # search start of tag
          # <img src="url">
          # <a href='url'">
          # <a href="javascript:open_function('url'...">
          if (html[ t + 1: t + 4].lower() == 'img' and html[ k - 3: k].lower() == 'src') \
              or (html[ t + 1].lower() == 'a' and html[ k - 4: k].lower() == 'href'):
            l = findDelimiter(html[ d + 1:])
            url = html[ d + 1: d + l + 1]        
            for domain in domains:
              if domain in url:
                try:
                  _globals.writeLog( self, '[exportExternalResources]: url=%s'%url)
                  s_new = s_old = url
                  for repl in ':/%&?;=':
                    s_new = s_new.replace(repl, '_')                  
                  # test if extension is a real extension at the end ?
                  # http://host:port/uri.gif?a=x&b=k => http___host_port_uri.gif_a_x_b_k.gif
                  # http://host:port/uri.gif => http__host_port_uri.gif
                  # http://host:port/draw/ID/png => http__host_port_draw_ID_png.png
                  # http://host:port/draw/ID?fmt=pdf&scale=2 => http__host_port_draw_ID_fmt_pdf_scale_2.pdf
                  for ext in ['gif','jpg','png','pdf','csv','xls','doc','ppt']:
                    if ext in url:
                      if s_new[-len(ext)-1:] != '.%s' % ext:
                        s_new = "%s.%s" %(s_new, ext)
                      break
                  ext_path = '%s/%s'%( path, s_new)
                  if not os.path.exists( ext_path):
                    data = self.http_import( url)
                    f = open( ext_path, 'w')
                    f.write( data)
                    f.close()
                  html = html.replace( s_old, s_new)
                except:
                  _globals.writeException( self, '[exportExternalResources]: url=%s'%url)
                break
          i = html.find( http_prefix, i + len( http_prefix))
      return html


    # --------------------------------------------------------------------------
    #	Exportable.recurse_downloadHtmlPages:
    # --------------------------------------------------------------------------
    def recurse_downloadHtmlPages(self, obj, path, lang, REQUEST):
      try:
        os.mkdir(path)
      except:
        pass
      
      level = obj.getLevel()
      dctOp = {'index':'','sitemap':'sitemap','index_print':'print'}
      for key in dctOp.keys():
        
        # Get html.
        REQUEST.set('op',dctOp[key])
        REQUEST.set('ZMS_PATH_HANDLER', True)
        
        try:

          # Remember others.
          others = copy.copy(REQUEST.other.keys())

          root = getattr( obj, '__root__', None)
          if root is not None:
            REQUEST.set('ZMS_PROXY_%s'%root.id,obj)
            html = root.index_html( root, REQUEST)
          else:
            html = obj.index_html( obj, REQUEST)

          # Remove new others.
          for rk in REQUEST.other.keys():
            if rk not in others:
              try:
                del REQUEST.other[rk]
              except:
                pass
          
          html = localHtml( self, obj, html, REQUEST)
          
          # Save html to file.
          if key == 'index' and \
             level > 0 and \
             self.getConfProperty('ZMS.pathhandler',0) != 0 and \
             self.getConfProperty('ZMS.export.pathhandler',0) == 1:
            html = localIndexHtml( self, obj, level - 1, html, REQUEST)
            filename = '%s/../%s%s'%( path, obj.getDeclId(REQUEST), obj.getPageExt(REQUEST))
          else:
            if key == 'sitemap':
              pageext = '.html'
            else:
              pageext = obj.getPageExt( REQUEST)
            html = localIndexHtml( self, obj, level - self.getLevel(), html, REQUEST)
            filename = '%s/%s_%s%s'%( path, key, lang, pageext)

          html = self.exportExternalResources( obj, html, path, REQUEST)

          f = open( filename, 'w')
          f.write( html)
          f.close()
          
          # Root folder requires and defaults to "index.html" at most systems.
          if key == 'index' and \
             level == 0 and lang == self.getPrimaryLanguage():
            filename = '%s/%s%s'%( path, key, obj.getPageExt( REQUEST))
            f = open(filename,'w')
            f.write(html)
            f.close()
          
        except:
          _globals.writeException( self, "[recurse_downloadHtmlPages]: Can't get html '%s'"%key)
        
      # Process DTML-methods of meta-objects.
      for metadictAttrId in self.getMetadictAttrs( obj.meta_type):
        try:
          metadictAttr = self.getMetadictAttr( metadictAttrId)
          if metadictAttr['type'] in self.getMetaobjIds():
            metaObj = self.getMetaobj( metadictAttr['type'])
            if metaObj['type'] == 'ZMSResource':
              for metadictObj in obj.getObjChildren( metadictAttr['id'], REQUEST):
                for metaObjAttr in metaObj['attrs']:
                  if metaObjAttr['type'] in [ 'DTML Document', 'DTML Method']:
                    html = getattr( obj, metaObjAttr['id'])( obj, REQUEST)
                    html = localHtml( self, obj, html, REQUEST)
                    filename = '%s/%s'%( path, metaObjAttr['id'])
                    f = open(filename,'w')
                    f.write(html)
                    f.close()
        except:
          _globals.writeException( self, "[recurse_downloadHtmlPages]: Can't process DTML-method '%s' of meta-object"%metadictAttr)
      
      # Process children.
      for child in obj.getChildNodes(REQUEST,self.PAGES):
        self.recurse_downloadHtmlPages(child,'%s/%s'%(path,child.getDeclId(REQUEST)),lang,REQUEST)


    # --------------------------------------------------------------------------
    #	Exportable.toZippedHtml:
    # --------------------------------------------------------------------------
    def toZippedHtml(self, REQUEST, get_data=True):
      
      #-- Create temporary folder.
      tempfolder = tempfile.mktemp()
      ressources = self.exportRessources( tempfolder, REQUEST, from_zms=self.getLevel()==0, from_common=True)
      
      #-- Download HTML-pages.
      for lang in self.getLangIds():
        REQUEST.set('ZMS_INDEX_HTML',1)
        REQUEST.set('ZMS_HTML_EXPORT',1)
        REQUEST.set('lang',lang)
        REQUEST.set('preview',None)
        self.recurse_downloadHtmlPages( self, tempfolder, lang, REQUEST)
      
      #-- Get zip-file.
      zipfiles = _fileutil.getOSPath('%s/*'%tempfolder)
      rtn = _fileutil.buildZipArchive( zipfiles, get_data)
      
      #-- Remove temporary folder.
      if not _globals.debug( self):
        _fileutil.remove( tempfolder, deep=1)
      
      return rtn


    # --------------------------------------------------------------------------
    #  Exportable.toZippedXml:
    # --------------------------------------------------------------------------
    def toZippedXml(self, REQUEST, get_data=True, incl_embedded=False):

      #-- Create temporary folder.
      tempfolder = tempfile.mktemp()
      ressources = self.exportRessources( tempfolder, REQUEST, incl_embedded=incl_embedded)
      
      #-- Get xml-export.
      xml = self.toXml(REQUEST,incl_embedded)
      
      #-- Write xml-export to file.
      xmlfilename = _fileutil.getOSPath('%s/%s_%s.xml'%(tempfolder,self.getHome().id,self.meta_type))
      _fileutil.exportObj(xml,xmlfilename)
      
      #-- Get zip-file.
      zipfiles = _fileutil.getOSPath('%s/*'%tempfolder)
      rtn = _fileutil.buildZipArchive( zipfiles, get_data)
      
      #-- Remove temporary folder.
      if not _globals.debug( self):
        _fileutil.remove( tempfolder, deep=1)
      
      return rtn

################################################################################
