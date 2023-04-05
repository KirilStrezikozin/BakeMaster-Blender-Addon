import bpy
from bpy.props import *

# order of events:
# 1 - OT modal
# 2 - prop update
# 3 - ui


def add_item(context, name):
    new_item = context.scene.my_collection.add()
    new_item.index = len(context.scene.my_collection) - 1
    new_item.name_old = name
    new_item.name = name


def drop_prompt_add_container(context):
    if context.scene.drop_prompt_collection_name == "":
        return
    add_item(context, context.scene.drop_prompt_collection_name)
    context.scene.drop_prompt_collection_name = ""


def drop_prompt_add_objects(context):
    if not context.scene.drop_prompt_allow_add:
        return
    #print("adding")
    context.scene.drop_prompt_allow_add = False
    for object in context.selected_objects:
        add_item(context, object.name)
    else:
        drop_prompt_add_container(context)

    context.scene.my_index = len(context.scene.my_collection) - 1


def remove_dropped_item(item, context):
    #print(item.name)
    if context.scene.drop_prompt_allow_add:
        #print("NOPE")
        return True
    #print("TT", context.scene.drop_prompt_allow_add)
    context.scene.drop_prompt_allow_add = False
    #objects = [object for object in context.selected_objects if object.name == item.name and object.type == 'MESH']

    names = []
    add_objects = False
    for object in context.selected_objects:
        if object.type == 'MESH':
            names.append(object.name)
        if object.name == item.name:
            add_objects = True
    if add_objects:
        for name in names:
            add_item(context, name)
        context.scene.my_index = len(context.scene.my_collection) - 1
        return False
        
    #if len(objects) != 0:
        #add_item(context, objects[0].name)
        #item.has_drop_prompt = False
        #item.name = object.name
        #return False
    collections = [coll for coll in bpy.data.collections if coll.name == item.name]
    if len(collections) != 0:
    #if context.collection is not None and item.name == context.collection.name:
        #item.has_drop_prompt = False
        #self.name = collections[0].name
        add_item(context, collections[0].name)
        context.scene.my_index = len(context.scene.my_collection) - 1
        return False
    return True

def name_update(self, context):
    #print("name update called: " + self.name + " " + self.name_old)
    #print("'" + self.name_old + "' " + str(self.has_drop_prompt))
    
    #if self.name_old == "":
        #print(self.name)
        #drop_prompt_add_objects(context)
    
    if self.name_old != self.name:
        self.name_old = self.name
        self.has_drop_prompt = remove_dropped_item(self, context)
    if self.has_drop_prompt:
        #print("REMOVED")
        context.scene.my_collection.remove(self.index)
        if context.scene.my_index >= len(context.scene.my_collection):
            context.scene.my_index = len(context.scene.my_collection) - 1
            
def drag_ticker_update(self, context):
    #for item in context.scene.my_collection:
    #    if item.index == self.index:
    #        continue
    #    item.has_drop_prompt = False
    #try:
    #    print(self.name)
    #except RecursionError:
    #    pass
    
    if context.scene.item_drag_possible:
        if context.scene.item_drag_index == -1:
            context.scene.my_index = self.index
            context.scene.item_drag_index = self.index
            self.has_drag_prompt = True
            return
            #context.scene.item_drag_ticker_updator_index = -1
        #context.scene.item_drag_possible = False
        if context.scene.dragged_item_new_index != -1:
            context.scene.my_collection[context.scene.dragged_item_new_index].drag_placeholder = False
        context.scene.dragged_item_new_index = self.index
        if context.scene.item_drag_index != self.index:
            self.drag_placeholder = True
        #if self.index == context.scene.item_drag_index:
            #return
        if self.drag_ticker == context.scene.my_collection[context.scene.item_drag_index].drag_ticker:
            self.drag_ticker = not context.scene.my_collection[context.scene.item_drag_index].drag_ticker
        #print("Update", self.index)
            
            
        #for item in context.scene.my_collection:
        #    if item.index == self.index:
        #        continue
        #    if item.drag_ticker == self.drag_ticker:
        #        item.drag_ticker = not self.drag_ticker
        
        return
    
    context.scene.my_index = self.index
    self.has_drag_prompt = False
    #context.scene.item_drag_possible = False
        

class MyItem(bpy.types.PropertyGroup):
    name: StringProperty(
        default="",
        update=name_update)
        
    name_old: StringProperty(default="")
    
    index: IntProperty(default=-1)
    
    has_drop_prompt: BoolProperty(default=False)
    
    has_drag_prompt: BoolProperty(default=False)
    drag_ticker: BoolProperty(
        default=False,
        update=drag_ticker_update)
        
    drag_empty: BoolProperty(default=False)
    drag_placeholder: BoolProperty(default=False)
    

