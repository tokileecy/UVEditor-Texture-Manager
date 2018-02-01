bl_info = {
    "name": "UIEditor Texture Manager",
    "author": "Stokes Lee",
    "version": (0, 2, 0),
    "blender": (2, 79, 0),
    "location": "UV > Properties Shelf",
    "category": "UV"
}

import bpy
from bpy.types import PropertyGroup, Panel
from rna_prop_ui import PropertyPanel
from bpy.props import EnumProperty

class Manager():

    @property
    def render_engine(self):
        return bpy.context.scene.render.engine

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
    def use_nodes(self):
        return self.material.use_nodes

    @property
    def uv_editor_area(self):
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                return area
        return None

    @property
    def slot_textures(self):
        texture_slots = self.material.texture_slots
        textures = [texture for texture in texture_slots if texture is not None]
        return textures
    @property
    def slot_textures_item(self):
        textures = self.slot_textures
        return [(str(index), textures[index].texture.image.name, textures[index].texture.image.name) for index in range(0, len(textures))]
    
    @property
    def texture_nodes(self):
        nodes = self.material.node_tree.nodes
        if self.render_engine == 'CYCLES':
            return [node for node in nodes if node.type == 'TEX_IMAGE' ]
        elif self.render_engine == 'BLENDER_RENDER':
            return [node for node in nodes if node.type == 'TEXTURE']

    @property
    def texture_nodes_item(self):
        nodes = self.texture_nodes
        if self.render_engine == 'CYCLES':
            return [(str(index), nodes[index].image.name, nodes[index].image.name) for index in range(0, len(nodes))]
        elif self.render_engine == 'BLENDER_RENDER':
            return [(str(index), nodes[index].texture.image.name, nodes[index].texture.image.name) for index in range(0, len(nodes))]

    def set_image(self, area, image_node):
        area.spaces.active.image = image_node.image

    def slot_textures_item_update(self, index):
        textures = self.slot_textures
        uv_editor_area = self.uv_editor_area
        uv_editor_area.spaces.active.image = textures[index].texture.image
    
    def texture_nodes_item_update(self, index):
        texture_nodes = self.texture_nodes
        uv_editor_area = self.uv_editor_area
        if self.render_engine == 'CYCLES':
            uv_editor_area.spaces.active.image = texture_nodes[index].image
        elif self.render_engine == 'BLENDER_RENDER':
            uv_editor_area.spaces.active.image = texture_nodes[index].texture.image

class Texture_Manager_Prop(PropertyGroup):
    slot_textures_item = EnumProperty(
        name="Texture",
        description="",
        items = lambda scene, context : Texture_Manager_Panel.manager.slot_textures_item,
        update = lambda self, context : Texture_Manager_Panel.manager.slot_textures_item_update(int(self.slot_textures_item))
        )
    node_texture_item = EnumProperty(
        name="Texture",
        description="",
        items = lambda scene, context : Texture_Manager_Panel.manager.texture_nodes_item,
        update = lambda self, context : Texture_Manager_Panel.manager.texture_nodes_item_update(int(self.node_texture_item))
        )
        
class Texture_Manager_Panel(Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Texture Manager"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    manager = Manager()
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        col.prop(context.scene.render, "engine")
        material = self.manager.material
        ob = context.object
        if context.object is not None:
            is_sortable = (len(ob.material_slots) > 1)
            rows = 1
            if is_sortable:
                rows = 4
            row = col.row()
            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

        if material is not None:
            if self.manager is not None:
                col.prop(material, "use_nodes", icon='NODETREE')
            if material.use_nodes:
                col.label("Texture Node")
                col.prop(scene.Texture_Manager_Prop,"node_texture_item")
            else:
                if self.manager.render_engine == 'BLENDER_RENDER':
                    col.label("Texture Slot")
                    col.prop(scene.Texture_Manager_Prop,"slot_textures_item")
        else:
            col.label("Do not Exist Material")
    
def register():
    bpy.utils.register_class(Texture_Manager_Panel)
    bpy.utils.register_class(Texture_Manager_Prop)
    bpy.types.Scene.Texture_Manager_Prop = bpy.props.PointerProperty(type = Texture_Manager_Prop)
    
def unregister():
    del bpy.types.Scene.Texture_Manager_Prop
    bpy.utils.unregister_class(Texture_Manager_Prop)
    bpy.utils.unregister_class(Texture_Manager_Panel)
    

if __name__ == "__main__":
    register()  