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

### OSM > ESRI Geodatabase

### OSM > shapefile

`ogr2ogr path_to_destination_shp path_from_OSM layer_type`
With `layer_type` potentially being `LINES`, `POINTS`, `POLYGONS` or several other options. See the OGR2OGR documentation for all the options.

### OSM > JSON

Very similar to OSM > shapefile command:
`ogr2ogr path_to_destination_json path_from_OSM layer_type`
