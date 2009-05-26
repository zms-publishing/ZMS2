################################################################################
# _ztrashcanclient.py
#
# $Id: _ztrashcanclient.py,v 1.4 2004/03/24 18:04:14 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.4 $
#
# Implementation of classes ZTrashcanClient (see below).
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


# Product Imports.
import _globals


################################################################################
################################################################################
###
###   class ZTrashcanClient
###
################################################################################
################################################################################
class ZTrashcanClient:

  # ----------------------------------------------------------------------------
  #  ZTrashcanClient.moveObjsToTrashcan
  # ----------------------------------------------------------------------------
  def moveObjsToTrashcan(self, ids, REQUEST):
    if self.meta_type == 'ZMSTrashcan': return
    trashcan = self.getTrashcan()
    # Move (Cut & Paste).
    try:
      cb_copy_data = self.manage_cutObjects(ids,REQUEST)
      trashcan.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
    except:
      if len(ids) > 1:
        except_ids = []
        for id in ids:
          try:
            cb_copy_data = self.manage_cutObjects([id],REQUEST)
            trashcan.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
          except:
            except_ids.append(id)
      else:
        except_ids = ids
      if len(except_ids) > 0:
        _globals.writeException(self,'[moveObjsToTrashcan]: Unexpected Exception: ids=%s!'%str(except_ids))
    trashcan.normalizeSortIds()
    # Sort-IDs.
    self.normalizeSortIds()


  # ----------------------------------------------------------------------------
  #  ZTrashcanClient.getTrashcan
  # ----------------------------------------------------------------------------
  def getTrashcan(self):
    docElmnt = self.getDocumentElement()
    if len(docElmnt.objectValues(['ZMSTrashcan']))==0:
      docElmnt.manage_addZMSObject('ZMSTrashcan',values={},REQUEST={'lang':self.getPrimaryLanguage()})
    return docElmnt.objectValues(['ZMSTrashcan'])[0]
    
################################################################################
