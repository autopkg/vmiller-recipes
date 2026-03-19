#!/usr/local/autopkg/python

from __future__ import absolute_import
import subprocess
from autopkglib import Processor, ProcessorError

__all__ = ["VectorworksUpdateVersioner"]


class VectorworksDecryptor(Processor):
    """This processor decrypts the a .bin file from a Vectorworks 
    installer pacakge payload"""

    description = __doc__
    input_variables = {
        "bin_file_path": {
            "required": True,
            "description": "Path to a .bin file to decrypt.",
        },
        "zip_file_path": {
            "required": True,
            "description": "Path to the ouput .zip file"
        }
    }
    output_variables = {
    }



    def main(self):
        # openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:vectorworks -in "$SRCBIN" -out "$ZIPDEST"
        try:
            decrypt_command = ['openssl', 'enc', '-d', \
                    '-aes-256-cbc', '-pbkdf2', '-pass', \
                    'pass:vectorworks', '-in', \
                    self.env["bin_file_path"], '-out', self.env["zip_file_path"]]

            self.output("Running command : %s" % decrypt_command)
            process = subprocess.run(
                   decrypt_command,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   text=True)


        except Exception as err:
            # handle unexpected errors here
            raise ProcessorError(err)


if __name__ == "__main__":
    PROCESSOR = VectorworksDecryptor()
    PROCESSOR.execute_shell()