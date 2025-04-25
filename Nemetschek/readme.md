# Recipes for Nemetschek Vectorworks

*Note* these recipes are for Vectorworks 2025 and later


## VectorworksFullInstaller.download.recipe

This recipe uses the `VectorworksInstallManager.download` recipe from `jazzace-recipes` as a parent.  After the Install Manager app is downloaded it then makes use of a custom processor to invoke the install manager CLI to download the offline payload


## VectorworksInstallManager-pkg.munki.recipe

This recipe uses `VectorworksInstallManager.pkg` recipe from `jazzace-recipes` as omt's parent.  It imports the package into Munki


## VectorworksInstallManager.munki.recipe

This recipe uses `VectorworksInstallManager.download` recipe from `jazzace-recipes` as a parent. The Install Manager app is wrapped in a dmg and imported into Munki with a postinstall script to do the installation.  This recipe relies on the `VersionSplitter` custom processor from `homebysix-recipes` 