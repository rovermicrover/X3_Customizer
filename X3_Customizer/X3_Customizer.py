'''
X3 Customizer v2.01
------------------

This tool will read in source files from X3, perform transforms on them,
and write the results back out.  Transforms will often perform complex
or repetitive tasks succinctly, avoiding the need for hand editing of
source files.  Source files will generally support any prior modding.

This tool is written in Python, and tested on version 3.6.

Usage:
 * "X3_Customizer <user_transform_module.py>"
   - Runs the customizer using the provided module, located in this
     directory, to specify the path to the AP directory, the folder
     containing the source files to be modified, and the transforms
     to be run. See User_Transforms_Example.py for an example.
 * "Make_Documentation.py"
   - Generates documentation for this project.

Setup:
  * Transforms will operate on source files which need to be set up
  prior to running this tool. Source files can be extracted using
  X2 Editor 2 if needed. Source files may be provided after any other 
  mods have been applied.

  * Source files need to be located in a folder underneath the 
  specified AP addon directory, and will have an internal folder
  structure matching that of the files in the normal addon directory.

  * Output files will be generated in the addon directory matching
  the folder structure in the source folder. Non-transformed files
  will generate output files. Files which do not have a name matching
  the requirement of any transform will be ignored and not copied.

  * Warning: Generated output will overwrite any existing files.

  Example directory:

    <path to X3 installation>
        addon
            source_folder
                maps
                    x3_universe.xml
                types
                    TBullets.txt
                    TLaser.txt
                    TShips.txt
                    TShips_backup.txt

   This will write to the following files, overwriting any
   existing ones:

    <path to X3 installation>
        addon
            maps
                x3_universe.xml
            types
                TBullets.txt
                TLaser.txt
                TShips.txt

Change Log:
 * 1.x :
   - Original project development for private use.
 * 2.0 :
   - Restructuring of project for general use, isolating individual
     transforms, separating out transform calls, adding robustness.
     Filling out documentation generation.
 * 2.01:
   - Added beam to bullet conversion.
'''
#Note: the above comment gets printed to the markdown file, so avoid
# having a 4-space indent because text will get code blocked.
#-Need to also avoid this 4-space group across newlines, annoyingly.
#-Spaces in text being put into a list seems okay.
#-In general, check changes in markdown (can use Visual Studio plugin)
# to verify they look okay.

import sys, os
#Load up the file manager.
import File_Manager

def Run(args):
    '''
    Run the customizer.
    This expect a single argument: the name of the .py file to load
    which specifies file paths and the transforms to run.
    '''
    #If only one arg available, it is the autofilled file name,
    # so user gave nothing.
    if len(args) == 1:
        #Print some semi-informative message.
        print('Please provide the name of a transform specification module.')

    elif len(args) > 2:
        print('Error: expecting 1 argument, 2 were given.')

    #Check for a help request.
    elif args[1] == '-help':
        help_lines = [
            '',
            'Usage: X3_Customizer user_transform_module.py',
            '',
            '\tPlease provide the name of a python module in this directory',
            '\twhich will declare the path to the AP directory, the folder ',
            '\tcontaining the source files to be modified, and the transforms ',
            '\tto be run.',
            '\tSee User_Transforms_Example.py for an example.'
            ]
        print('\n'.join(help_lines))

    else:
        #The arg should be a python module.
        #This may include pathing, though is generally not expected to.
        user_module_name = args[1]

        if not user_module_name.endswith('.py'):
            print('Error: expecting the name of a python module, ending in .py.')
      
        #Attempt to load the module.
        #This will kick off all of the transforms as a result.
        import importlib        
        module = importlib.machinery.SourceFileLoader(
            #Provide the name sys will use for this module.
            #Use the basename to get rid of any path, and prefix
            # to ensure the name is unique.
            'user_module_' + os.path.basename(user_module_name), 
            user_module_name
            ).load_module()

    #Run any needed cleanup.
    File_Manager.Cleanup()
        
    #Everything should now be done.
    #Can open most output files in X3 Editor to verify results.
    File_Manager.Write_Files()
    
if __name__ == '__main__':
    Run(sys.argv)

