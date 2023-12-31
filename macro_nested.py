import copy
import sys

lexems = []
dictionary = []
output = []


def lexer():
    """
    Performs lexical analysis on the input file and generates a list of lexemes.
    Categorizes the lexemes as macro start, macro end, macro call, or freetext.
    """
    stack = []
    with open(sys.argv[1]) as input:
        for line in input:
            # check if a macro definition
            if line[0] == '&':
                if 2 >= len(line) >= 1:
                    if len(stack) == 0:
                        print('ERROR: MACRO CLOSE STATEMENT WITHOUT OPENING FOUND')
                    else:
                        lexems.append("MACRO.END." + stack.pop()) # Add macro end lexeme to lexems list
                else:
                    if line[-1] == '\n':
                        lexems.append('MACRO.START.' + line[1:-1]) # Add macro start lexeme to lexems list
                        stack.append(line[1:-1]) # Push macro name to stack
                    else:
                        lexems.append('MACRO.START.' + line[1:])
                        stack.append(line[1:])

            # check if a macro call
            elif line[0] == '$': 
                if line[-1] == '\n':
                    lexems.append('MACRO.CALL.' + line[1:-1])
                else:
                    lexems.append('MACRO.CALL.' + line[1:])
            else:
                if line[-1] == '\n':
                    lexems.append('FREETEXT.' + line[:-1])
                else:
                    lexems.append('FREETEXT.' + line[:])

    if len(stack) != 0:
        for definition in stack:
            print('ERROR: DEFINITION OF MACRO WITH NO CLOSE STATEMENT ' + definition)


def parser(lexedFile, context):
    """
    Parses the lexemes to extract macro definitions.
    
    Args:
        lexedFile (list): List of lexemes generated by the lexer.
        context (list): Current context (list of macro names) for nested macros.
    
    Constructs a dictionary of macro definitions based on the lexemes.
    Each entry in the dictionary contains information about the macro's name, nested macro count, context, and content.
    """
    description = []
    defStart = False
    macroName = ''
    numberOfDef = 0

    # Iterate over each lexeme in the lexed file
    for lexem in lexedFile:
        if defStart == True:
            description.append(lexem)
            if lexem[:12] == 'MACRO.START.':
                numberOfDef += 1

        # Check if it's the start of a new macro definition and no previous definition is in progress
        if lexem[:12] == 'MACRO.START.' and defStart == False:
            defStart = True
            macroName = lexem[12:]

            # Check if the macro is being nested within its own context
            for nest in context:
                if macroName == nest:
                    print('ERROR CANNOT NEST A MACRO WITH A')
                    defStart = False

        # Check if it's the end of the current macro definition
        if lexem == 'MACRO.END.' + macroName:
            defStart = False
            macroDescription = {
                'name': macroName,
                'nested': numberOfDef,
                'context': context,
                'content': copy.deepcopy(description[:-1])
            }

            # Check if the same macro already exists in the dictionary
            for definition in dictionary:
                if definition['name'] == macroDescription['name'] and definition['context'] == macroDescription['context']:
                    dictionary.remove(definition)
                    print('Macro "' + macroName + '" has been overwritten')

            dictionary.append(macroDescription)
            numberOfDef = 0     # Reset the count of nested macro definitions
            description.clear()


def add_nested():
    """
    Adds nested macro definitions to the dictionary by recursively parsing the content of each macro.
    """

    # Iterate over each macro in the dictionary
    for macro in dictionary:
        if macro['nested'] != 0:
            tempContext = copy.deepcopy(macro['context'])   # Create a copy of the macro's context
            tempContext.append(macro['name'])
            parser(macro['content'], tempContext)   # Parse the content of the macro with the updated context


def clean_dictionary():
    """
    Removes nested macro definitions from the content of each macro in the dictionary.
    Ensures that macro definitions only contain freetext and non-nested macro calls.
    """
    clean = False
    macroName = ''

    # Iterate over each macro definition in the dictionary
    for definition in dictionary:
        tempContent = copy.deepcopy(definition['content'])  # Create a copy of the macro's content
        cleanedContent = []

        # Iterate over each lexeme in the macro's content
        for lexem in tempContent:
            if lexem[:12] == 'MACRO.START.' and clean == False:
                macroName = lexem[12:]
                clean = True
            if clean == False:
                cleanedContent.append(lexem)
            if lexem == 'MACRO.END.' + macroName:
                clean = False
                macroName = ''
        
        # Update the macro's content with the cleaned content
        definition['content'] = copy.deepcopy(cleanedContent)


def showDictionary():
    """
    Displays the contents of the macro dictionary.
    """
    for definition in dictionary:
        print(definition)


def create_output(lexems, context):
    """
    Generates the final output based on the lexemes and macro definitions.
    Handles freetext, macro starts, and macro calls based on the current context.
    Recursively resolves macro calls by searching for the corresponding macro definition in the dictionary.
    """
    global output
    write = True
    macroName = ''
    callName = ''
    definitionFound = False
    
    # Iterate over each lexeme in the lexems list
    for lexem in lexems:
        if lexem[:12] == 'MACRO.START.' and write == True:
            write = False
            macroName = lexem[12:]

        if lexem[:9] == 'FREETEXT.' and write == True:
            output.append(lexem)

        if lexem[:11] == 'MACRO.CALL.' and write == True:
            tempContext = copy.deepcopy(context)
            callName = lexem[11:]
            nestedCall = False

            for nest in tempContext:
                # Check if the called macro is being called within its own context
                if nest == callName:
                    nestedCall = True

            # Check if it's not a nested call
            if nestedCall == False:
                # until the definition of the called macro is found or no more context remains
                while definitionFound == False:
                    for definition in dictionary:
                        if definition['name'] == callName and definition['context'] == tempContext:
                            definitionFound = True
                            tempContext.append(callName)
                            create_output(definition['content'], tempContext)

                    # Check if the definition is not found and no more context remains
                    if definitionFound == False and len(tempContext) == 0:
                        print('MACRO "' + lexem[11:] +
                              '" has no definition in given context')
                        print(context)
                        break

                    # Check if the definition is not found but more context remains
                    if definitionFound == False and len(tempContext) != 0:
                        tempContext.pop()

            # It's a nested call within the same context            
            else:
                print('MACRO "' + lexem[11:] +
                      '" cannot be called for within its own definition in context:')
                print(context)

        definitionFound = False
        if lexem == 'MACRO.END.' + macroName:
            write = True
            macroName = ''


def write_output(output):
    """
    Writes the contents of the output list to a file named 'output.txt'.
    Each lexeme is written as a line in the file, without the 'FREETEXT.' prefix.
    """
    outputFile = open('output.txt', 'w')
    for lexem in output:
        outputFile.write(lexem[9:] + '\n')


lexer()
parser(lexems, [])
add_nested()
clean_dictionary()
create_output(lexems, [])
write_output(output)