class MyList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        #print("ui")
        
        col = layout.column(align=True)
        
        if item.drag_placeholder and context.scene.item_drag_possible:
            drag_placeholder = col.row().box()
            drag_placeholder.label(text="")
            drag_placeholder.scale_y = 0.1
        
        row = col.row(align=True)

        if item.drag_empty:
            if context.scene.dragged_item_new_index == -1:
                return
            row.alignment = 'LEFT'
            row.prop(item, "drag_ticker", text="...", emboss=False, toggle=True)
            #row.label(text=str(item.drag_ticker))
            return
            
        if item.has_drop_prompt:
            row.prop(item, "name", text="", emboss=True, translate=False, icon_value=icon)
            return
        
        if context.scene.item_drag_possible and not item.has_drag_prompt and context.scene.dragged_item_new_index != -1:
            row.active = False
            
        row.alignment = 'LEFT'
        try:
            context.scene.objects[item.name]
        except KeyError:
            icon = 'OUTLINER_COLLECTION'
        else:
            icon = 'OUTLINER_OB_MESH'
        row.prop(item, "drag_ticker", text=item.name, emboss=False, toggle=True, icon=icon)
    
    
class MY_OT_Mouse(bpy.types.Operator):
    bl_idname = "myaddon.mouse_ot"
    bl_label = "Mouse"
    
    _handler = None
    
    @classmethod
    def is_running(cls):
        return cls._handler is not None
    
    @classmethod
    def poll(cls, context):
        if cls._handler is not None:
            return False
        return True
    
    def reset_props(self, context):
        self.show_drop_prompt = False
        self.wait_exit = False
        self.query_remove_prompts = False
        context.scene.drop_prompt_allow_add = False
        context.scene.query_remove_prompts = False
        
        context.scene.item_drag_possible = False
        context.scene.item_drag_index = -1
        context.scene.dragged_item_new_index = -1
        self.item_drag_has_movement = False
    
    def start(self, context):
        cls = self.class
        wm = context.window_manager
        wm.modal_handler_add(self)
        cls.handler = self
        self.reset_props(context)
        context.scene.uilist_walk_is_running = True
    
    def exit(self, context):
        cls = self.class
        cls.handler = None
        self.reset_props(context)
        context.scene.uilist_walk_is_running = True
        
    def check_exit(self, context, event):
        if event.type not in {'RIGHTMOUSE', 'ESC'}:
            return False
        self.exit(context)
        self.report({'INFO'}, "Exit")
        return True
    
    def outliner_get_data(self, context, event):
        for area in context.screen.areas:
            if area is None:
                continue
            if area.type != 'OUTLINER':
                continue
            return area.x, area.y, area.height, area.width
        return -1, -1, -1, -1
    
    def outliner_has_valid_event(self, context, event):
        x, y, height, width = self.outliner_get_data(context, event)
        if x == -1:
            return False
        return all([x <= event.mouse_x <= x + width,
                y <= event.mouse_y <= y + height])
                
    def is_drop_available(self, context, event):
        if self.show_drop_prompt:
            return True
        elif event.type != 'LEFTMOUSE':
            self.hide_drop_prompt(context)
            return False
        elif not self.outliner_has_valid_event(context, event):
            return False
        return True
    
    def is_curson_in_region(self, context, region, event):
        if all([region.x <= event.mouse_x <= region.x + region.width,
                region.y <= event.mouse_y <= region.y + region.height]):
            #print("curson in addon region")
            #context.scene.item_drag_possible = True
            return True
        else:
            return False
    
    def is_drag_available(self, context, event):
        if context.scene.item_drag_possible:
            return True
        elif event.type != 'LEFTMOUSE':
            return False
        elif context.area is None:
            return False
        elif context.area.type != 'VIEW_3D':
            return False
        for region in context.area.regions:
            if region is None:
                continue
            if region.type != 'UI':
                continue
            return self.is_curson_in_region(context, region, event)
        return False
    
    def draw_drop_prompt(self, context):
        if self.show_drop_prompt:
            return
        
        #print("AA", context.scene.drop_prompt_allow_add)
        context.scene.drop_prompt_allow_add = True
        label = "Add new?"
        
        #print(True)
        self.show_drop_prompt = True
        self.wait_exit = False
        new_item = context.scene.my_collection.add()
        new_item.index = len(context.scene.my_collection) - 1
        new_item.name_old = label
        new_item.name = label
        #new_item.name_old = ""
        new_item.has_drop_prompt = True
        context.scene.my_index = len(context.scene.my_collection) - 1
        
    def remove_items_with_drop_prompt(self, context):
        to_remove = []
        for item in context.scene.my_collection:
            name_update(item, context)
            if not item.has_drop_prompt:
                continue
            #print("r")
            to_remove.append(item.index)
        for index in reversed(to_remove):
            context.scene.my_collection.remove(index)
        self.query_remove_prompts = False
        #print("RR", context.scene.drop_prompt_allow_add)
        context.scene.query_remove_prompts = False
        context.scene.drop_prompt_allow_add = False
        
    def hide_drop_prompt(self, context):
        # print(False)
        if self.show_drop_prompt:
            self.query_remove_prompts = True
        self.show_drop_prompt = False
        self.wait_exit = False
        
    def item_drag_revert(self, context):
        context.scene.item_drag_possible = False
        context.scene.item_drag_index = -1
        context.scene.dragged_item_new_index = -1
        self.item_drag_has_movement = False
        to_remove = []
        index = 0
        for item in context.scene.my_collection:
            item.has_drag_prompt = False
            #item.drag_placeholder = False
            if item.drag_empty:
                to_remove.append(item.index)
                continue
            item.index = index
            index += 1
        for index in reversed(to_remove):
            context.scene.my_collection.remove(index)
                
            
    def item_drag_init(self, context):
        index = context.scene.my_index
        self.item_drag_revert(context)
        
        drag_empty = context.scene.my_collection.add()
        drag_empty.name_old = "Here"
        drag_empty.name = "Here"
        drag_empty.drag_empty = True
        drag_empty.index = len(context.scene.my_collection) - 1
            
        for item in context.scene.my_collection:
            item.drag_ticker = False
        context.scene.my_index = index
        context.scene.item_drag_possible = True
    
    def modal(self, context, event):
        #print(event.type, event.value)
        #print(context.scene.drop_prompt_allow_add)
        #if event.type != self.event_type and event.value != 'NOTHING':
        #    print(event.type, event.value)
        #    self.event_type = event.type
        #if context.area is not None:
        #    if context.area.type != self.area_type:
        #        self.area_type = context.area.type
        #        print(self.area_type)
        #else:
        #    self.area_type = 'NONE'
        #    print(self.area_type)
        
        #print("M", event.mouse_x, event.mouse_y)
        
        # skip timer events
        # otherwise item drag gets finished instantly occasionally
        if 'TIMER' in event.type:
            return {'PASS_THROUGH'}
        
        if self.query_remove_prompts:
            self.remove_items_with_drop_prompt(context)
            
        if context.scene.item_drag_possible and context.scene.item_drag_index == -1:
            self.item_drag_revert(context)
            
        if all([context.scene.item_drag_possible,
                context.scene.item_drag_index != -1,
                context.scene.dragged_item_new_index != -1]):

            #print(context.scene.item_drag_index, context.scene.dragged_item_new_index)
            if context.scene.dragged_item_new_index > context.scene.item_drag_index:
                new_index = context.scene.dragged_item_new_index - 1
            else:
                new_index = context.scene.dragged_item_new_index
            context.scene.my_collection.move(context.scene.item_drag_index, new_index)
            context.scene.my_index = new_index
            index = 0
            for item in context.scene.my_collection:
                item.drag_placeholder = False
                item.index = index
                index += 1
            self.item_drag_revert(context)
            #print("GDHGHGF")
            
        if self.check_exit(context, event):
            #print("finish process")
            return {'FINISHED'}
        
        is_drop_available = self.is_drop_available(context, event)
        is_drag_available = self.is_drag_available(context, event)
        print(is_drop_available, is_drag_available, context.scene.item_drag_possible)
        if not any([is_drop_available, is_drag_available]) and not context.scene.item_drag_possible:
            return {'PASS_THROUGH'}
        
        if not self.wait_exit:    
            if event.value == 'PRESS':
                if is_drop_available:
                    self.item_drag_revert(context)
                    self.draw_drop_prompt(context)
                elif is_drag_available:
                    self.hide_drop_prompt(context)
                    self.item_drag_init(context)

            elif event.value in ['CLICK', 'RELEASE']:
                self.hide_drop_prompt(context)
                self.item_drag_revert(context)
        
            if self.show_drop_prompt and event.value == 'CLICK_DRAG':
                if is_drop_available:
                    self.item_drag_revert(context)
                    self.draw_drop_prompt(context)
                elif is_drag_available:
                    self.hide_drop_prompt(context)
                    self.item_drag_init(context)

                self.wait_exit = True
            return {'PASS_THROUGH'}
        
        if 'MOUSEMOVE' not in event.type:
            #print(event.type)
            self.item_drag_revert(context)
            self.hide_drop_prompt(context)
            return {'PASS_THROUGH'}
        
        self.wait_exit = True
        if not context.scene.item_drag_possible:
            self.show_drop_prompt = True   
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        #print("invoked")
        if self.poll(context) is False:
            return {'CANCELLED'}
        #print("start process")
        self.start(context)
        
        #for i in reversed(range(len(context.scene.my_collection))):
        #    context.scene.my_collection.remove(i)
        return {'RUNNING_MODAL'}

class MY_PT_Panel(bpy.types.Panel):
    bl_idname = "MY_PT_Panel"
    bl_label = "My Panel"
    bl_category = "My Addon"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("myaddon.mouse_ot", text="", icon='MOUSE_LMB_DRAG')
        col.row().prop(context.scene, "it", expand=True)
        col.template_list("MyList", "", context.scene, "my_collection", context.scene, "my_index")

