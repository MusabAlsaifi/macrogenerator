import subprocess
import os

# Define the input and output file names
input_files = ['test'+str(i) for i in range(1, 11)]
output_files = ['act'+str(i) for i in range(1, 11)]

def read_file(file_name):
    """
    read_files the contents of a file and returns the data as a string.
    
    Args:
        file_name (str): Name or path of the file to be read_file.
        
    Returns:
        str: Contents of the file as a string.
    """
    with open(file_name, 'r') as file:
        data = file.read()
    return data

i = 0   # Counter

# Iterate over input files and run the tests
for f in input_files:
    with open(output_files[i]+'.std', "w+") as infile:

        # Run the 'macro_nested.py' script with the current input file as an argument
        # and capture the output in 'output_files[i].std'
        subprocess.run(['python',  './macro_nested.py', './files/'+f+'.input'], stdout=infile)

        # Rename the generated 'output.txt' file to 'output_files[i].out'
        os.system('mv output.txt '+output_files[i]+'.out')

    #Compare the actual output with the expected output
    assert read_file('./files/'+f+'.out') == read_file(output_files[i]+'.out')

    # Compare the standard output with the expected standard output
    assert read_file('./files/'+f+'.std') == read_file(output_files[i]+'.std')
    i += 1

print('End of tests')