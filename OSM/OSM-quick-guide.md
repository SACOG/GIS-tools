# OSM Quick Guide

## NOTE - THIS IS A DRAFT WORK IN PROGRESS

# Help Topics

1. Where to get OSM Data Extracts
2. Converting between OSM native formats and other formats

# OSM Overview

There are lots of resources with in-depth information on what OSM is, so this doc won't go into that. Some good starting points are:

- [OpenStreetMap.org](https://www.openstreetmap.org/)

# Where to get OSM Data Extracts

## Protomaps

Protomaps has a cool tool for specifying and downloading specific areas' OSM data

# Working with OSM Data Extracts

After downloading an OSM data extract, you may want to trim or filter it before working with it. E.g., remove all data except for roads, or only keep points of interest. While there are several tools out there for such tasks, [Osmosis](https://wiki.openstreetmap.org/wiki/Osmosis) is nice because it is cross-platform (Linux, Mac, and Windows) and can do a lot of different things with OSM and PBF.

## Example Osmosis Commands

Convert a PBF (a compressed version of a .OSM) to OSM

`osmosis --read-pbf input.osm.pbf --write-xml output.osm`

Extract only roads from an OSM file originally containing everything (e.g., also buildings, points of interest, administrative boundaries, etc.):

`osmosis --read-xml input.osm --tf accept-ways highway=\* --write-xml output.osm`

# Converting between OSM native formats and other formats

## About OSM Native Format

OSM natively downloads as either .OSM or .PBF, the latter of which is a compressed OSM file. Each OSM file has several key related geographic subcomponents:

1.

## GDAL and OGR2OGR

[GDAL](https://gdal.org/), or GeoData Abstraction Library, is a suite of tools for working with raster and vector spatial data.

[OGR2OGR](https://gdal.org/programs/ogr2ogr.html) is a command-line (or GUI) tool for converting between various types of vector spatial data, such as between OSM and SHP, OSM and JSON, etc.

## Example OGR2OGR commands

### Basic OGR2OGR command structure

Below is the basic OGR2OGR structure that you enter into a command line. There are many options to include, and the complete documentation is in the [OGR2OGR documentation](https://gdal.org/programs/ogr2ogr.html#ogr2ogr)
`ogr2ogr destination_file_path origin_file_path`

### OSM > ESRI Geodatabase and GPKG Geodatabase

Going directly from OSM to an ESRI File Geodatabase (.GDB) is not easy. You either need to get a Data Interoperability license, or you need to get an old (from 2012) SDK. If possible, avoid doing this.

As an alternative to using ESRI's proprietary GDB format, you can instead use a [geopackage, or GPKG](https://www.geopackage.org/), database. GPKGs work in ArcGIS Pro like GDBs do, and can be easily created in OGR2OGR using the following command:
`ogr2ogr -f "GPKG" destination_gpkg_path source_osm_path`

### OSM > shapefile

`ogr2ogr path_to_destination_shp path_from_OSM layer_type`
With `layer_type` potentially being `LINES`, `POINTS`, `POLYGONS` or several other options. See the OGR2OGR documentation for all the options.

### OSM > JSON

Very similar to OSM > shapefile command:
`ogr2ogr path_to_destination_json path_from_OSM layer_type`

## Converting Back to OSM

OGR2OGR does not have any nice clean commands to convert from some non-OSM file (e.g. shapefile, GeoJSON, GPKG, etc.) _to_ an OSM or PBF file.

To create a new OSM file from a non-OSM file or set of files, you must acquire JOSM and install the Open Data plugin for it. Specifically [Download JOSM](https://josm.openstreetmap.de/wiki/Download). Unfortunately documentation is not good on this. We will update this section once we have more information available.

# Automating OSM conversions via python

Coming soon! Our goal is to provide a neater, more user-friendly version of [GDAL's Python API documentation](https://gdal.org/python/)

[General table of what conversions are doable to and from OSM files](https://wiki.openstreetmap.org/wiki/Converting_map_data_between_formats)
