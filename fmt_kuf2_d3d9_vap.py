#Noesis Python model import+export test module, imports/exports some data from/to a made-up format

# Original KUF2 .d3d9parmetric model file veiwer plugin. Xentax forum, author unknown.
# 
# Preview *.vap model file with texture binding by alanm1
#
# Special thanks:
#       Luigi Auriemma:  KUF2 2014 pkg file unpack bms script     
#       The arthor of .d3dparametric model viewer. from Xentax
#   
# Version 0.1:
# Support  2014 KUF 2 Asia client hero models (in Hero*.pkg files, they are not encrypted).
#  
# Installaion:
#   Copy this Noesis .py plugin to <Noesis dir>/plugins/python/ directory
# Usage:
#   Use QuickBMS and kuf2_2014.bms to unpak Hero*.pkg file to their own directory.
#   Most *.vap file contains texture and model. Each hero has a .dat file contains model/texture assignment
#
# There are 5 Heroes type:
#
# For Gunsliger(Glen):   copy Hero3\*.dat Hero2\ , Use Noesis and browse Hero2 directory for model preview
# For Spellsword(Isabella) copy Hero6\*.dat Hero5\, Use Noesis and browse Hero5 directory for model preview
# Follow same rule to preview the other 3 heroes. 
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

def AddAlpha(diffuse,mask):
    for i in range(0,len(diffuse),4):
        diffuse[i+3]=mask[i]

'''def getTexType(hash,tex_hash,data):
    index = data.find(hash)
    if index != -1:
        #look back for type id
        type_id = data[index-12, index -8]  # 4 bytes
        tex_hash[hash][1]=type_id
        
        if type_id == b'\x64\xf1\x6b\x59': # normal
        if type_id == b'\x9c\x9f\x46\x48': # specular ??
        if type_id == b'\x61\x4d\x3b\x8b': # diffuse
        elif type_id == b'\xb0\x55\x75\x02': # color_id?        
'''
def setModelMaterial2(m_name,m_hash,hash_list,map_type,mat_map,rgb_map,rgb_list,data,matNames,matList):            
    index = data.find(m_hash)
    print ("=======For mesh",m_hash)
    firstBlock = True
    while index != -1:  # found mesh        
        material_id = data[index-2:index]
        mesh_type = data[index-16:index-2]
        last_material = material_id
        material_str = hex(struct.unpack ("H",material_id)[0])
        print("----looking for mesh material", material_str,"   ",m_hash)

        diffuse_id=normal_id=spec_id=''
        #print ("mesh type == ",mesh_type)
        if mesh_type == b'\x02\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00': # head/face mesh marker            
            print ("HEAD mesh material")
            d_index = data.rfind(b'\x61\x4d\x3b\x8b',0,index-14) # search backward for a diffuse map hash
            if d_index !=-1:
                t_hash_key  = data[d_index+12:d_index +22] # this is diffuse_hash+matid            
                if t_hash_key in mat_map:
                    n_hash,s_hash= mat_map[t_hash_key]
                    t_hash = t_hash_key[:8]
                    if t_hash in map_type:  # rgb texture can have alias, more than one internal hash
                        diffuse_id = map_type[t_hash][0]
                        diffuse_hash = t_hash                                        
                        if n_hash in map_type:
                            normal_id= map_type[n_hash][0]
                        print ("Found HEAD diffuse map",t_hash,n_hash,diffuse_id,normal_id)                
                else:
                    h = ''.join(format(byte, '02x') for byte in t_hash_key)
                    print ("HEAD diffsue not in mat_map!!!!,key",h)
        else:            
            for t_hash in hash_list:
                key = t_hash+material_id # mat id + texture hash as key
                if key in mat_map:                                                        
                    diffuse_id = map_type[t_hash][0]    
                    diffuse_hash = t_hash                
                    n_hash,s_hash= mat_map[key]
                    if n_hash in map_type:
                        normal_id= map_type[n_hash][0]
                    print ("Found diffuse map",t_hash,n_hash,diffuse_id,normal_id)
                    break
                else:
                    print ("mat , hash not found", map_type[t_hash][0],material_str, t_hash) 

        if diffuse_id:
            break                         
        else:   
            index = data.find(m_hash,index + 8)

    # diffuse tex is required for material
    if diffuse_id:  
        MatName="Mat_"+ diffuse_id
        if not MatName in matNames: # new materail
                print("material", MatName, diffuse_id)
                mat = NoeMaterial(MatName,diffuse_id) # diffuse with alpha
                if normal_id:  # Add normal if exists                            
                    mat.setNormalTexture(normal_id)                    
                # Mat_0_0  is  RGB mat, no alpha
                # Mat_0_2  is  RGBA mat , with alpha                    
                matNames.append(MatName)
                matList.append(mat)
        rapi.rpgSetMaterial(MatName)
    else:
        rapi.rpgSetMaterial("") 

