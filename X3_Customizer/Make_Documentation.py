'''
Generate documentation for the customizer.
This will parse the docstrings at the top of X3_Customizer and
for each transform, and write them to a plain text file.

This can generally be called directly as an entry function.


Quick markdown notes, for the readme which will be dispayed on
github, and the main documentation just because:

 -Newlines don't particularly matter. Can break up lines for a text
 file, and they will get joined back together.

 -This is bad for a list of transforms, since they get lumped together,
 so aim to put markdown characters on them to listify them.

 -Adding asterisks at the start of lines will turn them into a list,
 as long as there is a space between the asterisk and the text.

 -Indentation by 4 spaces or 1 tab creates code blocks; try to avoid 
 this level of indent unless code blocking is intentional.

 -Indentation is built into some docstrings, though the only one that
 should matter for the markdown version is x3_customizer. That one needs
 to be carefully adjusted to avoid 4-space chains, including across
 newlines.

 -Triple -,*,_ will place a horizontal thick line. Can be used between
 sections. Avoid dashes, though, since they make whatever is above them
 into a header, unless that is desired.

'''

import X3_Customizer
import Transforms
import File_Manager
import sys, os
from collections import OrderedDict

def Make(args):

    #TODO:
    #Make a variation on the simple doc which has some formatting for
    # the egosoft forum, including code blocks and removing newlines
    # when the next line starts with a lowercase character.

    #Make a list of lines or text blocks to print out.
    doc_lines = []

    #Also include a simple version, which will truncate
    # the transform descriptions, aimed at providing a summary which
    # is suitable for posting.
    #Git appears to expect a README.md file; this can be used to
    # generate that, although one directory up.
    doc_short_lines = []

    #Set the indent type. A single spaces for now.
    #Avoid indenting by 4 unless wanting a code block, for the simple
    # file that gets markdowned.
    indent = ' '

    def Make_Horizontal_Line(include_in_simple = True):
        'Adds a horizontal line, with extra newline before and after.'
        this_line = '\n***\n'
        doc_lines.append(this_line)
        if include_in_simple:
            doc_short_lines.append(this_line)

    def Add_Line(line, indent_level = 0, include_in_simple = True):
        'Add a single line to the files, including any newlines.'
        #Prefix with a number of indents.
        this_line = indent * indent_level + line
        doc_lines.append(this_line)
        if include_in_simple:
            doc_short_lines.append(this_line)

    def Add_Lines(text_block, indent_level = 0, include_in_simple = True):
        '''
        Record a set of lines from text_block, with indent, splitting on
        newlines. May not include all starting or ending newlines, depending
        on behavior of splitlines().
        '''
        for line in text_block.splitlines():
            #Prefix with a number of indents.
            this_line = indent * indent_level + line
            doc_lines.append(this_line)
            if include_in_simple:
                doc_short_lines.append(this_line)


    def Record_Func(function, 
                    indent_level = 0, 
                    end_with_empty_line = True,
                    include_in_simple = True):
        'Adds lines for a function name with docstring.'

        #Get the name as-is.
        #Put an asterix in front for markdown.
        Add_Lines('* ' + function.__name__, indent_level)

        #If there are required files, print them.
        if hasattr(function, '_file_names'):
            #For markdown, don't want this attached to the file name,
            # but also don't want it causing an extra list indent on
            # the docstring. An extra newline and a healthy indent
            # seems to work.
            Add_Lines('\n{}Requires: {}'
                        .format(
                             indent * (indent_level + 1),
                             #Join the required file names with commas.
                             ', '.join(function._file_names)),
                         indent_level +1,
                         include_in_simple)

        Add_Lines(function.__doc__, indent_level +1, include_in_simple)
        #Don't put a newline in the simple version, which will be a
        # quick list of transforms.
        if end_with_empty_line and not include_in_simple:
            doc_lines.append('')


    #Grab the main docstring.
    Add_Lines(X3_Customizer.__doc__)
    
    #Add a note for the simple documentation to point to the full one.
    doc_short_lines.append('\nFull documentation found in Documentation.md.')

    #Grab any setup methods.
    #Skip this for the simple summary.
    Make_Horizontal_Line()
    Add_Line('Setup methods:')
    Add_Line('')
    #For now, just the Set_Path method.
    Record_Func(File_Manager.Set_Path, indent_level = 2,
                include_in_simple = False)
    

    #Put a header for the transform list.
    Make_Horizontal_Line()
    Add_Line('Transform List:')
    Add_Line('')

    #Grab the various transform functions.
    #This can grab every item in Transforms that has been decorated with
    # Check_Dependencies.
    #Pack these into an ordereddict, keyed by a tuple of 
    # (home module name, function name), to enable different 
    # sorting options.
    transform_modules_dict = OrderedDict()
    for item_name in dir(Transforms):
        item = getattr(Transforms, item_name)

        #Check for the _file_names attribute, attached by the decorator.
        if hasattr(item, '_file_names'):
            #Record the transform.
            transform_modules_dict[(item.__module__,item.__name__)] = item
            

    #Could alphabetize these or maybe categorize by the T module they
    # come from.
    #Go with alphabetical on transform name, item[0][1], eg. the
    # key's second field.
    for (module_name, transform_name), transform in sorted(transform_modules_dict.items(),
                                         key = lambda x: x[0][1]):
        #Only record the name for the simple file.
        Record_Func(transform, indent_level = 1, include_in_simple = False)
            

    #Print out the example module as well.
    #The example will accompany the simple version, since it is a good way
    # to express what the customizer is doing.
    Make_Horizontal_Line()
    Add_Line('Example input file, User_Transforms_Example.py:')
    #Need a newline before the code, otherwise the code block
    # isn't made right away (the file header gets lumped with the above).
    Add_Line('')
    with open('User_Transforms_Example.py', 'r') as file:
        #Put in 4 indents to make a code block.
        Add_Lines(file.read(), indent_level = 4)


    #Print out the license.
    #The simple version will skip this.
    Make_Horizontal_Line(include_in_simple = False)
    with open(os.path.join('..','License.txt'), 'r') as file:
        Add_Lines(file.read(), include_in_simple = False)

    #Write out the full doc.
    #Put these 1 directory up to separate from the code.
    with open(os.path.join('..','Documentation.md'), 'w') as file:
        file.write('\n'.join(doc_lines))

    #Write out the simpler readme.
    with open(os.path.join('..','README.md'), 'w') as file:
        file.write('\n'.join(doc_short_lines))

if __name__ == '__main__':
    Make(sys.argv)
    