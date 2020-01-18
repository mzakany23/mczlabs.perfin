

from perfin.lib.file_matching.util.support import get_s3_perfin_files, generate_new_file_names


if __name__ == '__main__':
    for old_filename, header, rows in get_s3_perfin_files():
        for new_file_name_name, file_key in generate_new_file_names(old_filename, header, rows):
            print(new_file_name_name)
        
