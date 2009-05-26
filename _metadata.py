################################################################################
# _metadata.py
#
# $Id: _metadata.py,v 1.1 2003/08/31 13:29:22 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.1 $
#
# Implementation of class Metadata (see below).
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
# Product Imports.
import _globals


################################################################################
################################################################################
###
###   C L A S S   M E T A D A T A
###
################################################################################
################################################################################
class Metadata:


    # Management Interface.
    # ---------------------
    f_metaInputFields = HTMLFile('dtml/metadict/f_metainputfields', globals()) 
    f_metaInputField = HTMLFile('dtml/metadict/f_metainputfield', globals()) 
    f_metaInputJS = HTMLFile('dtml/metadict/input_js', globals()) 


    # --------------------------------------------------------------------------
    #  Metadata.getDCCoverageOptions:
    #
    #  Values for select-list of DC.Coverage.
    # --------------------------------------------------------------------------
    def getDCCoverageOptions(self, REQUEST, meta_type=None):
      obs = []
      lang = REQUEST['lang']
      meta_type = _globals.nvl(meta_type,self.meta_type)
      coverage = self.getDCCoverage(REQUEST)
      if REQUEST.get('ZMS_INSERT',None) is None:
        coverage_lang = coverage[coverage.find('.')+1:]
        if lang != coverage_lang:
          obs.append(coverage)
        else:
          obs.append('global.'+coverage_lang)
          obs.append('local.'+coverage_lang)
      else:
        obs.append('global.'+lang)
        obs.append('local.'+lang)
      return obs


    # --------------------------------------------------------------------------
    #	Metadata.setMetadata:
    #
    #	Changes Metadata.
    # --------------------------------------------------------------------------
    def setMetadata(self, lang, REQUEST):
      if REQUEST.get('btn','') not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        if 'attr_dc_coverage' in self.getObjAttrs().keys():
          self.setReqProperty('attr_dc_coverage',REQUEST)
        for attr in self.getMetadictAttrs(self.meta_type):
          objAttr = self.getMetadictAttr(attr)
          if objAttr['type'] in self.getMetaobjIds(sort=0) and \
             self.getMetaobj(objAttr['type'])['type']=='ZMSResource':
            for ob in self.getObjChildren(objAttr['id'],REQUEST):
              ob.setObjStateModified(REQUEST)
              for key in self.getMetaobjAttrIds(objAttr['type']):
                ob.setReqProperty(key,REQUEST)
              ob.onChangeObj(REQUEST)
          else:
            self.setReqProperty(objAttr['key'],REQUEST)

################################################################################