def parseMaterial(mat_map,rgb_map,data):
    param="Unnamed color"
    index = data.find(b'\x17\x00\x00\x00'+param.encode('ASCII'))
    i =0
    if index != -1:
        while data[index:index+4] == b'\x17\x00\x00\x00':  # skip unnamed params section
            index += 73
            i+=1
        print ("found unnamed param, count",i)
        index += 22
        rgb_type =data[index:index+4]        
        while rgb_type[1:] == b'\x00\x00\x00':   # this section contain RGB texture info. use these blocks to convert raw RGB hash to material diffuse hash 
            #if rgb_type != b'\x07\x00\x00\x00':            
            chain_hash = data[index-8:index]
            #if rgb_type[0] == 0x05:    0x05 is  model rgb texture hash,  0x0b is the material rgb hash, 0x09 is chain hash that link between the two 
            # 0x05 -> 0x0a  -> 0x 09 -> 0xb , following the link list to 0xb type which hold the diffuse hash for material
            model_diffuse_hash=data[index+4:index+12]
            print("rgb diffuse: tex hash",model_diffuse_hash)      
            type_id=b'\x61\x4d\x3b\x8b' # diffuse
            #if model_diffuse_hash not in rgb_map:
            mask_map_hash = data[index+28:index+36]  # possible mask_map for rgb texture
            rgb_map[model_diffuse_hash]=[rgb_type,chain_hash,mask_map_hash] #  map model rgb hash to material diffuse hash            
            index += 116
            rgb_type =data[index:index+4]
        print("stop pos:", hex(index))
        # find two kind of material descriptor
        mat_cnt=0
        while True: # find all material description, each section usually contain  diffuse,noral and specular texture hash
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
            for i in range(type_cnt): #   usually 3 texture map type
                type_id = data[index:index+4] # fetch tex_type                   
                # 2nd long after type_id is count of texture entry
                index+=8
                tex_cnt = struct.unpack("I", data[index:index+4])[0]
                index += 4                
                for j in range(tex_cnt):   # each tex map type was stored in their own array, they all have the same tex_cnt
                    t_hash = data[index:index+8]  # tex hash id
                    mat_id = data[index+8:index+10]  # 2 bytes mat id
                 
                    if type_id == b'\x61\x4d\x3b\x8b': # diffuse
                        d_array.append((t_hash,mat_id,type_id,index))
                    elif type_id == b'\x64\xf1\x6b\x59': # normal
                        n_array.append((t_hash,mat_id,type_id,index))
                    #elif type_id == b'\x9c\x9f\x46\x48': # specular ???
                    #    pass
                    #elif type_id == b'\xb0\x55\x75\x02': # color_id?
                    #    pass
                    #else:
                    #    print ("--unkown map, index",hex(index))

                    #mat_array[i].append((t_hash,mat_id,type_id))
                    index +=10
                    material_str = hex(struct.unpack ("H",mat_id)[0])    
                index +=12 # skip 08000000 08000000 xx00000, point to type_id
            if d_array:  # convert separated diffuse/normal/specular arrays to one array of of 3 maps.
                #print("+++diffuse cnt, diffuse_i",tex_cnt,diffuse_i)
                n_hash=s_hash=b''
                for i in range(tex_cnt):
                    d_hash,matid,type_id, d_index= d_array[i]
                    key = d_hash+matid
                    if d_hash == b'\x9f\x28\x34\x44\x91\x4b\x56\x32':
                        print ("found missing texture ",d_hash, mat_id)
                    if  key not in mat_map:
                        if n_array:
                            n_hash,_,_,n_index = n_array[i]
                        mat_str = hex(struct.unpack ("H",matid)[0])                           
                        #print ("entry: ",d_hash,mat_str,type_id== b'\x61\x4d\x3b\x8b', type_id, len(n_array))
                        if n_hash==b'':
                            print("++++ no n_hash for diffuse:",d_hash,hex(d_index))                        
                        mat_map[key]=[n_hash,s_hash]  # for quick look up of diffuse map     
        print ("total mat block",mat_cnt)
               
