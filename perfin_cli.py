import sys
import os
from perfin.util.csv_functions import open_and_yield_csv_row
from perfin.lib.file_matching.analyzer import FileAnalyzer
from cli.prompts import (
    show_cli_message, 
    generate_prompt, 
    RENAME_FILES_TYPE
)



if __name__ == '__main__':
    args = sys.argv

    if len(args) == 4:
        one, two, stage, command = args
    elif len(args) == 3:
        one, two, command = args
    else:
        command = None
    
    commands = ['shell']
    if command and command in commands:
        if command == 'shell':
            print('Opening {} shell...'.format(ENV))
            time.sleep(2)
            import pdb; pdb.set_trace()
    
    show_cli_message()
    action_type = generate_prompt(['action_type'])
    
    if action_type == RENAME_FILES_TYPE:
        report = generate_prompt(['directory'])
        if report == 'custom directory':
            directory = generate_prompt(['custom_directory'])
        else:
            directory = os.path.expanduser(report)
        
        for path in os.listdir(directory):
            filename, file_extension = os.path.splitext(path)
            if file_extension.lower() == '.csv':
                old_filename = '{}/{}'.format(directory, path)
                reader = open_and_yield_csv_row(old_filename)
                header = next(reader, None)
                analyzer = FileAnalyzer(header=header, filename=old_filename)
                new_filename = '{}/{}.csv'.format(directory, analyzer.policy.unique_name)

                print(f'old: {old_filename}')
                print(f'new: {new_filename}')
                print('')
                

