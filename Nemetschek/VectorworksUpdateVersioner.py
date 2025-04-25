#!/usr/local/autopkg/python


from __future__ import absolute_import

import os
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["VectorworksUpdateVersioner"]


class VectorworksUpdateVersioner(Processor):
    """This processor uses the Vectorworks Installation Manager app 
    to find the version of the latest update"""

    description = __doc__
    input_variables = {
        "major_version": {
            "required": True,
            "description": "Major version of Vectoworks (e.g., 2025).",
        },
        "install_manager_path": {
            "required": True,
            "description": "Path to the install manager app.",
        }
    }
    output_variables = {
        "update_version": {"description": "Name of the update (e.g., Update2)."}
    }

    def main(self):
        try:
            downloader_cli = self.env["install_manager_path"] + "/Contents/Resources/cli.sh"
            list_updates_command = [downloader_cli,
                            'download',
                            '--ls']
            self.output("Running command : %s" % list_updates_command)
            process = subprocess.run(
                   list_updates_command,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   text=True)
            List = process.stdout.strip()

            high_version = "0"
            for line in List.split("\n"):
                if "Update" in line:
                    version = line[10:]
                    if version > high_version:
                        high_version = version

            self.output("Found update version %s" % high_version)

            self.env["update_version"] = high_version 

        except Exception as err:
            # handle unexpected errors here
            raise ProcessorError(err)


if __name__ == "__main__":
    PROCESSOR = VectorworksUpdateVersioner()
    PROCESSOR.execute_shell()