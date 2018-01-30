bl_info = {
    "name": "Update_Texture",
    "author": "Stokes Lee",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "UV/Image Editor > Header",
    "category": "3D View"
}

import bpy

class Update_Texture_Editor(bpy.types.Operator):
    bl_idname = "vw.get_node_texture"
    bl_label = "UV"
    
    def get_image_node(self) :
        material = self.get_Material()
        nodes = material.node_tree.nodes
        for node in nodes :
            if node.type == 'TEX_IMAGE' :
                if  len(node.outputs['Color'].links) > 0 :
                    base = node.outputs['Color'].links[0].to_node.bl_rna.base
                    if base == bpy.types.ShaderNode.bl_rna :
                        return node
        return None
        
    def get_image_area(self) :
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                return area
        return None
    
    def set_image_area(self,b):
        material = self.get_Material()
        if material is not None:
            image_node = self.get_image_node()
            if image_node is not None :
                b.spaces.active.image = image_node.image
    
    def get_Material(self) :
        obj = bpy.context.scene.objects.active
        if len(obj.material_slots) > 0 :
            material = obj.material_slots[0].material
            return material
        return None
    """
    def get_Material_Output(self, material) :
        nodes = material.node_tree.nodes
        for node in nodes :
            if node.type == 'OUTPUT_MATERIAL' :
                return node
        return None
    
    def get_image_node(self, output_node) :
        if len(output_node.inputs['Surface'].links) > 0 :
            from_node = output_node.inputs['Surface'].links[0].from_node
            if from_node.bl_rna.base == bpy.types.ShaderNode.bl_rna :
                if len(from_node.inputs[0].links) > 0 :
                    from_node2 = from_node.inputs[0].links[0].from_node
                    if from_node2.type == 'TEX_IMAGE' :
                        return from_node2
        return None
   """
    def set_image(self) :
        b = self.get_image_area()
        if b is not None :
            self.set_image_area(b)

    def execute(self, context):
        self.set_image()
        return {'FINISHED'}
    
def draw_func(self, context):
    layout = self.layout
    layout.operator("vw.get_node_texture")
    
def register():
    bpy.utils.register_class(Update_Texture_Editor)
    bpy.types.IMAGE_HT_header.prepend(draw_func)
    
def unregister():
    bpy.utils.unregister_class(Update_Texture_Editor)
    bpy.types.IMAGE_HT_header.remove(draw_func)

if __name__ == "__main__":
    register()  