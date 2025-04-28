#!/usr/local/autopkg/python


from __future__ import absolute_import

import os
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["VectorworksUpdateDownloader"]


class VectorworksUpdateDownloader(Processor):
    """This processor uses the Vectorworks Installation Manager app 
    to download the Update file used for offline installs"""

    description = __doc__
    input_variables = {
        "major_version": {
            "required": True,
            "description": "Major version of Vectoworks (e.g., 2025).",
        },
        "install_manager_path": {
            "required": True,
            "description": "Path to the install manager app.",
        },
        "update_version": {
            "required": True,
            "description": "Update version to download"
        }
    }
    output_variables = {
        "downloaded_update_path": {"description": "Path to the update file."},
        "update_name": {"description": "Name of the update (e.g., Update2)."}
    }

    def main(self):
        try:
            downloader_cli = self.env["install_manager_path"] + "/Contents/Resources/cli.sh"
    
            update_target_name = "Update" + self.env["update_version"]
            self.output("Found update target %s" % update_target_name)

            update_dir = self.env["RECIPE_CACHE_DIR"] + "/Update/" + self.env["major_version"]
            update_download_command = [downloader_cli,
                        'download',
                        '--target',
                        update_target_name,
                        '--dest',
                        update_dir]
            download_update_path = update_dir + '/' + update_target_name + '.vwim'

            if not os.path.isfile(download_update_path):
                self.output("Running command  %s" % update_download_command)
                process = subprocess.run(
                        update_download_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True)
            else:
                self.output("Update already exists as : %s" % download_update_path)
            self.env["downloaded_update_path"] = download_update_path
            self.env["update_name"] = update_target_name 

        except Exception as err:
            # handle unexpected errors here
            raise ProcessorError(err)


if __name__ == "__main__":
    PROCESSOR = VectorworksUpdateDownloader()
    PROCESSOR.execute_shell()