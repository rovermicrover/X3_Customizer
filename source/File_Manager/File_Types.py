'''
Classes to represent game files.
'''
import os
from Common.Settings import Settings
from collections import OrderedDict, defaultdict
from . import File_Fields
from .File_Paths import *
import xml.etree.ElementTree as ET
from xml.dom import minidom

class Game_File:
    '''
    Base class to represent a source file.
    This may be read from the source folder or a cat/dat pair.
    In either case, this will capture some properties of the file
    for organization purposes.

    Attributes:
    * name
      - String, name of the file, without pathing, and uncompressed.
      - Automatically parsed from virtual_path.
    * virtual_path
      - String, the path to the file in the game's virtual file system,
        using forward slash separators, including name, uncompressed.
      - Does not include the 'addon' folder.
      - This is the same as used in transform requirements and loads.
    * file_source_path
      - String, sys path where the file's original contents were read from,
        either a loose file or a cat file.
      - Mainly for debug checking.
      - None for generated files.
    * modified
      - Bool, if True then this file should be treated as modified,
        to be written out.
      - Files only read should leave this flag False.
      - Pending development; defaults True for now.
    '''
    def __init__(
            s,
            virtual_path,
            file_source_path = None,
        ):
        # Pick out the name from the end of the virtual path.
        s.name = virtual_path.split('/')[-1]
        s.virtual_path = virtual_path
        s.file_source_path = file_source_path
        s.modified = True


    def Get_Output_Path(s):
        '''
        Returns the full path to be used when writing out this file
         after any modifications, including file name, uncompressed.
        This may be placed in an 'addon' folder or a base game folder,
         depending on the file's virtual_path.
        '''
        return Virtual_Path_to_Output_Path(s.virtual_path)
        
        
class XML_File(Game_File):
    '''
    Simple XML file contents holder with encoding and text.

    Attributes:
    * text
      - Raw text for this file.
    * encoding
      - String indicating the encoding type of the xml.
    '''
    def __init__(s, file_binary, **kwargs):
        super().__init__(**kwargs)
        
        # Get the encoding to use, since xml files are sensitive to this.
        s.encoding = s.Find_Encoding(file_binary)
        # Translate to text with this encoding.
        # Note: when using 'open()' to read a file, python will convert
        #  line endings to \n even if they were \r\n. Python strings also
        #  use a bare \n, so doing string searches on file contents
        #  requires the file be normalized to \n. When using bytes.decode,
        #  it does not do newline conversion, so that is done explicitly
        #  here.
        s._text = file_binary.decode(s.encoding).replace('\r\n','\n')

        # -Removed; use text instead of xml.
        ## Parse the xml.
        #xml_tree = xml.etree.ElementTree.parse(file_path)
        #subdict[file_name] = xml_tree

        # Set as unmodified, and rely on transforms to call the appropriate
        #  methods when doing updates (instead of modifying text).
        s.modified = False

            
    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        # For xml, this will be the full XML_File object so that its
        #  text field can be edited.
        return s


    def Get_Text(s):
        '''
        Returns the text for this xml file.
        '''
        return s._text


    def Update_From_Text(s, new_text):
        '''
        Updates this xml file from a text block, likely the original
        text with some edits.
        '''
        s.modified = True
        s._text = new_text


    def Get_XML_Node(s):
        '''
        Return an ElementTree node after parsing the current text
        as xml.
        '''        
        return ET.fromstring(s._text)


    def Update_From_XML_Node(s, element_root):
        '''
        Update the current text from an ElementTree xml node.
        First line will be left unchanged.
        '''
        s.modified = True
        s._text = (s._text.splitlines()[0] + '\n' 
                   + ET.tostring(element_root, encoding = 'unicode'))
        assert s._text.count('<?xml') == 1


    @staticmethod
    def Find_Encoding(file_binary):
        '''
        Tries to determine the encoding to use for reading or writing an
        xml file.
        Returns a string name of the encoding.
        '''
        # Codec is found on the first line. Examples:
        #  <?xml version="1.0" encoding="ISO-8859-1" ?>
        #  <?xml version="1.0" encoding="UTF-8" ?>
        # Getting the encoding right is important for special character
        #  handling, and also ensuring other programs that load any written
        #  file based on the xml declared encoding will be using the right one
        #  (eg. utf-8 wasn't used to write an xml file declared as iso-8859
        #   or similar).

        # Convert binary to text; always treating as utf-8 (since this
        #  seems to be the most reliable, and is generally the default).
        file_text = file_binary.decode('utf-8').replace('\r\n','\n')

        # Get the first line by using split lines in a loop, and break early.
        for line in file_text.splitlines():
            # If there is no encoding specified on the first line, as with
            #  script files, just assume utf-8.
            if not 'encoding' in line:
                return 'utf-8'

            # Just do some quick splits to get to the code string.
            # Split on 'encoding'
            subline = line.partition('encoding')[2]

            # This should now have '="ISO-8859-1"...'.
            # Remove the '='.
            subline = subline.replace('=','')

            # Split on all quotes.
            # This will create a an empty string for text before
            #  the first quote.
            split_line = subline.split('"')

            # There should be at least 3 entries,
            #  [empty string, encoding string, other stuff].
            assert len(split_line) >= 3

            # The second entry should be the encoding.
            encoding = split_line[1]
            # Send it back.
            return encoding
            
        return None


    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''        
        # Open with the right encoding.
        with open(file_path, 'w', encoding = s.encoding) as file:   
            # Just write as raw text.
            file.write(s._text)
            # To be safe, add a newline at the end if there isn't
            #  one, since some files require this (eg. bods) to
            #  be read correctly.
            if not s._text.endswith('\n'):
                file.write('\n')

        #-Removed; use text instead of xml.
        # Let the xml plugin pick the encoding to write out in.
        #xml_tree.write(file_path)


