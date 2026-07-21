#!/usr/local/autopkg/python
#
# Copyright 2026 Vaughn Miller 
# modified from MunkiImporter processor by Greg Neagle 2013
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for MunkiImporter class"""

import os
import plistlib
import subprocess
from datetime import datetime

from autopkglib import Processor, ProcessorError
from autopkglib.munkirepolibs.AutoPkgLib import AutoPkgLib
from autopkglib.munkirepolibs.MunkiLib import MunkiLib

__all__ = ["MunkiNopkgImporter"]


class MunkiNopkgImporter(Processor):
    """Imports a nopkg item into the Munki repo."""

    description = __doc__
    lifecycle = {"introduced": "2.9.0"}
    input_variables = {
        "MUNKI_REPO": {
            "required": True,
            "description": "Path to a mounted Munki repo.",
        },
        "MUNKI_REPO_PLUGIN": {
            "required": False,
            "description": (
                "Munki repo plugin. Defaults to FileRepo. Munki must be installed and available "
                " at MUNKILIB_DIR if a plugin other than FileRepo is specified."
            ),
            "default": "FileRepo",
        },
        "MUNKILIB_DIR": {
            "required": False,
            "description": (
                "Directory path that contains munkilib. Defaults to /usr/local/munki"
            ),
            "default": "/usr/local/munki",
        },
        "force_munki_repo_lib": {
            "required": False,
            "description": (
                "When True, munki code libraries will be utilized when the FileRepo plugin is "
                "used. Munki must be installed and available at MUNKILIB_DIR"
            ),
            "default": False,
        },
        "repo_subdirectory": {
            "required": False,
            "description": (
                "The subdirectory under pkgs to which the item "
                "will be copied, and under pkgsinfo where the pkginfo will "
                "be created."
            ),
        },
        "pkginfo": {
            "required": True,
            "description": ("Dictionary of pkginfo keys to copy to generated pkginfo."),
        },
        "force_munkiimport": {
            "required": False,
            "description": (
                "If not False or Null, causes the pkg/dmg to be "
                "imported even if there is a matching pkg already in the "
                "repo."
            ),
        },
        "additional_makepkginfo_options": {
            "required": False,
            "description": (
                "Array of additional command-line options that will "
                "be inserted when calling 'makepkginfo'."
            ),
        },
        "MUNKI_PKGINFO_FILE_EXTENSION": {
            "required": False,
            "description": "Extension for output pkginfo files. Default is 'plist'.",
            "default": "plist",
        },
        "metadata_additions": {
            "required": False,
            "description": (
                "A dictionary that will be merged with the pkginfo _metadata.  "
                "Unique keys will be added, but overlapping keys will replace "
                "existing values."
            ),
        },
    }
    output_variables = {
        "pkginfo_repo_path": {
            "description": (
                "The repo path where the pkginfo was written. "
                "Empty if item not imported."
            )
        },
        "munki_info": {
            "description": "The pkginfo property list. Empty if item not imported."
        },
        "munki_repo_changed": {"description": "True if item was imported."},
        "munki_importer_summary_result": {
            "description": "Description of interesting results."
        },
    }

    def _fetch_repo_library(
        self,
        munki_repo,
        munki_repo_plugin,
        munkilib_dir,
        repo_subdirectory,
        force_munki_lib,
    ):
        if munki_repo_plugin == "FileRepo" and not force_munki_lib:
            return AutoPkgLib(munki_repo, repo_subdirectory)
        else:
            return MunkiLib(
                munki_repo, munki_repo_plugin, munkilib_dir, repo_subdirectory
            )

    def _find_matching_pkginfo(self, repo_library, pkginfo):
        """Looks through all catalog for items matching the one
        described by pkginfo. Returns a list of matching items if found."""

        pkgdb = repo_library.make_catalog_db()
        if "version" in pkginfo:
            for item in pkgdb["items"]:
                if item["name"] == pkginfo["name"]:
                    if item["version"] == pkginfo["version"]:
                        # We have a match
                        return [item]

        # if we get here, we found no matches
        return None

    def main(self) -> None:
        library = self._fetch_repo_library(
            self.env["MUNKI_REPO"],
            self.env["MUNKI_REPO_PLUGIN"],
            self.env["MUNKILIB_DIR"],
            self.env.get("repo_subdirectory"),
            self.env["force_munki_repo_lib"],
        )

        self.output(f"Using repo lib: {library.__class__.__name__}")
        self.output(f'        plugin: {self.env["MUNKI_REPO_PLUGIN"]}')
        self.output(f'          repo: {self.env["MUNKI_REPO"]}')

        # clear any pre-existing summary result
        if "munki_importer_summary_result" in self.env:
            del self.env["munki_importer_summary_result"]
        # Generate arguments for makepkginfo.
        args = ["/usr/local/munki/makepkginfo", "--nopkg"]
        if self.env.get("additional_makepkginfo_options"):
            args.extend(self.env["additional_makepkginfo_options"])

        # Call makepkginfo.
        try:
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False
            )
            out, err_out = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                f"makepkginfo execution failed with error code {err.errno}: "
                f"{err.strerror}"
            )
        if err_out:
            for err_line in err_out.decode().splitlines():
                self.output(err_line)
        if proc.returncode != 0:
            raise ProcessorError(
                f"creating pkginfo for {self.env['pkg_path']} failed: "
                f"{err_out.decode()}"
            )

        # Get pkginfo from output plist.
        pkginfo = plistlib.loads(out)

        # copy any keys from pkginfo in self.env
        if "pkginfo" in self.env:
            for key in self.env["pkginfo"]:
                value = self.env["pkginfo"][key]
                # Special handling: if key is force_install_after_date and value is a str with 'Z' at end, convert to naive datetime
                if (
                    key == "force_install_after_date"
                    and isinstance(value, str)
                    and value.endswith("Z")
                ):
                    try:
                        # Pull 'Z' off end, read string representation as naive/no-timezone-related datetime
                        datetime_obj = datetime.strptime(
                            value[:-1], "%Y-%m-%dT%H:%M:%S"
                        )
                        # When being written out later, the serialization of a date is always ISO8601 w/Z
                        pkginfo[key] = datetime_obj
                    except Exception:
                        pkginfo[key] = value  # fallback to string if parsing fails
                else:
                    pkginfo[key] = value

        # copy any keys from metadata_additions
        if "metadata_additions" in self.env:
            pkginfo["_metadata"].update(self.env["metadata_additions"])

        # set an alternate version_comparison_key
        # if pkginfo has an installs item
        if "installs" in pkginfo and self.env.get("version_comparison_key"):
            for item in pkginfo["installs"]:
                if not self.env["version_comparison_key"] in item:
                    raise ProcessorError(
                        "version_comparison_key "
                        f"'{self.env['version_comparison_key']}' could not be "
                        f"found in the installs item for path '{item['path']}'"
                    )
                item["version_comparison_key"] = self.env["version_comparison_key"]

        # check to see if this item is already in the repo
        if self.env.get("force_munkiimport"):
            matchingitems = None
        else:
            matchingitems = self._find_matching_pkginfo(library, pkginfo)
            self.output(matchingitems)
            if not matchingitems == None:
                self.env["munki_info"] = {}
                self.env["munki_repo_changed"] = False
                self.output(
                    f"Item {self.env['pkginfo']['name']} version {self.env['pkginfo']['version']} already exists in the "
                    f"munki repo "
                )            
                return


        # import pkginfo
        pkginfo_path = library.copy_pkginfo_to_repo(
            pkginfo, self.env.get("MUNKI_PKGINFO_FILE_EXTENSION", "plist")
        )
        pkginfo_prefix = os.path.join(library.munki_repo, "pkgsinfo")
        pkg_prefix = os.path.join(library.munki_repo, "pkgs")

        self.env["pkginfo_repo_path"] = pkginfo_path

        self.env["munki_info"] = pkginfo
        self.env["munki_repo_changed"] = True
        self.env["munki_importer_summary_result"] = {
            "summary_text": "The following new items were imported into Munki:",
            "report_fields": [
                "name",
                "version",
                "catalogs",
                "pkginfo_path",
            ],
            "data": {
                "name": pkginfo["name"],
                "version": pkginfo["version"],
                "catalogs": ",".join(pkginfo["catalogs"]),
                "pkginfo_path": os.path.relpath(
                    self.env["pkginfo_repo_path"], pkginfo_prefix
                ),
            },
        }

        self.output(f'Copied pkginfo to: {self.env["pkginfo_repo_path"]}')


if __name__ == "__main__":
    PROCESSOR = MunkiImporter()
    PROCESSOR.execute_shell()
