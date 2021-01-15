import argparse

from file_munging import rename_files
from settings import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser("perfin cli")
    parser.add_argument(
        "-rn", help=f"convert filenames in {config.LOCAL_FILE_DIR}", action="store_true"
    )
    parser.add_argument(
        "-ms3", help=f"move files in {config.LOCAL_FILE_DIR} to s3", action="store_true"
    )
    args = parser.parse_args()

    if args.rn:
        rename_files(config.ACCOUNT_LOOKUP, config.LOCAL_FILE_DIR)
    elif args.ms3:
        # TODO
        # need to upload files to s3
        # need to try and point logstash at the perfin directory
        # should run elk in docker and maybe share/mount the directory?
        pass
