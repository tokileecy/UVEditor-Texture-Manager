bl_info = {
    "name": "get Node Texture",
    "author": "Stokes Lee",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "UV > Header",
    "category": "UV"
}

import bpy
from bpy.types import Menu, Panel, UIList


class Manager():
    @property
    def active_object(self):
        return bpy.context.scene.objects.active
    
    @property
    def material(self):
        if len(self.active_object.material_slots) > 0 :
            material = self.active_object.material_slots[0].material
            return material
        return None
    @property
    def texture_nodes(self):
        nodes = self.material.node_tree.nodes
        return [node for node in nodes if node.type == 'TEX_IMAGE']

    @property
    def uv_editor_area(self):
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                return area
        return None

    def set_image(self, area, image_node):
        area.spaces.active.image = image_node.image

    
class Texture_Manager_Panel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Texture Manager"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    manager = Manager()

    def draw(self, context):
        layout = self.layout
        self.layout.operator("ops.uv_editor_get_uv_0")
        self.layout.operator("ops.uv_editor_get_uv_1")
        
class UVEditor_get_uv_1(bpy.types.Operator):
    bl_idname = "ops.uv_editor_get_uv_1"
    bl_label = "Active"

    def get_image_node(self) :
        material = Texture_Manager_Panel.manager.material
        active_node = material.node_tree.nodes.active
        if active_node is not None:
            if active_node.type == 'TEX_IMAGE':
                return active_node
        return None

    def execute(self, context):
        area = Texture_Manager_Panel.manager.uv_editor_area
        texture_node = self.get_image_node()
        
        if texture_node is not None:
            Texture_Manager_Panel.manager.set_image(area,texture_node)
        return {'FINISHED'}

class UVEditor_get_uv_0(bpy.types.Operator):
    bl_idname = "ops.uv_editor_get_uv_0"
    bl_label = "Classic"

    def get_image_node(self) :
        Tex_nodes = Texture_Manager_Panel.manager.texture_nodes
        for node in Tex_nodes :
            if  len(node.outputs['Color'].links) > 0 :
                base = node.outputs['Color'].links[0].to_node.bl_rna.base
                if base == bpy.types.ShaderNode.bl_rna :
                    return node
        return None

    def execute(self, context):
        area = Texture_Manager_Panel.manager.uv_editor_area
        texture_node = self.get_image_node()
        if texture_node is not None:
            Texture_Manager_Panel.manager.set_image(area,texture_node)
        return {'FINISHED'}
    
def draw_func(self, context):
    layout = self.layout
    layout.operator("ops.uv_editor_get_uv_0")
    
def register():
    bpy.utils.register_class(UVEditor_get_uv_0)
    bpy.utils.register_class(UVEditor_get_uv_1)
    bpy.types.IMAGE_HT_header.prepend(draw_func)
    bpy.utils.register_class(Texture_Manager_Panel)

    
def unregister():
    bpy.utils.unregister_class(UVEditor_get_uv_0)
    bpy.utils.unregister_class(UVEditor_get_uv_1)
    bpy.types.IMAGE_HT_header.remove(draw_func)
    bpy.utils.unregister_class(Texture_Manager_Panel)

if __name__ == "__main__":
    register()  