#load the model and textures
def KUF2d3d9LoadModel(data, mdlList):
    texList = []
    matList = []
    ctx = rapi.rpgCreateContext()
    bs = NoeBitStream(data)
    Version = bs.readInt()
    TextureCount = bs.readInt()
    DiffuseID=""
    NormalID=""
    tex_hash={}   # for tex type look up
    tex_group={}  # text group elemet  has 3 index [ dxt1/rgb tex id, normal tex id, dxt5 tex id] , -1 means that tex not found
    tex_order=[]  # order texture by size
    matNames = []

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
                print ("found material file:",file)

    map_type = {}
    mat_map = {}
    rgb_map = {}
    mdl_rgb = {}
    hash_list = []
    rgb_list = [] # contains model rgb texture hash
    if material_data:
        parseMaterial(mat_map,rgb_map,material_data) 

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
        #print(Type2) 
        #print(Size)
        #DXT1
        if Type2 == 0:
            texFmt = noesis.NOESISTEX_DXT1
            tex1 = NoeTexture(str(TextureID), Width, Height, data, texFmt)

            if Type1 == 5:
                pixels=rapi.imageGetTexRGBA(tex1)                            
            print("tex DXT1",i,Type1,Type2,Size,Width, Height)
        #DXT5
        if Type2 == 4:
            texFmt = noesis.NOESISTEX_DXT5
            tex1 = NoeTexture(str(TextureID), Width, Height, data, texFmt)  
            NormalID=str(TextureID)
            if Type1 == 5:
                pixels=rapi.imageGetTexRGBA(tex1)
            print("tex DXT5",i,Type1,Type2,Size, Width, Height)
        #RGB24
        if Type2 == 65:
            texFmt = noesis.NOESISTEX_UNKNOWN
            print("tex unknown",i,Type2, Width, Height)
        #RGB24
        if Type2 == 176:
            texFmt = noesis.NOESISTEX_RGB24
            carray = bytearray(data)
            for c in range(0, len(carray), 3):
                # swap R and B color component, src was BGR32
                carray[c], carray[c+2] = carray[c+2], carray[c]
            data=bytes(carray)
            tex1 = NoeTexture(str(TextureID), Width, Height, data, texFmt)
            pixels=rapi.imageGetTexRGBA(tex1)
            # build matgroup based on res.
            key=Width * Height
            if key not in tex_group:
                tex_group[key]=[-1,-1,-1]
                tex_order.append(key)
    
            rgb_list.append([t_hash,str(TextureID),Width,Height])
            print("tex RGB24",i,Type1,Type2,Size, Width, Height)
            #rgb hash has a internal version for material referene, convert to internal hash
            if t_hash in rgb_map and (rgb_map[t_hash][0]==b'\x05\x00\x00\x00' or rgb_map[t_hash][0]==b'\x0a\x00\x00\x00'): # a diffuse map
                print ("rgb in rgbmap")
                mask_hash = b''
                chain_hash = rgb_map[t_hash][1]
                if chain_hash in rgb_map:                    
                    type_id = rgb_map[chain_hash][0]
                    if type_id == b'\x02\x00\x00\x00':                            
                        mask_hash = rgb_map[chain_hash][2]
                        h = ''.join(format(byte, '02x') for byte in mask_hash)
                        print ("--- found mask hash ",h)                    
                    while type_id != b'\x0b\x00\x00\x00':        
                        h = ''.join(format(byte, '02x') for byte in chain_hash)
                        print ("chain hash, type_id", h, type_id)                
                        chain_hash=rgb_map[chain_hash][1]
                        type_id = rgb_map[chain_hash][0]

                    # internal diffuse hash use for pairing with normal and spec texture                                        
                    t_hash=rgb_map[chain_hash][1]            
                    mdl_rgb[t_hash]=[str(TextureID),mask_hash,pixels,Width,Height,tex1]

                    h = ''.join(format(byte, '02x') for byte in t_hash)
                    print ("found internal rgb hash",TextureID, h)
                else:
                    mdl_rgb[t_hash]=[str(TextureID),b'',pixels,Width,Height,tex1] # no internal mesh hash
            else:
                # no internal hash, this can be a mask map                
                mdl_rgb[t_hash]=[str(TextureID),b'',pixels,Width,Height,tex1]

        #Pallet?
        if Type2 == 321:
            texFmt = noesis.NOESISTEX_UNKNOWN
            print("tex unknown",i,Type1,Type2,Size, Width, Height)
        if Type2 == 65 or Type2 == 321:
            tex1 = NoeTexture(str(TextureID), Width, Height, data, texFmt)                
        tex_hash[t_hash]=[tex1,str(TextureID),Type2]                    

        if Type2 != 176: # don't create tex for RGB here. will add RGB texture later
            texList.append(tex1)

        map_type[t_hash]=[str(TextureID),Type2,Width,Height,orig_hash]
        hash_list.append(t_hash)

    
    for hash in mdl_rgb: # generate rgba texture from  rgb and alpha mask texture
        mask_hash = mdl_rgb[hash][1] 
        if mask_hash !=b'' and mask_hash in mdl_rgb: # has a mask hash
            h = ''.join(format(byte, '02x') for byte in mask_hash)
            print (" found MASK ",h)
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
        print ("map hash:",h,map_type[key])
    
    ModelVersion = bs.readInt()
    ModelCount = bs.readInt()
    if ModelCount == 0:
        mdl = NoeModel()
        mdl.setModelMaterials(NoeModelMaterials(texList, matList))
        mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
        rapi.rpgClearBufferBinds()
        return 1
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
            mdl = NoeModel()
            mdl.setModelMaterials(NoeModelMaterials(texList, matList))
            mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
            rapi.rpgClearBufferBinds()
            return 1
        MeshName = bs.readBytes(MeshNameSize).decode("ASCII")
        rapi.rpgSetName(MeshName + '_' + str(i))
        print ("MESH:",MeshName)
        if material_data:
            setModelMaterial2(MeshName,mesh_hash,hash_list,map_type,mat_map,rgb_map,rgb_list,material_data,matNames,matList)
        #    findMaterial(mesh_hash,tex_hash,material_data,matNames,matList) # try to find a material with correct texture

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
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList

    return 1