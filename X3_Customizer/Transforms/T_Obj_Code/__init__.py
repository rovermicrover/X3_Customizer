'''
Obj file edits, broken out due to length.
'''
'''
Some general notes on obj editing:

A group of Russian modders wrote a disassembler for the obj files.
See this thread for a link (maybe with browser security settings turned up): 
https://forum.egosoft.com/viewtopic.php?t=92374.

The obj files contain KC psuedo-assembly code, which is fed to a lower 
level interpreter in the exe. Egosoft has some details on the X2 KC 
available at https://www.egosoft.com/X/questsdk/info/doxygen/index.html, 
which can give a general idea of what is in there.

The assembly is stack oriented, where operations generally pull some number
of items off the stack and put a result back on the stack.

Notepad++ does a reasonable job as a text viewer.
The .asm file can be used for general perusal, though the .out is handy 
for checking stack depth changes to help understand different operations.

'''
from .Complex import _Prevent_Complex_Connectors
from .Complex import Remove_Complex_Related_Sector_Switch_Delay

from .Lasertowers import Hide_Lasertowers_Outside_Radar
from .Lasertowers import Set_LaserTower_Equipment

from .Marines import Set_Max_Marines
from .Marines import Max_Marines_Video_Id_Overwrite
from .Marines import Make_Terran_Stations_Make_Terran_Marines

from .Misc import Stop_GoD_From_Removing_Stations
from .Misc import Disable_Asteroid_Respawn
from .Misc import Allow_Valhalla_To_Jump_To_Gates
from .Misc import Remove_Factory_Build_Cutscene
from .Misc import Keep_TLs_Hired_When_Empty
from .Misc import Preserve_Captured_Ship_Equipment
from .Misc import Force_Infinite_Loop_Detection

from .Music import Disable_Combat_Music
from .Music import Disable_Docking_Music

from .Seta import Adjust_Max_Seta
from .Seta import Adjust_Max_Speedup_Rate
from .Seta import Stop_Events_From_Disabling_Seta

from .Spaceflies import Kill_Spaceflies
from .Spaceflies import Prevent_Accidental_Spacefly_Swarms

# Fill in the default documentation category for the transforms.
# Use a dict copy, since this adds new locals.
for _attr_name, _attr in dict(locals()).items():
    if hasattr(_attr, '_category'):
        _attr._category = 'Obj_Code'
