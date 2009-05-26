################################################################################
# zmsrubrik.py
#
# Implementation of class ZMSRubrik (deprecated!).
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
from zmscontainerobject import ZMSContainerObject


################################################################################
################################################################################
###
###   C l a s s
###
################################################################################
################################################################################
class ZMSRubrik(ZMSContainerObject):

    # Properties.
    # -----------
    meta_type = meta_id = 'ZMSRubrik'
    
    # Properties.
    # -----------
    __obj_attrs__ = {
        # Changed by
        'created_uid':{'datatype':'string','multilang':False,'xml':False},
        'created_dt':{'datatype':'datetime','multilang':False,'xml':False},
        'change_uid':{'datatype':'string','multilang':True,'xml':False,'lang_inherit':False},
        'change_dt':{'datatype':'datetime','multilang':True,'xml':False,'lang_inherit':False},
        # Version info
        'change_history':{'datatype':'list','xml':False,'default':[]},
        'master_version':{'datatype':'int','xml':False,'default':0},
        'major_version':{'datatype':'int','xml':False,'default':0},
        'minor_version':{'datatype':'int','xml':False,'default':0},
        # Versioned by
        'work_uid':{'datatype':'string','multilang':True,'xml':False,'lang_inherit':False},
        'work_dt':{'datatype':'datetime','multilang':True,'xml':False,'lang_inherit':False},
        # Properties
        'active':{'datatype':'boolean','multilang':True},
        'attr_active_start':{'datatype':'datetime','multilang':True},
        'attr_active_end':{'datatype':'datetime','multilang':True},
        'title':{'datatype':'string','multilang':True,'size':40},
        'titleshort':{'datatype':'string','multilang':True,'size':20},
        'titleimage':{'datatype':'image','multilang':True},
        'levelnfc':{'datatype':'string','type':'select','options':[0,0,1,1,2,2],'label':'ATTR_LEVELNFC'},
        'attr_cacheable':{'datatype':'boolean','default':True},
        # Meta-Data
        'attr_dc_coverage':{'datatype':'string'},
        # Meta-Dictionaries
        '$metadict':{'datatype':'MetaDict'},
    }

################################################################################
