import os

PathResources = os.path.abspath(os.path.split(__file__)[0])
PathFonts = os.path.join(PathResources, 'Fonts')
PathMaterials = os.path.join(PathResources, 'Materials')
PathMeshes = os.path.join(PathResources, 'Meshes')
PathShaders = os.path.join(PathResources, 'Shaders')
PathTextures = os.path.join(PathResources, 'Textures')

from .ResourceManager import VertexShaderLoader, FragmentShaderLoader, MaterialLoader, MeshLoader, ResourceManager