class T_File(Game_File):
    '''
    T file contents holder, as a list of OrderedDict objects.
    Represents files found in the 'types' folder.
    Each OrderedDict represents a separate line.
    Class exists mainly to clarify naming for now, and for any
    future attribute expansion.

    Attributes:
    * text
      - Raw text for this file.
    * line_dict_list
      - List of OrderedDict objects, each holding the labelled 
        contents of a line.
      - This includes all lines, with headers.
    * data_dict_list
      - As above, but only holding lines that have data, skipping 
        headers. This is used for transform editing.
    '''
    def __init__(s, file_binary, **kwargs):
        super().__init__(**kwargs)
        s.text = None
        s.line_dict_list = []
        s.data_dict_list = []
                
        # Field ordering could be done with named tuples, but in practice
        #  it is  probably easiest to just use ordered dicts.
        # Indices without names will be keyed by the index integer.

        # Get the file text. Treat as default utf-8.
        # Store a copy of raw text, in case it is ever wanted anywhere.
        # General expectation is that this isn't used, except maybe
        #  in making patches from pre-modified files.
        s.text = file_binary.decode().replace('\r\n','\n')
        
        # This gets a list of lines, where each line is a list of strings.
        # Read in the data lines into a list of lists.
        # Sublists are a series of text strings.
        # Since lines end in semicolons, the last entry will generally 
        #  be a simple new line.
        data_list_list = []
        # Keep line endings when splitting (True arg to splitlines).
        for line in s.text.splitlines(True):
            # Comment lines (//) are ignored.
            if line.startswith('//'):
                continue
            # Split the entries.
            data_list_list.append(line.split(';'))
            

        # Lookup the fields for this file name.
        field_dict = File_Fields.T_file_name_field_dict_dict[s.name]

        # Loop over the lines, aiming to annotate the entries with field
        #  names.
        for data_list in data_list_list:

            # Create an ordered dict for this line to hold the fields.
            this_dict = OrderedDict()

            # Note: the line may be a TC format or AP format, in the
            #  case of the jobs file.
            # If the fields_dict specifies a line count for an AP
            #  format, and that format is seen here, it will provide
            #  some special insertion points for new AP fields.
            # The default field_dict is for the TC format in this
            #  case, with no extra lines.
            # (This is inside the loop, so it gets triggered on the first
            #  data line which has a length matching an AP file).
            if ('lines_ap' in field_dict
            and len(data_list) == field_dict['lines_ap']):
                # Switch to the ap field dict.
                # This will only swap once; afterward there is no
                #  'lines_ap' field in field_dict, and these checks
                #  are skipped.
                field_dict = File_Fields.T_file_name_field_dict_dict[
                    field_dict['ap_name']]
                        

            # Step through the fields, with an index counter.
            for index, field_string in enumerate(data_list):

                # If this index has a field name, use it, otherwise use 
                #  the index for a key.
                this_key = index
                # Only do the named key check when the line is considered
                #  a data line; don't do this for headers/comments.
                if len(data_list) >= field_dict['min_data_entries']:
                    if index in field_dict:
                        this_key = field_dict[index]
                    # Also check negative indices.
                    negative_index = index - len(data_list)
                    if negative_index in field_dict:
                        this_key = field_dict[negative_index]
                        # Error if both matched; something went wrong in that
                        #  case.
                        assert index not in field_dict

                # Record in the ordered dict.
                # Values will not be converted to ints, since some might 
                #  need to stay strings.
                # Int conversion should happen upon use elsewhere.
                this_dict[this_key] = field_string
                                

            # Add this line dict to the list that tracks all lines.
            s.line_dict_list.append(this_dict)
            # Conditionally add this line dict to the data tracking list,
            #  skipping if the line is too short.
            if len(this_dict) >= field_dict['min_data_entries']:
                s.data_dict_list.append(this_dict)


    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        # For T files, this is the list of line dicts with data, which can
        #  be edited directly.
        return s.data_dict_list
    

    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''
        # Open the file to write to.
        with open(file_path, 'w') as file:
            # Loop over the lines.
            for line_dict in s.line_dict_list:

                # Convert the line fields to a list.
                field_list = line_dict.values()
                # Join with semicolons.
                this_line = ';'.join(field_list)

                # Write to the file.
                # The last entry of each sublist is alrady a new line, so
                #  no new line needed here.
                file.write(this_line)

                
    def Add_Entries(s, new_entry_list):
        '''
        Convenience function to add new lines to a t file.

        * new_entry_list
          - List of OrderedDict entries matching the tfile's line format.
        '''
        # Return early if the list is empty.
        if not new_entry_list:
            return

        # All new entries will be put at the bottom of the tfile dict_list.
        # This will require that the header be modified to account for the
        #  new lines.

        # Set how many columns are expected in the header line, based on
        #  the t file name, along with which column/index holds the
        #  entry counter.
        # Error when a new t file seen; this somewhat has to be done
        #  manually.
        if s.virtual_path == 'types/TShips.txt':
            header_columns = 3
            index_with_count = 1
        elif s.virtual_path == 'types/TFactories.txt':
            header_columns = 3
            index_with_count = 1
        elif s.virtual_path == 'types/Globals.txt':
            header_columns = 2
            index_with_count = 0
        elif s.virtual_path == 'types/WareLists.txt':
            header_columns = 2
            index_with_count = 0
        else:
            raise Exception()

        # Add the new entries.
        # These need to go in both the data and line lists, data for future
        # visibility to this and other transforms, lines to be seen at
        # writeout.
        s.data_dict_list += new_entry_list
        s.line_dict_list += new_entry_list

        # Find the header line.
        for line_dict in s.line_dict_list:
            
            # To normalize handling when the dict could have indexed or named
            # keys, pull out the first key (for comment checks) and the key
            # with the counter.
            keys = list(line_dict.keys())
            first_key, count_key = keys[0], keys[index_with_count]

            # Looking for the first non-comment line; it should have
            # header_columns entries (with newline).
            if (not line_dict[first_key].strip().startswith('/') 
            and len(line_dict) == header_columns):
                # The second field is the entry count, to be updated.
                line_dict[count_key] = str(int(line_dict[count_key]) 
                                                  + len(new_entry_list))
                # Can stop looping now.
                break

            # Error if hit a data line.
            if line_dict is s.data_dict_list[0]:
                raise Exception()

        return


