#Noesis Python model import+export test module, imports/exports some data from/to a made-up format

# Original KUF2 .d3d9parmetric model file veiwer plugin. Xentax forum, author unknown.
# 
# Preview *.vap model file with texture binding by alanm1
#
# Credits:
#       Luigi Auriemma:  KUF2 2014 pkg file unpack bms script     
#       The arthor of .d3dparametric model viewer. from Xentax
#       Rich Whitehouse: Noesis developer
#       Ekey's KUF2.PKG.Tool: Use his PkgHash function to match descriptive file name to unpacked .vap file
#   
# Version 0.1:
# Support  2014 KUF 2 Asia client hero models (in Hero*.pkg files, they are not encrypted).
# Version 0.2:
# Add support for full character display and switching body parts
#  
# Installaion:
#   Copy both fmt_kuf2_d3d9_vap.py and KUF2FileNames.txt to "Noesis"/plugins/python/ directory    
#
# Usage:
#   Use QuickBMS and kuf2_2014.bms to unpack Hero*.pkg file to their own directory.
#   Most *.vap file contains texture and model. Each hero has a .dat file contains model/texture assignment
#
# There are 5 Heroes type:
#
# For Gunsliger(Glen):      copy Hero3\*.dat and repo's full_char\*.ksw to Hero2\ , Use Noesis and browse Hero2 directory for model preview
# For Spellsword(Isabella)  copy Hero6\*.dat and repo's full_char\*.ksw to Hero5\, Use Noesis and browse Hero5 directory for model preview
# Oliver  :                 copy Hero9\*.data and repo's full_char\*.ksw to Hero8\,  browse hero8
# Regnier  :                copy Hero12\*.data and repo's full_char\*.ksw to Hero11\,  browse hero11
# Regnier-test  :           copy Hero15\*.data and repo's full_char\*.ksw to Hero14\,  browse hero14
#
# To display full character : 
#     In Noesis: double-click on _000_full_character.ksw file. It takes a few seconds to load a full character so be patient.
#     A kuf2_char_config.txt file will be created in the same directory as the *.vap file. It will be updated whenever double-clicking on a .ksw file to switch body part.
#       
#     Double click on one of the _<number>_<part name>.ksw file to cycle through the options for a body part. Tt takes a few seconds to reload character.
#     Not all character have face/head/earring accessories support, those *_acc.ksw do not have any effect for some characters.
#     When a desired combination of character option is display in preview window, use Noesis "File|Export from Preview" menu to export character.
#     Models may not look smooth in prview due to there are 4 level of detail (LOD) meshes overlaping. Delete the 3 low detail meshes after model import into Blender3D.
#                            
# The best model file format for exporting to Blender 3D is Noesis gltf format. It adds named prefix to exported files.

from inc_noesis import *

import noesis

#rapi methods should only be used during handler callbacks
import rapi

import glob
#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
    handle = noesis.register("Kingdom Under Fire II 2014-vap", ".vap")
    noesis.setHandlerTypeCheck(handle, KUF2d3d9CheckType)
    noesis.setHandlerLoadModel(handle, KUF2d3d9LoadModel) #see also noepyLoadModelRPG
    # A special file that load complete character for previewing
    handle = noesis.register("Kingdom Under Fire II 2014-model switch", ".ksw")
    noesis.setHandlerTypeCheck(handle, KUF2SwitchCheckType)
    noesis.setHandlerLoadModel(handle, KUF2SwitchModel)  
    #noesis.logPopup()
    #print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
    return 1



#check if it's this type based on the data
def KUF2d3d9CheckType(data):
    bs = NoeBitStream(data)
    if len(data) < 8:
            return 0
    if bs.readInt() != 1:
        return 0
    return 1       

def KUF2SwitchCheckType(data):
    return 1

def AddAlpha(diffuse,mask):
    for i in range(0,len(diffuse),4):
        diffuse[i+3]=mask[i]

