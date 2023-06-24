# Macrogenerator with no parameters but definitions can be nested.

## General:
The goal of this program is to serve as a macro generator that can
accept macro definitions without any parameters and with possibility of
nested macros. The input has to be provided as a single file and all of
the macro definitions(nested and not nested) have to be properly
closed. The program will firstly add all the macro definitions into the
dictionary and only then resolve all the macro calls. This way the
macro call can be present before its definition and still be resolved
without errors.

