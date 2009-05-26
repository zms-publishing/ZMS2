################################################################################
# Initialisation file for the ZMS Product for Zope
#
# $Id: __init__.py,v 1.3 2004/11/24 21:02:52 zmsdev Exp $
# $Name:  $
# $Author: zmsdev $
# $Revision: 1.3 $
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
#
################################################################################

"""ZMS Product"""

# Documentation string.
__doc__ = """initialization module."""
# Version string.
__version__ = '0.1'

# Imports.
from Globals import ImageFile
from App.Common import package_home
import OFS.misc_
import os
import stat
# Product Imports.
import zms
import zmsdocument
import zmstextarea 
import zmsgraphic
import zmstable
import zmsfile
import zmsfolder
import zmsnote
import zmsrubrik
import zmsteasercontainer
import zmsteaserelement
import zmscustom
import zmssqldb
import zmssysfolder
import zmslinkcontainer
import zmslinkelement
import zmslog
import _mediadb
import _sequence
import _zmsattributecontainer

################################################################################
# Define the initialize() function. 
################################################################################

def initialize(context): 
    """Initialize the product."""
    
    try: 
        """Try to register the product."""
        
        context.registerClass(
            zms.ZMS,
            permission = 'Add ZMSs',
            constructors = ( zms.manage_addZMSForm, zms.manage_addZMS),
            icon = 'www/zms.gif'                
            )
        context.registerClass(
            zmssysfolder.ZMSSysFolder,
            permission = 'Add ZMSs',
            constructors = ( zmssysfolder.manage_addZMSSysFolderForm, zmssysfolder.manage_addZMSSysFolder),
            icon = 'www/zmssysfolder.gif'
            )
        context.registerClass(
            zmsrubrik.ZMSRubrik,
            permission = 'Add ZMSs',
            constructors = ( zmsfolder.manage_addZMSFolderForm, zmsfolder.manage_addZMSFolder),
            icon = 'www/zmsfolder.gif'
            )
        context.registerClass(
            zmsfolder.ZMSFolder,
            permission = 'Add ZMSs',
            constructors = ( zmsfolder.manage_addZMSFolderForm, zmsfolder.manage_addZMSFolder),
            icon = 'www/zmsfolder.gif'
            )
        context.registerClass(
            zmsdocument.ZMSDocument,
            permission = 'Add ZMSs',
            constructors = ( zmsdocument.manage_addZMSDocumentForm, zmsdocument.manage_addZMSDocument),
            icon = 'www/zmsdocument.gif'
            )
        context.registerClass(
            zmstextarea.ZMSTextarea,
            permission = 'Add ZMSs',
            constructors = (zmstextarea.manage_addZMSTextareaForm, zmstextarea.manage_addZMSTextarea),
            icon = 'www/zmstextarea.gif'
            )
        context.registerClass(
            zmsnote.ZMSNote,
            permission = 'Add ZMSs',
            constructors = (zmsnote.manage_addZMSNote, zmsnote.manage_addZMSNote),
            icon = 'www/zmsnote.gif'
            )
        context.registerClass(
            zmscustom.ZMSCustom,
            permission = 'Add ZMSs',
            constructors = (zmscustom.manage_addZMSCustomForm, zmscustom.manage_addZMSCustom),
            icon = 'www/zmsdocument.gif'
            )
        context.registerClass(
            zmsteasercontainer.ZMSTeaserContainer,
            permission = 'Add ZMSs',
            constructors = (zmsteasercontainer.manage_addZMSTeaserContainer, zmsteasercontainer.manage_addZMSTeaserContainer),
            icon = 'www/zmsteaser.gif'
            )
        context.registerClass(
            zmsteaserelement.ZMSTeaserElement,
            permission = 'Add ZMSs',
            constructors = (zmsteaserelement.manage_addZMSTeaserElement, zmsteaserelement.manage_addZMSTeaserElement),
            icon = 'www/zmsteaser.gif'
            )
        context.registerClass(
            zmsgraphic.ZMSGraphic,
            permission = 'Add ZMSs',
            constructors = (zmsgraphic.manage_addZMSGraphicForm, zmsgraphic.manage_addZMSGraphic),
            icon = 'www/zmsgraphic.gif'
            )
        context.registerClass(
            zmstable.ZMSTable,
            permission = 'Add ZMSs',
            constructors = ( zmstable.manage_addZMSTableForm, zmstable.manage_addZMSTable),
            icon = 'www/zmstable.gif'
            )
        context.registerClass(
            zmsfile.ZMSFile,
            permission = 'Add ZMSs',
            constructors = ( zmsfile.manage_addZMSFileForm, zmsfile.manage_addZMSFile),
            icon = 'www/zmsfile.gif'
            )
        context.registerClass(
            zmssqldb.ZMSSqlDb,
            permission = 'Add ZMSs',
            constructors = (zmssqldb.manage_addZMSSqlDbForm, zmssqldb.manage_addZMSSqlDb),
            icon = 'www/zmssqldb.gif'
            )
        context.registerClass(
            zmslinkcontainer.ZMSLinkContainer,
            permission = 'Add ZMSs',
            constructors = (zmslinkcontainer.manage_addZMSLinkContainer, zmslinkcontainer.manage_addZMSLinkContainer),
            icon = 'www/zmslinkcontainer.gif'
            )
        context.registerClass(
            zmslinkelement.ZMSLinkElement,
            permission = 'Add ZMSs',
            constructors = (zmslinkelement.manage_addZMSLinkElementForm, zmslinkelement.manage_addZMSLinkElement),
            icon = 'www/zmslinkcontainer.gif'
            )
        context.registerClass(
            zmslog.ZMSLog,
            permission = 'Add ZMSs',
            constructors = (zmslog.manage_addZMSLog, zmslog.manage_addZMSLog),
            )
        context.registerClass(
            _mediadb.MediaDb,
            permission = 'Add ZMSs',
            constructors = (_mediadb.manage_addMediaDb, _mediadb.manage_addMediaDb),
            icon = 'www/acl_mediadb.gif'
            )
        context.registerClass(
            _sequence.Sequence,
            permission = 'Add ZMSs',
            constructors = (_sequence.manage_addSequence, _sequence.manage_addSequence),
            icon = 'www/acl_sequence.gif'
            )
        context.registerClass(
            _zmsattributecontainer.ZMSAttributeContainer,
            permission = 'Add ZMSs',
            constructors = (_zmsattributecontainer.manage_addZMSAttributeContainer, _zmsattributecontainer.manage_addZMSAttributeContainer),
            )
            
        context.registerBaseClass(zms.ZMS)
        
        # automated registration for other Images
        for img_path in ['www/']:
          path = package_home(globals()) + os.sep + img_path
          for file in os.listdir(path):
            filepath = path + os.sep + file 
            mode = os.stat(filepath)[stat.ST_MODE]
            if not stat.S_ISDIR(mode):
              registerImage(filepath,file)
    
    except:
        """If you can't register the product, dump error. 
        
        Zope will sometimes provide you with access to "broken product" and
        a backtrace of what went wrong, but not always; I think that only 
        works for errors caught in your main product module. 
        
        This code provides traceback for anything that happened in 
        registerClass(), assuming you're running Zope in debug mode."""
        
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(traceback.format_exception(type, val, tb), ''))
        del type, val, tb

def registerImage(filepath,s):
  """
  manual icon registration
  """
  icon=ImageFile(filepath,globals())
  icon.__roles__ = None
  OFS.misc_.misc_.zms[s]=icon

################################################################################
