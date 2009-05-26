################################################################################
# _sequence.py
#
# $Id: _sequence.py,v 1.1 2003/08/31 13:29:23 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.1 $
#
# Implementation of class Sequence (see below).
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
from Globals import MessageDialog
from Globals import Persistent   
import OFS.SimpleItem
import Acquisition
import AccessControl.Role
import urllib


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################
manage_addSequenceForm = HTMLFile('manage_addsequenceform', globals()) 
def manage_addSequence(self, startvalue=0, REQUEST=None, RESPONSE=None):
  """ manage_addSequence """
  
  # Create sequence.
  obj = Sequence(startvalue)
  self._setObject(obj.id, obj)
  
  # Return.
  if RESPONSE is not None:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())



################################################################################
################################################################################
###
###   C l a s s   S e q u e n c e 
###
################################################################################
################################################################################
class Sequence(
    OFS.SimpleItem.Item,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager
    ): 

    # Properties.
    # -----------
    meta_type = 'Sequence'

    # Management Options.
    # -------------------
    manage_options = (
	{'label': 'Properties','action': 'manage_properties'},
        ) 

    manage_properties = HTMLFile('dtml/acl_sequence/manage_properties', globals())

    """
    ############################################################################    
    #
    #   CONSTRUCTOR
    #
    ############################################################################    
    """

    ############################################################################
    #  Sequence.__init__: 
    #
    #  Initialise a new instance of Sequence.
    ############################################################################
    def __init__(self, startvalue=0):
      self.id = 'acl_sequence'
      self.value = startvalue

    """
    ############################################################################    
    #
    #   FUNCTIONS
    #
    ############################################################################    
    """

    # --------------------------------------------------------------------------
    #  Sequence.nextVal
    # --------------------------------------------------------------------------
    def nextVal(self):
      self.value = self.value + 1
      return self.currVal()

    # --------------------------------------------------------------------------
    #  Sequence.currVal
    # --------------------------------------------------------------------------
    def currVal(self):
      return self.value


    """
    ############################################################################    
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################    
    """

    ############################################################################
    #  Sequence.manage_changeProperties: 
    #
    #  Change Sequence properties.
    ############################################################################
    def manage_changeProperties(self, submit, currentvalue, REQUEST, RESPONSE): 
      """ Sequence.manage_changeProperties """
      
      message = ''

      # Set current value.
      if submit == 'Change':
        if currentvalue >= self.value:
          self.value = currentvalue
        
      # Fetch next value.
      if submit == 'Next':
        self.nextVal()

      # Return.
      if RESPONSE is not None:
        RESPONSE.redirect('manage_properties?manage_tabs_message=%s'%urllib.quote(message))

################################################################################
