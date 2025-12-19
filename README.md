 Noesis python plugin for import/export of Kingdom under Fire 2 2014 hero character models 

 Original KUF2 .d3d9paradata model file veiwer plugin downloaded from Xentax forum, author unknown.
 
 Preview *.vap model file with texture binding by alanm1

 Version 0.1: Support 2014 KUF 2 Asia client hero models (in Hero*.pkg files, they are not encrypted).
 
 Version 0.2: Add support for full character display and switching body part
 
 ## Credits:
   Luigi Auriemma:  KUF2 2014 pkg file unpack bms script     
  
   The arthor of .d3dparadata model viewer from Xentax forum
  
   Rich Whitehouse: Noesis tools
   
   Ekey: KUF2.PKG.Tool - Use his PkgHash function to match descriptive file name to unpacked .vap file
## Installation:
   Copy both fmt_kuf2_d3d9_vap.py and KUF2FileNames.txt to "Noesis"/plugins/python/ directory    
   
## Usage:
   Use QuickBMS and kuf2_2014.bms to unpack Hero*.pkg file to their own directory.
   Most *.vap file contains texture and model. Each hero has a .dat file contains model/texture assignment

 There are 5 Heroes type:

 For Gunslinger(Glen):      copy Hero3\\\*.dat and repo's full_char\\\*.ksw to Hero2\\, use Noesis and browse Hero2 directory for model preview
 
 For Spellsword(Isabella)  copy Hero6\\\*.dat and repo's full_char\\\*.ksw to Hero5\\, use Noesis and browse Hero5 directory for model preview
 
 Oliver  :                 copy Hero9\\\*.dat and repo's full_char\\\*.ksw to Hero8\\,  browse hero8
 
 Regnier  :                copy Hero12\\\*.dat and repo's full_char\\\*.ksw to Hero11\\,  browse hero11
 
 Regnier-test  :           copy Hero15\\\*.dat and repo's full_char\\\*.ksw to Hero14\\,  browse hero14

 To display full character:
 
 - In Noesis: double-click on _000_full_character.ksw file. It takes a few seconds to load a full character so be patient.
     
 - A kuf2_char_config.txt file will be created in the same directory as the *.vap file to record character configuration. It will be updated whenever double-clicking on a .ksw file to switch body part.       
 
 - Double click on one of the _NUMBER_CHAR-PART.ksw file to cycle through the options for a body part. It takes a few seconds to reload the changed models.
     
 - Not all character have face/head/earring accessory, those *_acc.ksw do not have any effect for some characters.
     
 - When a desired combination of character option is display in preview window, use Noesis "File|Export from Preview" menu to export character.

 - Models may not look smooth in preview due to there are 4 level of detail (LOD) meshes overlaping. Delete the 3 low detail meshes after model imported into Blender3D.

 The best model file format for exporting to Blender 3D is Noesis gltf format. It adds named prefix to exported files, that allows exporting all body parts to the same destination without texture name conflicting each others. 

 In Blender use File|Import|GLTF 2.0 to import models. Body and limb model have 4 LOD meshes. You can delete the 3 low detail meshes. 

 To get all the supported texture types beyond diffuse and normal map (specular/roughness/colorid?? etc) that came with a character model, export model to fbx format. The supported map type will be written to individual image files.

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/preview1.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/preview2.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/character_customization.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/glenn.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/regnier.png?raw=true)

![alt text](https://github.com/alanm20/KUF2_2014_vap/blob/main/images/image.png?raw=true)
