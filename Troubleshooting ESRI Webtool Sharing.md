# Quick Guide for Publishing ESRI Geoprocessing Services



## Start with ESRI's How-To Guide

This document is more of a troubleshooting guide for publishing ESRI geoprocessing (GP) services. For a basic how-to guide, please check out [ESRI's documentation](https://pro.arcgis.com/en/pro-app/latest/get-started/share-a-web-tool.htm) on it.



## Troubleshooting GP publishing

### Supporting Modules Not Uploading When Publishing

*Details* - you have a main script with some number of supporting scripts, but when you publish, not all of the supporting scripts upload to the server so you get importation errors when running the script online.



*Solution* - Workaround, as of 2/1/2022, is to check and if needed manually move the needed supporting script files over. However this does not address the question of why they do not copy over in the first place.