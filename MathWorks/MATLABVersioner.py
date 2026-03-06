#!/usr/local/autopkg/python


from __future__ import absolute_import

import os
import xml.etree.ElementTree as ET

from autopkglib import Processor, ProcessorError

__all__ = ["VectorworksUpdateVersioner"]


class MATLABVersioner(Processor):
    """This processor determines the version of MATLAB from the 
    VersionInfo.xml file"""

    description = __doc__
    input_variables = {
        "versioninfo_path": {
            "required": True,
            "description": "Path to the VersionInfo.xml file",
        }
    }
    output_variables = {
        "current_version": {"description": "Version of MATLAB"}
    }

    def main(self):
        try:
            xmlPath = self.env["versioninfo_path"]
            
            self.output("Looking at : %s" % xmlPath)

            tree = ET.parse(xmlPath)
            root = tree.getroot()
            found_version = (root[0].text)

            self.output("Found version %s" % found_version)

            self.env["current_version"] = found_version 

        except Exception as err:
            # handle unexpected errors here
            raise ProcessorError(err)


if __name__ == "__main__":
    PROCESSOR = MATLABVersioner()
    PROCESSOR.execute_shell()