class Obj_File(Game_File):
    '''
    Obj file contents holder.
    These are binary files holding KC assembly level code.
    '''
    def __init__(s, file_binary, **kwargs):
        super().__init__(**kwargs)
        # Expecting a bytearray input, not bytes (which are immutable
        #  and more annoying to edit).
        assert isinstance(file_binary, bytearray)
        s.binary = file_binary

    def Read_Data(s):
        'Return the contents to be sent for Load_File requests.'
        # For obj, this will be the full Obj_File object so that its
        #  binary field can be edited.
        return s
    

    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''
        # Do a binary write.
        with open(file_path, 'wb') as file:
            file.write(s.binary)


class Misc_File(Game_File):
    '''
    Generic container for misc file types transforms may generate.
    This will only support file writing.

    Attributes:
    * text
      - String, raw text for the file. Optional if binary is present.
    * binary
      - Bytes object, binary for this file. Optional if text is present.
    '''
    def __init__(s, text = None, binary = None, **kwargs):
        super().__init__(**kwargs)
        s.text = text
        s.binary = binary
        

    def Write_File(s, file_path):
        '''
        Write these contents to the target file_path.
        '''
        if s.text != None:
            # Do a text write.
            with open(file_path, 'w') as file:
                # To be safe, add a newline at the end if there isn't
                #  one, since some files require this (eg. bods) to
                #  be read correctly.
                file.write(s.text)
                if not s.text.endswith('\n'):
                    file.write('\n')
        elif s.binary != None:
            # Do a binary write.
            with open(file_path, 'wb') as file:
                file.write(s.binary)


