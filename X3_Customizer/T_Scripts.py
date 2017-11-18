'''
Add new or modified scripts.

Due to difficulty in directly modifying script files, this will focus
on copying over pre-modified scripts where needed, renaming existing
scripts to avoid overwriting them.

This module will include a shared Add_Script transform, and some
convenience transforms for select scripts.
'''
from File_Manager import *
import os
import shutil

# No dependencies here; this only mucks around in the script folder.
@Check_Dependencies()
def Add_Script(
        script_name = None,
        remove = False
    ):
    '''
    Add a script to the addon/scripts folder. If an existing xml version
    of the script already exists, it is overwritten. If an existing pck
    version of the script already exists, it is renamed with suffix
    '.x3c.bak'.

    * script_name:
      - String, the name of the script to add. This should be present
        in the /scripts directory of this program. The name does not
        need to include the '.xml' suffix, though it may.
    * remove:
      - Bool, if True then instead of adding the given script, it will
        be removed if present from a prior transform, and any backed
        up pck version will be restored.
    '''
    # Add the .xml extension if needed.
    if not script_name.endswith('.xml'):
        script_name += '.xml'
        
    # Copy the script to the scripts directory, to make it available.
    # Do this here to share the path with cleanup, which runs early.
    dest_path = os.path.join('scripts', script_name)
    # The pck version would just be the same path with a different
    # extension.
    pck_path = dest_path.replace('.xml', '.pck')
    # The backup pck is similar, with a longer extension.
    pck_backup_path = pck_path + '.x3c.bak'

    # The file is present here in scripts, so can reuse the dest_path.
    this_dir = os.path.normpath(os.path.dirname(__file__))
    source_path = os.path.join(this_dir, dest_path)
    
    # Continue based on if removal is being done or not.
    if not remove:
        
        # Error if the file is not found locally.
        if not os.path.exists(source_path):
            print('Add_Script error: file {} not found at {}.'.format(
                script_name, source_path))
            return

        # Perform the copy of the xml; this overwrites any existing xml
        # version.
        shutil.copy(source_path, dest_path)

        # Check if a pck version exists.
        # If it does, it needs to be renamed to ensure the xml script
        # will get loaded by the game instead of the pck version.
        if os.path.exists(pck_path):
            os.rename(pck_path, pck_backup_path)

    else:
        # Check if the xml file exists from a prior run.
        if os.path.exists(dest_path):
            # Remove the xml file.
            os.remove(dest_path)
            # Check if a backed up pck exists.
            if os.path.exists(pck_backup_path):

                # Something odd if the standard pck also exists.
                if os.path.exists(pck_path):
                    # Print a warning and skip the rename.
                    print('Add_Script warning: when removing file {}, a .pck'
                         'version and a .pck.x3c.bak version were discovered;'
                         'backup restoration will be skipped.'.format(script_name))
                else:
                    # Rename it back to .pck.
                    os.rename(pck_backup_path, pck_path)

    return
    

@Check_Dependencies()
def Disable_OOS_War_Sector_Spawns(
        _cleanup = False
    ):
    '''
    Disables spawning of dedicated ships in the AP war sectors which attack
    player assets when the player is out-of-sector. By default, these ships
    scale up with player assets, and immediately respawn upon being killed.
    This replaces '!fight.war.protectsector'.
    '''
    # Can pass the _cleanup flag straight through as the remove field.
    Add_Script('!fight.war.protectsector', remove = _cleanup)

    
@Check_Dependencies()
def Convert_Attack_To_Attack_Nearest(
        _cleanup = False
    ):
    '''
    Modifies the Attack command when used on an owned asset to instead
    enact Attack Nearest. In vanilla AP, such attack commands are quietly
    ignored. Intended for use when commanding groups, where Attack is 
    available but Attack Nearest is not.
    This replaces '!ship.cmd.attack.std'.
    '''
    Add_Script('!ship.cmd.attack.std', remove = _cleanup)