def setModelMaterial2(m_name,m_hash,mesh_hash_map,hash_list,map_type,mat_map,rgb_map, rgb_lookup_map, rgb_list,data,matNames,matList):            
    index = data.find(m_hash)
    #print ("=======For mesh",m_hash)
    diffuse_id=normal_id=spec_id=''   
    
    if m_hash in mesh_hash_map:
        for t_hash_key in mesh_hash_map[m_hash]:            
            t_hash = t_hash_key[:8]
            material_id = t_hash_key[8:10]
            #h = ''.join(format(byte, '02x') for byte in material_id)
            #t_h = ''.join(format(byte, '02x') for byte in t_hash)
            #print ("for material id",h,t_h)

            if t_hash_key in mat_map:  # Is this mesh's diffuse hash in material map.
                n_hash,s_hash= mat_map[t_hash_key]
               
                if n_hash in map_type: # normal map
                    rgb_hash = n_hash       # try to convert internal hash to texture hash
                    while rgb_hash in rgb_lookup_map:                        
                        #h = ''.join(format(byte, '02x') for byte in rgb_hash)
                        #print (" mapping ",h )
                        rgb_hash, rgb_type = rgb_lookup_map[rgb_hash]
                        #h = ''.join(format(byte, '02x') for byte in rgb_hash)
                        #t_h = ''.join(format(byte, '02x') for byte in rgb_type)
                        #print (" to ",h," ", t_h)                        
                        if rgb_hash in map_type:
                            map_type[n_hash] = map_type[rgb_hash]  # update mapping

                if t_hash not in map_type:  # diffuse map
                    rgb_hash = t_hash       # try to convert internal hash to texture hash
                    while rgb_hash in rgb_lookup_map:                        
                        #h = ''.join(format(byte, '02x') for byte in rgb_hash)
                        #print (" mapping ",h )
                        rgb_hash, rgb_type = rgb_lookup_map[rgb_hash]
                        #h = ''.join(format(byte, '02x') for byte in rgb_hash)
                        #t_h = ''.join(format(byte, '02x') for byte in rgb_type)
                        #print (" to ",h," ", t_h)                        
                    if rgb_hash in map_type:
                        map_type[t_hash] = map_type[rgb_hash]  # update mapping

                if t_hash in map_type:  # map_type  convert texture hash to texture id
                    diffuse_id = map_type[t_hash][0]                                       
                    if n_hash in map_type:
                        normal_id= map_type[n_hash][0]
                    #print ("Found diffuse map",t_hash,n_hash,diffuse_id,normal_id)    
                    break  
                else:
                    pass #print ("diffuse not found in map_type", h)
            else:
                pass #h = ''.join(format(byte, '02x') for byte in t_hash_key)
                #print ("diffuse not in mat_map!!!!,key",h)
                        
    # diffuse texture is required for material
    if diffuse_id:  
        MatName="Mat_"+ diffuse_id
        if not MatName in matNames: # new materail
                #print("material", MatName, diffuse_id)
                mat = NoeMaterial(MatName,diffuse_id) # diffuse with alpha
                if normal_id:  # Add normal if exists                            
                    mat.setNormalTexture(normal_id)                                    
                matNames.append(MatName)
                matList.append(mat)
        rapi.rpgSetMaterial(MatName)
    else:
        rapi.rpgSetMaterial("") 

