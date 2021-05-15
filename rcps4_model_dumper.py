import struct
import reader  # ToDo, refactor to explicitly use reader
import sys
file = sys.argv[1]

with open(file, 'rb') as f:
    magic = f.read(4)
    if magic != b'1TAD':
        raise Exception("Invalid .model file. are you sure you decompressed it?")
        exit()
    typeHash = struct.unpack('<I', f.read(4))[0]
    fileSize = struct.unpack('<I', f.read(4))[0]
    sectionCount = struct.unpack('<I', f.read(4))[0]
    # quickly define some variables for later use
    VertexOffset = 0
    VertexSize = 0
    UVOffset = 0
    UVSize = 0
    SubmeshInfoOffset = 0
    SubmeshInfoSize = 0
    FaceDataOffset = 0
    FaceDataSize = 0
    JointDataOffset = 0
    JointDataSize = 0
    
    for i in range(sectionCount):
        sectionNameHash = struct.unpack('<I', f.read(4))[0]
        if sectionNameHash == 140084797:
            FaceDataOffset, FaceDataSize = struct.unpack('<II', f.read(8))
        elif sectionNameHash == 385071640:
            UVOffset, UVSize = struct.unpack('<II', f.read(8))
        elif sectionNameHash == 2027539422:
            SubmeshInfoOffset, SubmeshInfoSize = struct.unpack('<II', f.read(8))
        elif sectionNameHash == 2844518043:
            VertexOffset, VertexSize = struct.unpack('<II', f.read(8))
        elif sectionNameHash == 366976315:
            JointDataOffset, JointDataSize = struct.unpack('<II', f.read(8))
        else:
            f.seek(8, 1)
    # Let's get the verts first
    Verts = []
    f.seek(VertexOffset)
    while f.tell() < VertexOffset + VertexSize:
        vertpos = struct.unpack('<hhh', f.read(6))
        f.seek(10, 1)
        Verts.append([vertpos[0] * 0.001, vertpos[1] * 0.001, vertpos[2] * 0.001])
    # Now the UVs
    f.seek(UVOffset)
    UVs = []
    while f.tell() < UVOffset + UVSize:
        UVs.append(list(struct.unpack('<ee', f.read(4))))
    # Next the Face indices
    f.seek(FaceDataOffset)
    FaceIdxs = []
    while f.tell() < FaceDataOffset + FaceDataSize:
        FaceIdxs.append(struct.unpack('<H', f.read(2))[0])
    # Finally submesh info
    f.seek(SubmeshInfoOffset)
    SubmeshInfo = []
    while f.tell() < SubmeshInfoOffset + SubmeshInfoSize:
        f.seek(16, 1)
        SubmeshInfo.append(list(struct.unpack('<IIII', f.read(16))))
        f.seek(32, 1)
    # and now the moment of truth.
    with open(file.split('.')[0] + '.obj', 'w') as obj:
        for vert in Verts:
            obj.write(f'v {vert[0]} {vert[1]} {vert[2]}\n')
        for uv in UVs:
            obj.write(f'vt {uv[0]} {uv[1]}\n')
        obj.write('s 1\n')  # because i haven't found the normals yet.
        for smi in range(len(SubmeshInfo)):
            obj.write(f'o {file.split(".")[0]}_submesh{smi}\n')
            for i in range(SubmeshInfo[smi][1], SubmeshInfo[smi][1]+SubmeshInfo[smi][2], 3):
                obj.write(f"f {FaceIdxs[i] + SubmeshInfo[smi][0] + 1}/{FaceIdxs[i] + SubmeshInfo[smi][0] + 1} {FaceIdxs[i+1] + SubmeshInfo[smi][0] + 1}/{FaceIdxs[i+1] + SubmeshInfo[smi][0] + 1} {FaceIdxs[i+2] + SubmeshInfo[smi][0] + 1}/{FaceIdxs[i+2] + SubmeshInfo[smi][0] + 1}\n")
                
    BoneParents = []
    BoneUnk1s = []
    BoneChildren = []
    BoneUnk2s = []
    BoneHashes = []
    BoneNames = []
    # Let's try logging some armature info, this could help with ripping in the future
    f.seek(JointDataOffset)
    with open(file.split('.')[0] + '_ParentInfo.txt', 'w') as inf:
        inf.write('# Structure: Parent, Unk, Child, Unk2, NameHash, NameOffset\n')
        while f.tell() < JointDataOffset + JointDataSize:
            Parent = reader.ReadInt16(f, '<')
            print(Parent)
            BoneParents.append(Parent)
            Unk = reader.ReadInt16(f, '<')
            BoneUnk1s.append(Unk)
            Child = reader.ReadInt16(f, '<')
            BoneChildren.append(Child)
            Unk2 = reader.ReadInt16(f, '<')
            BoneUnk2s.append(Unk2)
            Hash = reader.ReadUInt32(f, '<')
            BoneHashes.append(Hash)
            BoneName = reader.ReadStrOffset(f, '<', 'NullTerminated', 'ASCII')
            BoneNames.append(BoneName)
        for i in range(len(BoneParents)):
            if BoneParents[i] != -1:
                inf.write(f'Bone {BoneNames[i]} (Index {i}, Hash {BoneHashes[i]}) is parented to Bone {BoneNames[BoneParents[i]]}, child is {BoneNames[BoneChildren[i]]}\n')
            else:
                inf.write(f'Bone {BoneNames[i]} (Index {i}, Hash {BoneHashes[i]}) has no parent, child is {BoneNames[BoneChildren[i]]}\n')
        
            