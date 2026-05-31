bl_info = {
    "name": "The Packstabber's Blues",
    "author": "Captain Northstar",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "File > The Packstabber's Blues",
    "description": "Collects all PNGs used in the current scene into a folder of your choice.",
    "category": "Import-Export",
}

import bpy
import os
import shutil


class PACKSTABBER_OT_collect_textures(bpy.types.Operator):
    bl_idname = "packstabber.collect_textures"
    bl_label = "Collect Scene Textures"
    bl_description = "Copy all PNGs used in the current scene into a selected folder"

    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        output_folder = self.directory

        used_images = set()

        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH':
                continue
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if not mat or not mat.use_nodes:
                    continue
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        used_images.add(node.image)

        if not used_images:
            self.report({'WARNING'}, "No PNG textures found on scene objects.")
            return {'FINISHED'}

        self.report({'INFO'}, f"Found {len(used_images)} texture(s). Searching C: drive...")

        not_found = []

        for image in used_images:
            filename = os.path.basename(image.filepath).strip()

            abs_path = bpy.path.abspath(image.filepath)
            if os.path.isfile(abs_path) and abs_path.lower().endswith('.png'):
                dest = os.path.join(output_folder, os.path.basename(abs_path))
                if os.path.abspath(abs_path) != os.path.abspath(dest):
                    shutil.copy2(abs_path, dest)
                    print(f"[Packstabber] Copied (direct): {abs_path}")
                else:
                    print(f"[Packstabber] Already in place: {filename}")
                continue

            if not filename.lower().endswith('.png'):
                print(f"[Packstabber] Skipping non-PNG: {filename}")
                continue

            found = False
            for root, dirs, files in os.walk("C:\\"):
                dirs[:] = [d for d in dirs if d not in (
                    'Windows', 'System32', '$Recycle.Bin', 'ProgramData',
                    'Program Files', 'Program Files (x86)'
                )]
                for f in files:
                    if f.lower() == filename.lower():
                        src = os.path.join(root, f)
                        dest = os.path.join(output_folder, f)
                        shutil.copy2(src, dest)
                        print(f"[Packstabber] Copied: {src} -> {dest}")
                        found = True
                        break
                if found:
                    break

            if not found:
                not_found.append(filename)
                print(f"[Packstabber] NOT FOUND: {filename}")

        if not_found:
            self.report({'WARNING'}, f"Done. {len(not_found)} file(s) not found — check console.")
        else:
            self.report({'INFO'}, "Done. All textures collected successfully.")

        return {'FINISHED'}

    def invoke(self, context, event):
        blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Save your .blend file first.")
            return {'CANCELLED'}
        self.directory = os.path.dirname(blend_path)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(
        PACKSTABBER_OT_collect_textures.bl_idname,
        text="The Packstabber's Blues",
        icon='PACKAGE'
    )


def register():
    bpy.utils.register_class(PACKSTABBER_OT_collect_textures)
    bpy.types.TOPBAR_MT_file.append(menu_func)


def unregister():
    bpy.utils.unregister_class(PACKSTABBER_OT_collect_textures)
    bpy.types.TOPBAR_MT_file.remove(menu_func)


if __name__ == "__main__":
    register()