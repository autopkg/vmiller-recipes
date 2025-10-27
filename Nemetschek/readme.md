# Recipes for Nemetschek Vectorworks

## Recipes for Vectorworks 2026 and later

### VectorworksPkg.download.recipe

This recipe downloads the new (as of 2026 release) installer package.  As the package does not have good version information, the version is extracted from the package payload

### VectorworksPkg.munki.recipe

This recipe takes the package downloaded by the download recipe and builds a diskimage with the package and the plist file at the root of the disk image.  The admin must specify the path to a prperly named and formatted plist in the recipe input.  See the [documentation](https://forum.vectorworks.net/index.php?/articles.html/articles/how-to/installation/command-line-installation-of-vectorworks-2026-r945/)


## Recipes for Vectorworks 2025 and later


## VectorworksFullInstaller.download.recipe

This recipe uses the `VectorworksInstallManager.download` recipe from `jazzace-recipes` as a parent.  After the Install Manager app is downloaded it then makes use of a custom processor to invoke the install manager CLI to download the offline payload


## VectorworksInstallManager-pkg.munki.recipe

This recipe uses `VectorworksInstallManager.pkg` recipe from `jazzace-recipes` as omt's parent.  It imports the package into Munki


## VectorworksInstallManager.munki.recipe

This recipe uses `VectorworksInstallManager.download` recipe from `jazzace-recipes` as a parent. The Install Manager app is wrapped in a dmg and imported into Munki with a postinstall script to do the installation.  This recipe relies on the `VersionSplitter` custom processor from `homebysix-recipes` 

## VectorworksFullInstaller.munki.recipe

This recipe requires `VectorworksInstallManager.download` recipe from `jazzace-recipes`, and uses the `VersionSplitter` custom processor from `homebysix-recipes`,  The Install Manager app is downloaded and then used to download the latest Update file.  A dmg is then created with the Install Manager app, the .vwim update file, and the .ldf file provided by the admin.  The resulting dmg is then imported into Munki with a postinstall script to perform the installation.  