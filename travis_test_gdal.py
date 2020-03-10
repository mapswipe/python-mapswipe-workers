from osgeo import gdal

version_num = int(gdal.VersionInfo("VERSION_NUM"))
print(version_num)
