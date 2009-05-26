################################################################################
# zmstable.py
#
# $Id: zmstable.py,v 1.6 2004/11/23 23:04:51 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.6 $
#
# Implementation of class ZMSTable (see below).
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
import copy
# Product Imports.
from zmsobject import ZMSObject
import _globals
import _metadata


################################################################################
################################################################################
###   
###   constructor ZMSTable:
###   
################################################################################
################################################################################
manage_addZMSTableForm = HTMLFile('manage_addzmstableform', globals()) 
def manage_addZMSTable(self, lang, manage_lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSTable """
  
  if REQUEST['btn'] == self.getLangStr('BTN_INSERT',manage_lang):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSTable(self.getNewId(id_prefix),_sort_id+1)
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
    
    # Active.
    obj.setReqProperty('active',REQUEST)
    obj.setReqProperty('attr_active_start',REQUEST)
    obj.setReqProperty('attr_active_end',REQUEST)
    
    # Caption.
    obj.setReqProperty('caption',REQUEST)
    obj.setReqProperty('align',REQUEST)
    
    # Table.
    table = []
    tabletype = REQUEST['table_type']
    numrows = REQUEST['table_rows']
    numcols = REQUEST['table_cols']
    
    #  <TH> <TH> <TH>
    #  <td> <td> <td>
    #  <td> <td> <td>
    if tabletype == 1:
      row = []
      for colnum in range(numcols):
        row.append(obj.__init_cell__('th',1))
      table.append(row)
      for rownum in range(1,numrows):
        row = []
        for colnum in range(numcols):
          row.append(obj.__init_cell__('td',1))
        table.append(row)
    
    #  <     TH     >
    #  <td> <td> <td>
    #  <td> <td> <td>
    elif tabletype == 2:
      row = [obj.__init_cell__('th',numcols)]
      table.append(row)
      for rownum in range(1,numrows):
        row = []
        for colnum in range(numcols):
          row.append(obj.__init_cell__('td',1))
        table.append(row)
    
    #  <TH> <td> <td>
    #  <TH> <td> <td>
    #  <TH> <td> <td>
    elif tabletype == 3:
      for rownum in range(numrows):
        row = [obj.__init_cell__('th',1)]
        for colnum in range(1,numcols):
          row.append(obj.__init_cell__('td',1))
        table.append(row)
    
    #       <TH> <TH>
    #  <TH> <td> <td>
    #  <TH> <td> <td>
    elif tabletype == 4:
      row = []
      row.append(obj.__init_cell__('td',1))
      for colnum in range(1,numcols):
        row.append(obj.__init_cell__('th',1))
      table.append(row)
      for rownum in range(1,numrows):
        row = [obj.__init_cell__('th',1)]
        for colnum in range(1,numcols):
          row.append(obj.__init_cell__('td',1))
        table.append(row)
    
    #  <td> <td> <td>
    #  <td> <td> <td>
    #  <td> <td> <td>
    elif tabletype == 5:
      for rownum in range(numrows):
        row = []
        for colnum in range(numcols):
          row.append(obj.__init_cell__('td',1))
        table.append(row)
    
    obj.setObjProperty('table',table,lang)
    obj.setObjProperty('type',tabletype)
    obj.setObjProperty('rows',numrows,lang)
    obj.setObjProperty('cols',numcols,lang)
    
    ##### VersionManager ####
    obj.onChangeObj(REQUEST)
    
    ##### Normalize Sort-IDs ####
    self.normalizeSortIds(id_prefix)
    
    message = self.getLangStr('MSG_INSERTED',manage_lang)%obj.display_type(REQUEST)
    RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,manage_lang,urllib.quote(message)))
  
  else:
    RESPONSE.redirect('%s/manage_main?lang=%s&manage_lang=%s'%(self.absolute_url(),lang,manage_lang))


################################################################################
################################################################################
###   
###   class ZMSTable:
###   
################################################################################
################################################################################
class ZMSTable(ZMSObject, _metadata.Metadata):

    # Properties.
    # -----------
    meta_type = "ZMSTable"
    icon = "misc_/zms/zmstable.gif"
    icon_disabled = "misc_/zms/zmstable_disabled.gif"

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
        'active':{'datatype':'boolean' ,'multilang':True},
        'attr_active_start':{'datatype':'datetime' ,'multilang':True},
        'attr_active_end':{'datatype':'datetime' ,'multilang':True},
        'type':{'datatype':'int' ,'default':True},
        'rows':{'datatype':'int' ,'multilang':True},
        'cols':{'datatype':'int' ,'multilang':True},
        'table':{'datatype':'list' ,'multilang':True},
        'caption':{'datatype':'string' ,'multilang':True},
        'align':{'datatype':'string', 'type':'select','default':'TOP','options':['TOP','TOP','BOTTOM','BOTTOM','LEFT','LEFT','RIGHT','RIGHT']},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries        
        '$metadict':{'datatype':'MetaDict'},
    }


    # Management Interface
    # ---------------------
    manage_main = HTMLFile('dtml/zmstable/manage_main', globals()) 
    table_cell_edit_html = HTMLFile('dtml/zmstable/table_cell_edit', globals())


    """
    ############################################################################    
    #
    #   CONSTRUCTOR
    #
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #	ZMSTable.getSpanOptions:
    # --------------------------------------------------------------------------
    def getSpanOptions(self, i, n):
      options = []
      for o in range(1, n-i+1):
        options.append((o,o))
      return options


    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """

    ############################################################################
    #  ZMSTable.manage_changeProperties: 
    #
    #  Change Table properties.
    ############################################################################
    def manage_changeProperties(self, lang, manage_lang, REQUEST, RESPONSE): 
        """ ZMSTable.manage_changeProperties """
        
        self._checkWebDAVLock()
        message = ''
        if len(REQUEST.get('function','')) > 0 or \
           REQUEST.get('btn','') not in [ self.getLangStr('BTN_CANCEL',manage_lang), self.getLangStr('BTN_BACK',manage_lang)]:
        
          ##### Object State #####
          self.setObjStateModified(REQUEST)
            
          ##### Properties #####
          # Active.
          self.setReqProperty('active',REQUEST)
          self.setReqProperty('attr_active_start',REQUEST)
          self.setReqProperty('attr_active_end',REQUEST)
          # Type.
          if REQUEST.has_key('type'): 
            self.setReqProperty('type',REQUEST)
          # Caption.
          self.setReqProperty('caption',REQUEST)
          self.setReqProperty('align',REQUEST)

          ##### Metadata ####
          self.setMetadata(lang,manage_lang,REQUEST)
        
          table = self.getTable( REQUEST)

          for reqkey in REQUEST.keys():
            if reqkey.find('cell') == 0 and len(reqkey.split('_')) == 3:
              colnum = int(reqkey.split('_')[1])
              rownum = int(reqkey.split('_')[2])
              row = table[ rownum]
              cell = row[ colnum]
              cell['tag'] = REQUEST['tag_%i_%i'%(colnum,rownum)].strip()
              cell['content'] = REQUEST['cell_%i_%i'%(colnum,rownum)].strip()
              cell['format'] = REQUEST['format_%i_%i'%(colnum,rownum)].strip()
          
          if REQUEST.has_key('function'):
            sFunction = REQUEST['function']
            sRow = REQUEST['row']
            sCol = REQUEST['col']
            if len(sFunction) > 0 and len(sRow) > 0 and len(sCol) > 0:
              rownum = int(sRow)
              colnum = int(sCol)
              if sFunction == 'move_row_down':
                self.move_row(table,rownum,1,lang,REQUEST)
              elif sFunction == 'move_row_up':
                self.move_row(table,rownum,-1,lang,REQUEST)
              elif sFunction == 'delete_row':
                self.delete_row(table,rownum,lang,REQUEST)
              elif sFunction == 'insert_row':
                self.insert_row(table,rownum,lang,REQUEST)
              elif sFunction == 'move_col_right':
                self.move_col(table,colnum,1,lang,REQUEST)
              elif sFunction == 'move_col_left':
                self.move_col(table,colnum,-1,lang,REQUEST)
              elif sFunction == 'delete_col':
                self.delete_col(table,colnum,lang,REQUEST)
              elif sFunction == 'insert_col':
                self.insert_col(table,colnum,lang,REQUEST)

          self.setObjProperty('table',table,lang)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
          
          ##### Message #####
          message = self.getLangStr('MSG_CHANGED',manage_lang)
          
          if (REQUEST.has_key('function') and len(REQUEST['function'])>0):
            return RESPONSE.redirect('manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s'%(lang,manage_lang,urllib.quote(message)))
        
        # Return with message.
        self.checkIn(REQUEST)
        return RESPONSE.redirect('%s/manage_main?lang=%s&manage_lang=%s&manage_tabs_message=%s#_%s'%(self.getParentNode().absolute_url(),lang,manage_lang,urllib.quote(message),self.id))


    # --------------------------------------------------------------------------
    #  ZMSTable.isPageElement:
    # --------------------------------------------------------------------------
    def isPageElement(self): 
      return True

    # --------------------------------------------------------------------------
    #  ZMSTable.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt(self,REQUEST): 
      return self.display_type(REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSTable.getTable
    # --------------------------------------------------------------------------
    def getTable(self, REQUEST): 
      table = self.getObjProperty('table',REQUEST)
      return table

    # --------------------------------------------------------------------------
    #  ZMSTable.getRow
    # --------------------------------------------------------------------------
    def getRow(self, rownum, REQUEST): 
      table = self.getTable( REQUEST)
      row = table[ rownum]
      return row

    # --------------------------------------------------------------------------
    #  ZMSTable.getCell
    # --------------------------------------------------------------------------
    def getCell(self, rownum, colnum, REQUEST): 
      row = self.getRow( rownum, REQUEST)
      cell = row[ colnum]
      return cell


    ############################################################################    
    # Column
    ############################################################################    

    # --------------------------------------------------------------------------
    #	ZMSTable.insert_col:
    # --------------------------------------------------------------------------
    def insert_col(self, table, colnum, lang, REQUEST):
      type = self.getObjProperty('type',REQUEST)
      rownum = 0
      for row in table:
        if not (rownum == 0 and type == 2):
          cell = self.__init_cell__('td',1)
          if rownum > 0 or self.getObjProperty('type',REQUEST) in [3,5]:
            cell['tag'] = 'td'
          else:
            cell['tag'] = 'th'
          row.insert(colnum,cell)
        rownum = rownum + 1
      # increase number of columns
      cols = self.getObjProperty('cols',REQUEST)+1
      self.setObjProperty('cols',cols,lang)
      #
      if type == 2:
        cell = table[0][0]
        cell['colspan'] = cols

    # --------------------------------------------------------------------------
    #	ZMSTable.delete_col:
    # --------------------------------------------------------------------------
    def delete_col(self, table, colnum, lang, REQUEST):
      type = self.getObjProperty('type',REQUEST)
      rownum = 0
      for row in table:
       if not (rownum == 0 and type == 2):
         row.remove(row[colnum])
       rownum = rownum + 1
      # decrease number of columns
      cols = self.getObjProperty('cols',REQUEST)-1
      self.setObjProperty('cols',cols,lang)
      #
      if type == 2:
        cell = table[0][0]
        cell['colspan'] = cols

    # --------------------------------------------------------------------------
    #	ZMSTable.move_col:
    #
    #	Move column left or right.
    # --------------------------------------------------------------------------
    def move_col(self, table, colnum, direction, lang, REQUEST):
      rownum = 0
      for oRow in table:
        if not (rownum == 0 and self.getObjProperty('type',REQUEST) == 2):
          cell1 = table[rownum][colnum]
          cell2 = table[rownum][colnum+direction]
          content = cell1['content']
          cell1['content'] = cell2['content']
          cell2['content'] = content
        rownum = rownum + 1


    ############################################################################    
    # Row
    ############################################################################    

    # --------------------------------------------------------------------------
    #	ZMSTable.insert_row:
    # --------------------------------------------------------------------------
    def insert_row(self, table, rownum, lang, REQUEST):
      # increase number of rows
      self.setObjProperty('rows',self.getObjProperty('rows',REQUEST)+1,lang)
      # init new row
      row = []
      if self.getObjProperty('type',REQUEST) in [1,2]:
        for colnum in range(self.getObjProperty('cols',REQUEST)):
          row.append(self.__init_cell__('td',1))
      elif self.getObjProperty('type',REQUEST) in [3,4]:
        row.append(self.__init_cell__('th',1))
        for colnum in range(1,self.getObjProperty('cols',REQUEST)):
          row.append(self.__init_cell__('td',1))
      elif self.getObjProperty('type',REQUEST) in [5]:
        for colnum in range(self.getObjProperty('cols',REQUEST)):
          row.append(self.__init_cell__('td',1))
      # insert new row
      table.insert(rownum,row)

    # --------------------------------------------------------------------------
    #	ZMSTable.delete_row:
    # --------------------------------------------------------------------------
    def delete_row(self, table, rownum, lang, REQUEST):
      # decrease number of rows
      self.setObjProperty('rows',self.getObjProperty('rows',REQUEST)-1,lang)
      # remove row
      table.remove(table[rownum])

    # --------------------------------------------------------------------------
    #	ZMSTable.move_row:
    #
    #	Move row up or down.
    # --------------------------------------------------------------------------
    def move_row(self, table, rownum, direction, lang, REQUEST):
      row1 = copy.deepcopy(table[rownum+direction])
      row2 = copy.deepcopy(table[rownum])
      table[rownum+direction] = row2
      table[rownum] = row1


    """
    ############################################################################
    ###
    ###  H T M L - P r e s e n t a t i o n 
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSTable.getBodyContent:
    #         
    #  HTML presentation of Table. 
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      type = self.getObjProperty('type',REQUEST)
      table = self.getObjProperty('table',REQUEST)
      s = []
      s.append('\n<table')
      s.append(' id="'+self.id+'"')
      s.append(' class="'+self.meta_type+'"')
      # Summary
      tableSummary = self.getObjProperty('attr_dc_description',REQUEST)
      if tableSummary:
        s.append(' summary="'+tableSummary+'"')
      s.append('>')
      # Caption
      
      s.append('\n<caption')
      if self.getObjProperty('align',REQUEST):
        s.append(' align="'+self.getObjProperty('align',REQUEST).lower()+'"')
      s.append('>' + self.getObjProperty('caption',REQUEST) + '</caption>')
      if len( table) > 0:
        # Columns
        columns = max( map( lambda row: len( row), table))
        weights = map( lambda x: 1, range( columns))
        # Content
        content = []
        rowindex = 0
        tag = None
        for row in table:
          newtag = None
          if (type in [1,2,4] and rowindex == 0):
            newtag = 'thead'
          elif (type in [1,2,4] and rowindex == 1) or (rowindex == 0):
            newtag = 'tbody'
          if newtag is not None:
            if tag is not None:
              content.append('\n</' + tag + '>')
            content.append('\n<' + newtag + '>')
            tag = newtag
          content.append('\n<tr')
          if rowindex%2==0:
            content.append(' class="even"')
          else:
            content.append(' class="odd"')
          content.append('>')
          colindex = 0
          for cell in row:
            if rowindex == 0 and colindex == 0 and type == 4:
              content.append('\n<td></td>')
              colindex = colindex + 1
            else:
              # Retrieve properties.
              text = cell['content']
              textformat = cell['format']
              colspan = int(cell['colspan'])
              # Render HTML presentation.
              text = self.renderText( textformat, text, REQUEST)
              try:
                text = _globals.dt_html(self,text,REQUEST)
              except:
                text = _globals.writeException(self,'[_getBodyContent]: (%i,%i)'%(colindex, rowindex))
              text = self.renderContentEditable('table_%i_%i'%(colindex, rowindex), text, REQUEST)
              content.append('\n<%s'%cell['tag'])
              if colspan > 1:
                content.append(' colspan="%i"'%colspan)
              else:
                weights[ colindex] += len( str( text))
              content.append('>')
              content.append(text)
              content.append('</%s>'%cell['tag'])
              for i in range( colspan):
                if colindex < len( weights):
                  weights[ colindex] += len( str( text)) / colspan
                  colindex += 1
          content.append('\n</tr>')
          rowindex += 1
        if tag is not None:
          content.append('\n</' + tag + '>')
        # Assemble colgroup.
        weightssum = sum( weights)
        s.append('\n<colgroup>')
        s.extend( map( lambda weight: '\n<col width="%i'%int(100*weight/weightssum)+'%"/>', weights))
	s.append('\n</colgroup>')
	# Append content.
	s.extend( content)
      s.append('\n</table>')
      # Return body-content.
      return ''.join(s)


    # --------------------------------------------------------------------------
    #  ZMSTable.renderShort:
    #
    #  Renders short presentation of Table.
    # --------------------------------------------------------------------------
    def renderShort(self,REQUEST):
      return self._getBodyContent(REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSTable.catalogText:
    #
    #  Catalog text of Table (overwrite method from ZCatalogItem).
    # --------------------------------------------------------------------------
    def catalogText(self, REQUEST):
      s = ''
      if self.isVisible(REQUEST):
        table = self.getObjProperty('table',REQUEST)
        for row in table:
          for cell in row:
            s += cell['content'] + ' '
      return s


    """
    ############################################################################    
    #
    #   C e l l 
    #
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  ZMSTable.__init_cell__:
    #
    #  Initialise table-cell.
    # --------------------------------------------------------------------------
    def __init_cell__(self, tag='', colspan=1, content=''):
      cell = {}
      cell['tag'] = tag
      cell['colspan'] = colspan
      cell['content'] = content
      cell['format'] = self.getTextFormatDefault()
      return cell

################################################################################
