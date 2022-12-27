# Using GDAL

## What is GDAL and how do I normally install it?

Check out [GDAL's website](https://gdal.org),



## If you work in an ESRI python environment, READ THIS FIRST

### The problem: `ogr2ogr` does not work in an ESRI python environment

[`ogr2ogr`](https://gdal.org/programs/ogr2ogr.html#ogr2ogr) is a great command-line tool for converting between dozens of different geospatial data types. But as of this writing, if you run `ogr2ogr` in the command line while in an ESRI python environment, you will get an [error stating that several DLL files are missing](https://community.esri.com/t5/data-management-questions/ogr2ogr-raises-quot-dll-not-found-quot-error-when/td-p/1206780). As the linked thread explains, this is due to ESRI putting a unique edition of GDAL into its environment that raises the DLL error.

### Workaround: create a new, non-ESRI environment just for GDAL

To use `ogr2ogr`, simply create a new, empty conda environment, then run the appropriate `conda install` command described on [GDAL's installation page](https://gdal.org/download.html#binaries).

## `ogr2ogr` Command Line Tool

[`ogr2ogr`](https://gdal.org/programs/ogr2ogr.html#ogr2ogr) is probably the best-known GDAL tool. You run it in the command line to convert between dozens of different geospatial data types. To use it, enter the command `ogr2ogr [options...]` into the command line. Example conversions you can do:

* Convert an OpenStreetMap (.osm or .pbf) file into a GPKG file (geopackage, kind of an open-source version of an ESRI File Geodatabase) containing the points, lines, polygons, etc as separate GPKG layers: `ogr2ogr -f GPKG output.gpkg input.pbf`
* Convert an OSM file to a shapefile, specifying what parts you want, which CRS you want, etc. There are many, many filtering and configuration options available.

### Calling ogr2ogr in a python script

You can call `ogr2ogr` commands via python's `subprocess` module.