def parseMaterial(mat_map,rgb_map,rgb_lookup_map,mesh_hash_map, data):
    param="Unnamed color"
    index = data.find(b'\x17\x00\x00\x00'+param.encode('ASCII'))
    i =0
    if index != -1:
        while data[index:index+4] == b'\x17\x00\x00\x00':  # skip unnamed params section
            index += 73
            i+=1
        #print ("found unnamed param, count",i)
        index += 22
        rgb_type =data[index:index+4]        
        while rgb_type[1:] == b'\x00\x00\x00':   # this section contain RGB texture info. use these blocks to convert raw RGB hash to material texture hash
            #if rgb_type != b'\x07\x00\x00\x00':            
            chain_hash = data[index-8:index]
            #if rgb_type[0] == 0x05: 0x05 is  raw rgb texture hash,  0x0b is the material rgb hash, 0x09 is chain hash that link between the two 
            # 0x05 -> 0x0a  -> 0x09 -> 0xb , following the link list to 0xb type which hold the diffuse hash for material
            model_diffuse_hash=data[index+4:index+12]
            #print("rgb diffuse: tex hash",model_diffuse_hash)      
            type_id=b'\x61\x4d\x3b\x8b' # diffuse            
            mask_map_hash = data[index+28:index+36]  # possible mask_map for rgb texture
            rgb_map[model_diffuse_hash]=[rgb_type,chain_hash,mask_map_hash] #  map model rgb hash to material diffuse hash            
            rgb_lookup_map[chain_hash] = (model_diffuse_hash,rgb_type) #  map material diffuse has to rgb hash
            index += 116
            rgb_type =data[index:index+4]

        #print("stop pos:", hex(index))
        # This section are material definition,  can be one block for one material and matching mesh, or an array of material and array of meshes.
        mat_cnt=0
        while True: # find all material description, each section usually contain  diffuse,normal and specular texture hash
            index = data.find(b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00',index)
            if index == -1:
                break  #no more material texture
            if not (data[index+20] and data[index+21:index+24]==b'\x00\x00\x00'): # not a material block
                index += 24
                continue
            #index += 36 # mat_pattern + '08000000 08000000 xx000000 + <type id 4bytes>
            index+=16
            type_cnt = struct.unpack("I",data[index:index+4])[0]
            index += 16 # point to type id
            tex_info=data[index+4:index+12] # 01000000 e3000000
            #print ("=== Material no.",mat_cnt, tex_info)
            mat_cnt+=1
            diffuse_i=normal_i=spec_i=-1
            mat_array=[[]] * type_cnt
            #for i in range(type_cnt):
            #    mat_array[i]=[]
            d_array=[]
            n_array=[]            
            for i in range(type_cnt): # how many textures per material,  usually 3 texture map type
                type_id = data[index:index+4] # fetch tex_type                   
                # 2nd long after type_id is count of texture entry
                index+=8
                tex_cnt = struct.unpack("I", data[index:index+4])[0]   # tex_cnt 1 is single material, >1 is array of material
                index += 4                
                for j in range(tex_cnt):   # each tex map type was stored in their own array, they all have the same tex_cnt
                    t_hash = data[index:index+8]  # tex hash id
                    mat_id = data[index+8:index+10]  # 2 bytes mat id
                 
                    if type_id == b'\x61\x4d\x3b\x8b': # diffuse
                        d_array.append((t_hash,mat_id,type_id,index))
                    elif type_id == b'\x64\xf1\x6b\x59': # normal
                        n_array.append((t_hash,mat_id,type_id,index))
                    #elif type_id == b'\x9c\x9f\x46\x48': # specular ???, future enhancement
                    #    pass
                    #elif type_id == b'\xb0\x55\x75\x02': # color_id?
                    #    pass
                    #else:
                    #    print ("--unkown map, index",hex(index))
                    index +=10

                index +=12 # skip 08000000 08000000 xx00000, point to type_id
            if d_array:  # convert separated diffuse/normal/specular arrays to array of 3 textures
                #print("+++diffuse cnt, diffuse_i",tex_cnt,diffuse_i)
                n_hash=b''
                s_hash=b''
                for i in range(tex_cnt):
                    d_hash,matid,type_id, d_index= d_array[i]
                    key = d_hash+matid
                    if  key not in mat_map:
                        if n_array:
                            n_hash,_,_,n_index = n_array[i]
                        mat_map[key]=[n_hash,s_hash]  # for quick look up of material's texture component hash
            
            # mat_id + mesh_hash  come after material array , store mesh's material assignment in a dictionary (mesh_hash_map)           
            
            index+=24 # skip rest of material texture block
            d_matid = d_array[0][1]
            pattern = b'\x00\x00\x00'+ d_matid
            index = data.find(pattern, index)  # look for mat_id + mesh hash  pattern
            while index != -1 and data[index+5:index+7] == b'\x00\x00': # not a mesh hash block
                index += 7
                index = data.find(pattern, index)  # try again  
            single_hash = data[index-1]  # this is a flag indicate whether we have single mesh or multiple meshes blocks to skip
            index += 3 # point to matid

            for j in range(tex_cnt):
                matid = data[index:index+2]
                mesh_hash = data[index + 2: index +10]                        
                
                if mesh_hash not in mesh_hash_map:
                    mesh_hash_map[mesh_hash]=[]
                d_hash,d_matid,type_id, d_index = d_array[j]
                if matid != d_matid:
                    print ("Warning: matid mismatch!", hex(struct.unpack ("H",matid)[0]), hex(struct.unpack ("H",d_matid)[0]),hex(index))
                mesh_hash_map[mesh_hash].append(d_hash+d_matid)
                index +=22 # skip  matid , mesh_hash, 01000000 01000000 0100000, point to data count
                data_cnt = struct.unpack("I",data[index:index +4])[0]
                if single_hash == 0:                        
                    index += 4 + data_cnt * 4  # skip data block                
                else:
                    index += 4
                    break    
                #if data[index:index+4] != b'\x01\x00\x00\x00': # next material block
                #    print ("error, not next material block", hex(index))
        print ("total mat block",mat_cnt)
        #print ("mesh_hash_map :",mesh_hash_map)

def LoadMaterialFile():
    # look up texture type from material file (.dat)
    file_path = noesis.getSelectedFile()
    directory, filename = os.path.split(file_path)
    pattern = "*.dat"
    full_pattern = os.path.join(directory, pattern)
    material_data=b''
    # Use glob.glob to find all matching files
    matching_files = glob.glob(full_pattern)
    for file in matching_files:
        with open (file,"rb") as f:
            sig = f.read(12)
            f.seek(0)            
            if  sig[4:10]== b'\x08\x00\x00\x00\x43\x5f':  # found material file
                material_data=f.read()
                #print ("found material file:",file)
    return material_data

#load the model and textures
def KUF2d3d9LoadModel(data, mdlList):

    material_data = LoadMaterialFile()

    ctx = rapi.rpgCreateContext()
    mat_map = {}  # map diffuse hash to normal and specular hash
    rgb_map = {}  # revsered look up from RGB hash to interal hash, for RGB mask map lookup
    rgb_lookup_map = {} # look up rgb hash frome material  internal hash for that RGB
    mesh_hash_map = {}  # mesh hash and their mat id 
    if material_data:
        parseMaterial(mat_map,rgb_map,rgb_lookup_map,mesh_hash_map, material_data) 

    texList = []
    matList = []

    rapi.rpgSetActiveContext(ctx)              
    rapi.rpgReset()      # reset context before next model is loaded
    model_cnt = LoadModelFile(ctx, data, mdlList, texList, matList, material_data,mat_map,rgb_map, rgb_lookup_map, mesh_hash_map)
    
    if  model_cnt == 0:  # need this to display texture for empty model file
        mdl = NoeModel()
        mdl.setModelMaterials(NoeModelMaterials(texList, matList))
        mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
        rapi.rpgClearBufferBinds()
    else:
        mdl = rapi.rpgConstructModel()
        mdl.setModelMaterials(NoeModelMaterials(texList, matList))
        mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
    
    return 1

# load one vap file
def LoadModelFile(ctx, data, mdlList, texList, matList, material_data,mat_map,rgb_map,rgb_lookup_map, mesh_hash_map,model_no=0):

    #texList = []
    #matList = []

    bs = NoeBitStream(data)
    Version = bs.readInt()
    TextureCount = bs.readInt()
    DiffuseID=""
    NormalID=""

    #tex_hash={}   # for tex type look up
    matNames = []    
    map_type = {}

    mdl_rgb = {}
    hash_list = []
    rgb_list = [] # contains model rgb texture hash

    for i in range(0, TextureCount):
        t_hash = bs.readBytes(8) #hash
        TextureID = bs.readInt()
        Width = bs.readUShort()
        Height = bs.readUShort()
        Type1 = bs.readUShort()
        Type2 = bs.readUShort()
        Size = bs.readInt()
        data = bs.readBytes(Size)
        texFmt = 0
        orig_hash=t_hash
        strTexID=str(model_no) + "_" + str(TextureID)
        #print(Type2) 
        #print(Size)
        #DXT1
        if Type2 == 0:
            texFmt = noesis.NOESISTEX_DXT1
            tex1 = NoeTexture(strTexID, Width, Height, data, texFmt)

            if Type1 == 5:
                pixels=rapi.imageGetTexRGBA(tex1)                            
            #print("tex DXT1",i,Type1,Type2,Size,Width, Height)
        #DXT5
        if Type2 == 4:
            texFmt = noesis.NOESISTEX_DXT5
            tex1 = NoeTexture(strTexID, Width, Height, data, texFmt)  
            NormalID=strTexID
            if Type1 == 5:
                pixels=rapi.imageGetTexRGBA(tex1)
            #print("tex DXT5",i,Type1,Type2,Size, Width, Height)
        #RGB24
        if Type2 == 65:
            texFmt = noesis.NOESISTEX_UNKNOWN
            #print("tex unknown",i,Type2, Width, Height)
        #RGB24
        if Type2 == 176:
            texFmt = noesis.NOESISTEX_RGB24
            carray = bytearray(data)
            for c in range(0, len(carray), 3):
                # swap R and B color component, src was BGR32
                carray[c], carray[c+2] = carray[c+2], carray[c]
            data=bytes(carray)
            tex1 = NoeTexture(strTexID, Width, Height, data, texFmt)
            pixels=rapi.imageGetTexRGBA(tex1)
    
            rgb_list.append([t_hash,strTexID,Width,Height])
            #print("tex RGB24",i,Type1,Type2,Size, Width, Height)
            #rgb hash has a internal version for material referene, convert to internal hash
            if t_hash in rgb_map and (rgb_map[t_hash][0]==b'\x05\x00\x00\x00' or rgb_map[t_hash][0]==b'\x0a\x00\x00\x00'): # a diffuse map
                #print ("rgb in rgbmap")
                mask_hash = b''
                chain_hash = rgb_map[t_hash][1]
                if chain_hash in rgb_map:                    
                    type_id = rgb_map[chain_hash][0]
                    if type_id == b'\x02\x00\x00\x00':                            
                        mask_hash = rgb_map[chain_hash][2]
                        h = ''.join(format(byte, '02x') for byte in mask_hash)
                        #print ("--- found RGB mask hash ",h)                    
                    while type_id != b'\x0b\x00\x00\x00':        
                        h = ''.join(format(byte, '02x') for byte in chain_hash)
                        #print ("chain hash, type_id", h, type_id)                
                        chain_hash=rgb_map[chain_hash][1]
                        type_id = rgb_map[chain_hash][0]

                    mdl_rgb[t_hash]=[strTexID,mask_hash,pixels,Width,Height,tex1]

                    #h = ''.join(format(byte, '02x') for byte in t_hash)
                    #print ("found internal rgb hash",TextureID, h)
                else:
                    mdl_rgb[t_hash]=[strTexID,b'',pixels,Width,Height,tex1] # no internal mesh hash
            else:
                # no internal hash, this can be a mask map                
                mdl_rgb[t_hash]=[strTexID,b'',pixels,Width,Height,tex1]

        #Pallet?
        if Type2 == 321:
            texFmt = noesis.NOESISTEX_UNKNOWN
            #print("tex unknown",i,Type1,Type2,Size, Width, Height)
        if Type2 == 65 or Type2 == 321:
            tex1 = NoeTexture(strTexID, Width, Height, data, texFmt)                
        #tex_hash[t_hash]=[tex1,strTexID,Type2]                    

        if Type2 != 176: # don't create tex for RGB here. will add RGB texture later
            texList.append(tex1)

        map_type[t_hash]=[strTexID,Type2,Width,Height,orig_hash]
        hash_list.append(t_hash)

    
    for hash in mdl_rgb: # generate rgba texture from  rgb and alpha mask texture
        mask_hash = mdl_rgb[hash][1] 
        if mask_hash !=b'' and mask_hash in mdl_rgb: # has a mask hash
            h = ''.join(format(byte, '02x') for byte in mask_hash)
            #print (" found MASK ",h)
            rgb_pixels = mdl_rgb[hash][2]
            Width = mdl_rgb[hash][3]
            Height = mdl_rgb[hash][4]
            mask_pixels = mdl_rgb[mask_hash][2]
            AddAlpha(rgb_pixels,mask_pixels)
            tex1 = NoeTexture(mdl_rgb[hash][0], Width, Height, rgb_pixels, noesis.NOESISTEX_RGBA32)     
            texList.append(tex1)
        else:
            texList.append(mdl_rgb[hash][5]) # no alpha mask, just use the RGB24 texture        
    #print ("MapType:")
    for key in map_type:
        h = ''.join(format(byte, '02x') for byte in key)
        orig_h = ''.join(format(byte, '02x') for byte in map_type[key][4])
        #print ("map hash:",h,map_type[key],orig_h)
    
    ModelVersion = bs.readInt()
    ModelCount = bs.readInt()
    if ModelCount == 0:
        return ModelCount
    for i in range(0, ModelCount):
        mesh_hash=bs.readBytes(8) #hash
        Unk01 = bs.readInt()
        Size = bs.readInt()
        Unk02 = bs.readInt()
        Unk03 = bs.readInt()
        FT2_MESH_DESC = bs.readString()
        #print(FT2_MESH_DESC)
        bs.seek(28, NOESEEK_REL)#stuff
        Unk04 = bs.readInt()
        Unk05 = bs.readInt()
        Unk06 = bs.readInt()
        Unk07 = bs.readInt()
        MeshNameSize = bs.readInt()
        if MeshNameSize == 0:
            return i
        MeshName = bs.readBytes(MeshNameSize).decode("ASCII")
        rapi.rpgSetName(MeshName + '_' + str(model_no) + "_" + str(i))
        print ("MESH:",MeshName)
        if material_data:
            setModelMaterial2(MeshName,mesh_hash,mesh_hash_map,hash_list,map_type,mat_map,rgb_map,rgb_lookup_map, rgb_list,material_data,matNames,matList)

        Unk08 = bs.readInt()
        VertCount = bs.readInt()
        PartCount = bs.readInt()
        for i in range(0, PartCount):
            BuffType = bs.readUInt()
            DataType = bs.readUInt()
            #print(BuffType)
            #print(DataType)
            #print(bs.tell())
            if DataType == 0:
                Type = noesis.RPGEODATA_FLOAT
                Size = 4
            if DataType == 1:
                Type = noesis.RPGEODATA_FLOAT
                Size = 8
            if DataType == 2:
                Type = noesis.RPGEODATA_FLOAT
                Size = 12
            if DataType == 3:
                Type = noesis.RPGEODATA_FLOAT
                Size = 16
            if DataType == 4:
                Type = noesis.RPGEODATA_FLOAT
                Size = 4
            if DataType == 5:
                Type = noesis.RPGEODATA_FLOAT
                Size = 8
            if DataType == 6:
                Type = noesis.RPGEODATA_FLOAT
                Size = 12
            if DataType == 7:
                Type = noesis.RPGEODATA_FLOAT
                Size = 16

            if BuffType == 0:
                VertBuff = bs.readBytes(VertCount * Size)
                rapi.rpgBindPositionBuffer(VertBuff, Type, Size)
                FaceCount = bs.readInt()
                FaceBuff = bs.readBytes(FaceCount * 4)
            if BuffType == 1: # normal??
                VertBuff1 = bs.readBytes(VertCount * Size) 
                rapi.rpgBindNormalBuffer(VertBuff1, Type, Size)
                SkipCount = bs.readInt()
                SkipBuff = bs.readBytes(SkipCount * 4)
            if BuffType == 2:
                VertBuff2 = bs.readBytes(VertCount * Size)
                SkipCount = bs.readInt()
                SkipBuff = bs.readBytes(SkipCount * 4)
            if BuffType == 3:
                VertBuff3 = bs.readBytes(VertCount * Size)
                SkipCount = bs.readInt()
                SkipBuff = bs.readBytes(SkipCount * 4)
            if BuffType == 4:#uv's
                UVBuff = bs.readBytes(VertCount * Size)
                rapi.rpgBindUV1Buffer(UVBuff, Type, Size)
                SkipCount = bs.readInt()
                SkipBuff = bs.readBytes(SkipCount * 4)
            if BuffType == 5:#weights
                VertBuff5 = bs.readBytes(VertCount * Size)
                SkipCount = bs.readInt()
                SkipBuff = bs.readBytes(SkipCount * 4)
            if BuffType == 6:#Bone Id's
                VertBuff6 = bs.readBytes(VertCount * Size)
                SkipCount = bs.readInt()
                SkipBuff = bs.readBytes(SkipCount * 4)
        bs.seek(20, NOESEEK_REL)#id stuff
        BoneCount = bs.readInt()
        for i in range(0, BoneCount):
            BoneNameSize = bs.readInt()
            BoneName = bs.readBytes(BoneNameSize).decode("ASCII")
        MeshGrp = bs.readInt()

        rapi.rpgCommitTriangles(FaceBuff, noesis.RPGEODATA_INT, FaceCount, noesis.RPGEO_TRIANGLE, 1)

        rapi.rpgClearBufferBinds()
    return ModelCount

################### disaplay full character by loading multiple vap files ####################

# rotate part variation according to ksw file name,  load all part files
def KUF2SwitchModel(data, mdlList):

    ctx = rapi.rpgCreateContext()
    rapi.rpgSetActiveContext(ctx)              
    rapi.rpgReset()      # reset context before next model is loaded

    material_data = LoadMaterialFile()
    mat_map = {}
    rgb_map = {}
    rgb_lookup_map = {}
    mesh_hash_map = {}
    if material_data:
        parseMaterial(mat_map,rgb_map,rgb_lookup_map,mesh_hash_map,material_data) 

    # body part database for constructing full character from multiple files
    group_array = build_model_db(material_data)

    #for g in group_array:
    #    print ("Group:",g[0])  # first item is group name
    #    for part,filelist in g[1]:  # second item is list of part variation and their files
    #        print (part,filelist)

    texList = []
    matList = []

    file_path = noesis.getSelectedFile()
    directory, input_name = os.path.split(file_path)

    # ==== rotate body part variation index in config file ==== #
    # read character body group configuration from last preview
    char_config_file = os.path.join(directory, "kuf2_char_config.txt")
    
    #print ("read config file")
    invalid_setting = False
    if os.path.exists(char_config_file)==False:  # create a default config file
        invalid_setting = True
    else:
        with open(char_config_file,"rt") as f:
            part_config_str = f.readline()
            try:
                part_idx = [int(x) for x in part_config_str.strip().split(':')] # split config string into list of indices
                if  len(group_array) >  len (part_idx):
                    invalid_setting = True
            except:
                invalid_setting = True
    if  invalid_setting:
        part_config_str=""  # genereate default setting for part selection
        for i,(key,_) in enumerate(group_array):   # just a bunch of indices for each body group array
            if i > 0:
                part_config_str += ":"
            if key.find("acc") != -1:  # accessory group
                part_config_str += "-1" # accessaries hidden by default, no model loaded
            else:
                part_config_str += "0"
        #print ("new config:",part_config_str)
        part_idx = [int(x) for x in part_config_str.strip().split(':')] # split config string into list of indices
    
    if  input_name.find("000_") != -1: # _000_full_character.ksw
        pass
        # just show the last body combination        
    else:
        idx = int(input_name.lstrip('_').split("_")[0]) # input file name has the group idx "_00_<name>.ksw"
        #print ("switching group idx:",idx)

        part_idx[idx] += 1  # move to next part variation for this group

        if part_idx[idx] >= len(group_array[idx][1]):  # exceed part variation count
            if group_array[idx][0].find("acc") != -1:  # accessory group
                part_idx[idx] = -1  # hide accessary part, no model loaded
            else:
                part_idx[idx] = 0  # loop back to first part variation

    #record updated config
    with open(char_config_file,"wt") as f:
        new_part_config_str=str(part_idx[0])
        for i in range(1,len(part_idx)):
            new_part_config_str += ":" + str(part_idx[i]) 
        print ("new config:",new_part_config_str)
        f.write(new_part_config_str) 

    limit_str = str(len(group_array[0][1]))
    for i in range(1,len(group_array)):
        limit_str += ":" + str(len(group_array[i][1]))
    print ("part variation limit:",limit_str)
    
    #========= display full character model =============#
    model_id = 0
    model_cnt = 0
    for i, (grp_name,parts) in enumerate(group_array):  # display every group and its selected part based on idx in config file
        idx = part_idx[i]
        if idx >=0 and idx < len(parts):  # part is visible
            for hex_name, real_name in parts[idx][1]:
                file_name = hex_name + ".vap"
                full_path = os.path.join(directory, file_name)
                print ("full_path:",full_path)
                if os.path.exists(full_path):
                    with open (full_path,"rb") as f:                        
                        data = f.read()                                  
                        model_cnt += LoadModelFile(ctx,data, mdlList, texList, matList, material_data,mat_map,rgb_map, rgb_lookup_map, mesh_hash_map, model_id)
                        model_id +=1        

    if  model_cnt == 0:  # need this to display texture file with no model
        mdl = NoeModel()
        mdl.setModelMaterials(NoeModelMaterials(texList, matList))
        mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
        rapi.rpgClearBufferBinds()
    else:
        mdl = rapi.rpgConstructModel()
        mdl.setModelMaterials(NoeModelMaterials(texList, matList))
        mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList    

    for grp_name, parts in group_array:
        print ("===grp name", grp_name)
        for part in parts:
            print (part[0], part[1])
    return 1

groups = {  # mapping from file name to group name
    # "part file name keyword" : "body groups name"]
        
        "_face":"00_face",
        "_hair":"01_hair",
        "_hea":"01_hair",       # head model is from hair group
        "_ub":"02_upperbody",
        "_lb":"03_lowerbody",
        "_gt":"04_gauntlet",
        "_sd":"05_shoulder",
        "_bt":"06_boot",
        # accessories
        "_kn":"07_knee_acc",
        "_ch":"08_chest_acc",
        "_si":"09_side_acc",
        "_hd":"10_head_acc",
        "_fa0":"11_face_acc",
        "_er":"12_earring_acc",
}
 
#character id from material file header
char_code={b'glenn\x01':"gl",    # character id :  short code
           b'isabela\x01':"is",
           b'olivia\x01':"ov",
           b'regnier\x01':"rg",
           b'regnier_test\x01':"rg",
           }


def build_model_db(material_data):
    group_array = []
    part_db = {}
    file_no=1
    # put all vap file (hex file name) in part groups based on their descriptive name
    # i.e. I_DEH_IS_UBA05_A_mantel ,IS = "Isabela", _UB = "upperbody" , A05_A = one of the part variation , each variation can have multiple components

    #  detect which charcter it is
    name_code=''
    mat_header = material_data[:48]
    for key in char_code:
        if mat_header.find(key) != -1:
            name_code=char_code[key]        
            if key.find(b'regnier_test')!= -1:
                char_tag = "===rg-test"
            else:
                char_tag = "==="+name_code
            break
    if not name_code:
        return group_array
    
    groupset=set() # group name list
    for key in groups: 
        groupset.add(groups[key])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # info file for mapping hex file name to descriptive name
    KUF2_NamesFile=os.path.join(script_dir,"KUF2FileNames.txt")
    if os.path.isfile(KUF2_NamesFile):
        with open (KUF2_NamesFile,"r") as f:  
            print ("looking for char tag:",char_tag)                           
            found = False
            lines = f.readlines()
            for line in lines:
                line=line.strip().lower()
                if not found:                    
                    if line.find(char_tag) != -1: # start of this character section
                       found = True                     
                    continue
                if line.find("===")!=-1: # end of this character section, exit
                    break

                filename = "{:08x}".format(file_no)
                #print ("parsing line:",filename, line)
                file_no += 2  #   the KUF2_2014.bms script generated hex file name by increment of 2 in accending order 
                
                for k in sorted(groups):  # pairing hex file name to the descriptive file name
                    key=name_code + k
                    if key in line:
                        #print ('{}: {},'.format(filename, key))
                        ind=key_end=vind = 0
                        key_ind = line.find(key)
                        ind =  key_ind + len(key)
                        if "_" in line[ind:]:
                            key_end=line.find("_",ind)
                            if line.find("scar",ind) != -1 or line.find("tattoo",ind) != -1: # skip scar and tattoo parts, they have no model file
                                continue
                            # split filename into group+part_variant+_component
                            if "_" in line[key_end+1:]:
                                # looking for key[suffix]_A_
                                vind=line.find("_",key_end+1)
                                if (vind - key_end ==  2):
                                    part_key=line[ind:vind]  # file name LB01_A_mantle_left, is group 03_lowerbody, partkey is [01_A] , _mantle_left is component name
                                else:
                                    part_key=line[ind:key_end] # file name LB01_mantle_left, is group 03_lowerbody, partkey is [01], _mantle_left is component name
                            elif len(line) - key_end == 2:
                                if k == "_hair":  # special case for hair part, _hair is the key, suffix [0x_]A/B/C/D belong to same hair part
                                    part_key = line[ind:key_end+1]
                                else:
                                    part_key=line[ind:]  #    filename is LB01_A, part key is [01_A]
                            else:
                                part_key=line[ind:key_end]   # filename is LB01 partkey is [01]
                        else:
                            part_key=line[ind:]
                        #print ("part_key: {} {} {} {}".format(part_key,ind,key_end,vind))
                        group_db_key=groups[k]
                        if group_db_key not in part_db:
                            part_db[group_db_key]={}
                        if part_key not in part_db[group_db_key]:
                            part_db[group_db_key][part_key]=[]
                        part_db[group_db_key][part_key].append((filename,line[key_ind:]))  # each part variation can use multiple files

            print (hex(file_no))
    else:
        print ("No KUF2FileNames.txt found in script directory:", script_dir)

    # convert dictionary to array for ordered access
    for name in sorted(groupset):
        if name in part_db:
            part_array = []
            for partkey in sorted(part_db[name]):
                part_array.append((partkey,part_db[name][partkey]))
                #print ("{} : {}".format(partkey,part_db[key][partkey]))
            group_array.append((name,part_array))
        else:
            group_array.append((name,[]))

    return group_array  
