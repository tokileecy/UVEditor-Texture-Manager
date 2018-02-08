'''
Copyright (C) 2017
jim159093@gmial.com

Created by Stokes Lee

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
bl_info = {
    "name": "UVEditor Texture Manager",
    "author": "Stokes Lee",
    "version": (0, 2, 0),
    "blender": (2, 79, 0),
    "location": "UV > Properties Shelf",
    "category": "UV",
    "tracker_url": "https://github.com/StokesLee/UIEditor-Texture-Manager/issues",
}

import bpy
from bpy.types import PropertyGroup, Panel, AddonPreferences
from rna_prop_ui import PropertyPanel
from bpy.props import EnumProperty, BoolProperty
from bpy.app.handlers import persistent

class Manager():
    def __init__(self):
        self._last_active_object = None
    @property
    def active_is_update(self):
        return self._last_active_object != self.active_object
    @property
    def render_engine(self):
        return bpy.context.scene.render.engine

    @property
    def active_object(self):
        return bpy.context.scene.objects.active
    
    @property
    def material(self):
        if len(self.active_object.material_slots) > 0 :
            material = self.active_object.active_material
            return material
        return None

    @property
    def use_nodes(self):
        return self.material.use_nodes

    @property
    def uv_editor_areas(self):
        areas = bpy.context.screen.areas
        return [area for area in areas if area.type == 'IMAGE_EDITOR']

    @property
    def slot_textures(self):
        texture_slots = self.material.texture_slots
        filter_textures = []
        for texture in texture_slots:
            if (texture is not None) and (texture.texture.image is not None):
                exist = False
                for filter_texture in filter_textures:
                    if filter_texture.texture.image.name == texture.texture.image.name:
                        exist = True
                        break
                if not exist:
                    filter_textures.append(texture)
        return filter_textures
        # return [texture for texture in texture_slots if (texture is not None) if (texture.texture.image is not None) ]
    @property
    def slot_textures_item(self):
        textures = self.slot_textures
        return [(str(index), 
                textures[index].texture.image.name, 
                textures[index].texture.image.name) 
                for index in range(0, len(textures))]
    
    @property
    def texture_nodes(self):
        nodes = self.material.node_tree.nodes
        filter_nodes = []
        if self.render_engine == 'CYCLES':
            for node in nodes:
                if (node.type == 'TEX_IMAGE') and (node.image is not None):
                    exist = False
                    for filter_node in filter_nodes:
                        if node.image.name == filter_node.image.name:
                            exist = True
                            break
                    if not exist:
                        filter_nodes.append(node)
            return filter_nodes
            # return [node for node in nodes if (node.type == 'TEX_IMAGE') if (node.image is not None) ]
        elif self.render_engine == 'BLENDER_RENDER':
            for node in nodes:
                if (node.type == 'TEXTURE') and (node.texture.image is not None):
                    exist = False
                    for filter_node in filter_nodes:
                        if node.texture.image.name == filter_node.texture.image.name:
                            exist = True
                            break
                    if not exist:
                        filter_nodes.append(node)
            return filter_nodes
            # return [node for node in nodes if (node.type == 'TEXTURE') if (node.texture.image is not None)]

    @property
    def texture_nodes_item(self):
        nodes = self.texture_nodes
        if self.render_engine == 'CYCLES':
            return [(str(index), nodes[index].image.name, nodes[index].image.name) for index in range(0, len(nodes))]
        elif self.render_engine == 'BLENDER_RENDER':
            return [(str(index), 
                    nodes[index].texture.image.name, 
                    nodes[index].texture.image.name) 
                    for index in range(0, len(nodes))]

    def slot_textures_item_update(self, index):
        textures = self.slot_textures
        if len(textures) > index:
            areas = self.uv_editor_areas
            for area in areas:
                area.spaces.active.image = textures[index].texture.image
    
    def texture_nodes_item_update(self, index):
        texture_nodes = self.texture_nodes
        if len(texture_nodes) > index:
            areas = self.uv_editor_areas
            if self.render_engine == 'CYCLES':
                for area in areas:
                    area.spaces.active.image = texture_nodes[index].image
            elif self.render_engine == 'BLENDER_RENDER':
                for area in areas:
                    area.spaces.active.image = texture_nodes[index].texture.image
    
@persistent
def scene_update(context):
    manager = Texture_Manager_Panel.manager
    if manager.active_is_update:
        if manager.use_nodes:
            manager.texture_nodes_item_update(0)
        else:
            manager.slot_textures_item_update(0)
                
        manager._last_active_object = manager.active_object

class Texture_Manager_AddonPreferences(AddonPreferences):
    bl_idname = __name__
    Enable_AutoUpdate = BoolProperty(
            name="AutoUpdate",
            default=False,
            update = lambda self, context : self.register_update(self.Enable_AutoUpdate),
            )
    def register_update(self, register):
        if register:
            if not scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
                bpy.app.handlers.scene_update_post.append(scene_update)
        else:
            if scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
                bpy.app.handlers.scene_update_post.remove(scene_update)

    Enable_Engine = BoolProperty(
            name="Engine",
            default=True,
            )
    Enable_Material = BoolProperty(
            name="Material",
            default=True,
            )
    Enable_Use_nodes = BoolProperty(
            name="use_nodes",
            default=True,
            )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Panel")
        col.prop(self, "Enable_AutoUpdate")
        col.prop(self, "Enable_Engine")
        col.prop(self, "Enable_Material")
        col.prop(self, "Enable_Use_nodes")

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
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        col = layout.column()
        if addon_prefs.Enable_Engine:
            col.prop(context.scene.render, "engine")

        material = self.manager.material
        ob = context.object

        if addon_prefs.Enable_Material:
            if context.object is not None:
                is_sortable = (len(ob.material_slots) > 1)
                rows = 1
                if is_sortable:
                    rows = 4
                row = col.row()
                row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

        if material is not None:
            if addon_prefs.Enable_Use_nodes:
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
    bpy.utils.register_class(Texture_Manager_AddonPreferences)
    bpy.utils.register_class(Texture_Manager_Panel)
    bpy.utils.register_class(Texture_Manager_Prop)
    bpy.types.Scene.Texture_Manager_Prop = bpy.props.PointerProperty(type = Texture_Manager_Prop)
    
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    if addon_prefs.Enable_AutoUpdate:
        if not scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
            bpy.app.handlers.scene_update_post.append(scene_update)
    
def unregister():
    if scene_update.__name__ in [handler.__name__ for handler in bpy.app.handlers.scene_update_post]:
        bpy.app.handlers.scene_update_post.remove(scene_update)
    bpy.utils.unregister_class(Texture_Manager_AddonPreferences)
    del bpy.types.Scene.Texture_Manager_Prop
    bpy.utils.unregister_class(Texture_Manager_Prop)
    bpy.utils.unregister_class(Texture_Manager_Panel)
    

if __name__ == "__main__":
    register()  