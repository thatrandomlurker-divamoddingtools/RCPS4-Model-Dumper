# RCPS4-Model-Dumper
WIP Script to rip rcps4 model files

# Usage
simply run `rcps4_model_dumper.py *file*` on a decompressed model file, and the program should output an OBJ file with UVs intact, plus a txt file detailing the joint information that can currently be read.

# Known Issues
Currently doesn't support ripping normals, vertex weights, or bone positions. Textures also can't be ripped as of writing this, severely limiting overal usefulness.

# Credits
doesthisusername for their ig-tools which helped me figure out the verts + faces, as well as allowing the assets to be extracted and decompressed in the first place
