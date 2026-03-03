# MathWorks MATLAB recipes

For both of these recipes, the MATLAB installation files must be downloaded from MathWorks first before running wither recipe.  Additionally a properly formatted isntaller input text file must be provided.

Versioning is provided by parsing the `VersionInfo.xml` 

## Inputs

To run either of these recipes you must override the following keys :

* DLPATH : The path to the files downloaded from MathWorks
* INPUT_FILE_NAME : The name of the installer input file
* INPUT_FILE_PATH : The path to the directory containing the installer input file
* RELEASE_VERSION : Marketing release of MATLAB i.e. R2025b


## MATLAB.pkg.recipe

This recipe builds an installer package to copy the MATLAB installation files and the installer input text file to `/tmp/MATALAB_Install` The package includes a postinstall script to run the MATLAB installer.

Example run overriding the keys on the command line:

`autopkg run MATLAB.pkg -k DLPATH="/Users/myuser/Downloads/MathWorks/R2025b" -k INPUT_FILE_NAME="installer_input.txt" -k INPUT_FILE_PATH="matlab_files/" -k RELEASE_VERSION="R2025b"`


## MATLAB.munki.recipe

This recipe builds a disk image containing the provided MATLAB installation files and installer input file.  It then leverages Munki's copy from dmg installer type to copy the files to `/tmp` and uses a `postinstall_script` to do the installation.  This uses Munki 7's `version_script` to determine installation state

Example run overriding the inputs at the command line :

`autopkg run MATLAB.munki -k DLPATH="/Users/myuser/Downloads/MathWorks/R2025b" -k INPUT_FILE_NAME="installer_input.txt" -k INPUT_FILE_PATH="matlab_files/" -k RELEASE_VERSION="R2025b"`