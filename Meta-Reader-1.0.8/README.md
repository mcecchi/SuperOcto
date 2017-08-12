# Meta_Reader

This Plugin Scans all Simplify 3D and Cura Gcode files for metadata and saves it locally to the printer.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/Robo3D/Meta-Reader/archive/master.zip
    
    
# Keywords for Cura 2

```
layer_height_0
;LAYER_COUNT:
sparse_density =
;TIME:
```

# Keywords for cura 15

```
; infill = 
; layer height = 
; time = 
;Layer count: 
```
# Keywords for Simplify 3D

```
;   layerHeight,
; layer 
;   infillPercentage,
;   Build time: ([0-9.]+) hours ([0-9.]+) minutes
```