#-Removed for now; this would need to be paired up with something
# the loads the text (eg. a script) and override other text being
# replaced, and it might be easier for now just to do direct
# edits.         
#class Page_Text_File(Game_File):
#    '''
#    A file to be placed in the addon/t folder, defining text strings.
#    Preferably, all override or new text strings should share this one file,
#    which the game will automatically use to override strings in other files.
#
#    Pending development to read in such files.
#
#    Attributes:
#    * page_id_string_dict
#      - Two layer dict; outer key is text page number, inner key is
#        line number, and value is the string.
#    '''
#    def __init__(self, **kwargs):
#        super().__init__(**kwargs)
#        self.page_id_string_dict = defaultdict(dict)
#        # Can treat as unmodified unless an item is added.
#        self.modified = False
#
#
#    def Add_Line(self, page, line, value):
#        '''
#        Record a new string at the given page and item id.
#        '''
#        self.page_id_string_dict[page][line] = value
#        # Set modified, so this gets written out.
#        self.modified = True
#
#
#    def Read_Data(self):
#        '''
#        Returns self instead of captured data.  Use Add_Line to add
#        or change entries.
#        '''
#        return self
#
#
#    def Write_File(self, file_path):
#        '''
#        Encode these contents into xml and write to the file_path.
#        '''
#        # Output format should look like:
#        # <?xml version="1.0" encoding="UTF-8"?>
#        # <language id="44">
#        # 	<page id="7778">
#		#     <t id="61000">some string</t>
#	    #   </page>
#        # </language>
#
#        # Could do xml nodes, but raw strings is probably fine.
#        output_lines = [
#            '<?xml version="1.0" encoding="UTF-8"?>',
#            '<language id="44">',
#            ]
#
#        # Work through the pages and lines, sorted.
#        for page, line_string_dict in sorted(self.page_id_string_dict.items()):
#
#            # Open the page node.
#            output_lines.append('  <page id="{}">'.format(page))
#
#            # Fill in the lines.
#            for line, string in sorted(line_string_dict.items()):
#                output_lines.append('    <t id="{}">{}</t>'.format(
#                    line, string))
#
#            # Close the page node.
#            output_lines.append('  </page>')
#        
#
#        # Close the language node.
#        output_lines += [
#            '</language>',
#            ]
#        
#        # Open with the right encoding; match utf-8 used in the
#        #  xml header.
#        with open(file_path, 'w', encoding = 'utf-8') as file:
#
#            # Write the lines.
#            file.write('\n'.join(output_lines))
#
#            # To be safe, add a newline at the end.
#            file.write('\n')
#
#        return