 Noesis python plugin for import/export of Kingdom under Fire 2 2014 hero character models 

 Original KUF2 .d3d9paradata model file veiwer plugin downloaded from Xentax forum, author unknown.
 
 Preview *.vap model file with texture binding by alanm1

 Version 0.1:
 Support  2014 KUF 2 Asia client hero models (in Hero*.pkg files, they are not encrypted).

 ## Credits:
   Luigi Auriemma:  KUF2 2014 pkg file unpack bms script     
  
   The arthor of .d3dparadata model viewer from Xentax forum
  
   Rich Whitehouse: Noesis tools
   
  
## Installation:
   Copy this Noesis .py plugin to Noesis's plugins/python/ directory
   
## Usage:
   Use QuickBMS and kuf2_2014.bms to unpack Hero*.pkg file to their own directory.
   Most *.vap file contains textures and models. Each hero has a .dat file contains model/texture material assignments

 There are 5 hero characters:

 For Gunslinger(Glen):   copy *.dat from Hero3\ to Hero2\ , Use Noesis and browse Hero2 directory for model preview
 For Spellsword(Isabella) copy *.dat from Hero6\ to Hero5\, Use Noesis and browse Hero5 directory for model preview
 Follow same rule to preview the other 3 heroes. 

 The best model file format for exporting to Blender 3D is Noesis gltf format. It adds named prefix to exported files, that allows exporting all body parts to the same destination without texture name conflicting each others. 

 In Blender use File|Import|GLTF 2.0 to import models. Body and limb model have 4 LOD meshes. You can delete the 3 low detail meshes. 

 To get all the supported texture types beyond diffuse and normal map (specular/roughness/colorid?? etc) that came with a character model, export model to fbx format. The supported map type will be written to individual image files.

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/preview1.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/preview2.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/image.png?raw=true)
