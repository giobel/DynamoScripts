import math

import shape
import section

class BarLayer:
    """Describes how a layer of bars is arranged in a slab"""

    def __init__(self,sizes,spacing):
        self.sizes = sizes
        self.spacing = spacing

        assert len(self.sizes) > 0

        self.max_size = max(self.sizes)
        self.width = self.spacing * len(sizes)

    def create_bars(self,steel,width,depth):
        count = math.floor(width/self.width)

        result = []
        for i in range(0,count):
            for size in self.sizes:
                result.append(section.Bar(steel,size,depth))

        return result

class Slab:
    """A slab of concrete"""

    def __init__(self,concrete,steel,thickness):
        self.concrete = concrete
        self.steel = steel
        self.thickness = thickness

        #set these
        self.cover_top = 0
        self.cover_bot = 0
        self.aggregate_size = 0
        self.inner_layer = "Y"

        self.layers_x_top = []
        self.layers_x_bot = []

        self.layers_y_top = []
        self.layers_y_bot = []

        self.concrete_factor = 1
        self.steel_factor = 1

        #to be updated
        self.width_x = 1000
        self.width_y = 1000

        self.depths_x_top = []
        self.depths_y_top = []
        self.depths_x_bot = []
        self.depths_y_bot = []

        self.section_x = None
        self.section_y = None

    def update_widths(self):
        bar_width_x = 1
        for layer in self.layers_x_top:
            bar_width_x = max(bar_width_x,layer.width)
        for layer in self.layers_x_bot:
            bar_width_x = max(bar_width_x,layer.width)

        bar_width_y = 1
        for layer in self.layers_y_top:
            bar_width_y = max(bar_width_y,layer.width)
        for layer in self.layers_y_bot:
            bar_width_y = max(bar_width_y,layer.width)

        self.width_x = bar_width_x * math.ceil(1000 / bar_width_x)
        self.width_y = bar_width_y * math.ceil(1000 / bar_width_y)

    def update_depths(self):
        self.depths_x_top = []
        self.depths_x_bot = []
        self.depths_y_top = []
        self.depths_y_bot = []

        def update_depths_impl(layers,depths,cover,is_bottom):
            current_cover = cover

            #iterate through the layers in alternating directions to update the depths
            for i in range(0,max(len(layers[0]),len(layers[1]))):
                if i < len(layers[0]):
                    if is_bottom:
                        depths[0].append(self.thickness - (current_cover + layers[0][i].max_size / 2))
                    else:
                        depths[0].append(current_cover + layers[0][i].max_size / 2)
                    current_cover += layers[0][i].max_size
                elif i > 1:
                    max_size = max(layers[1][i-1].max_size,layers[1][i].max_size)

                    #add spacing Clause 7.4 -> A23.1 Clause 6.6.5
                    current_cover += max(
                        1.4*max_size,
                        1.4*self.aggregate_size,
                        30)

                if i < len(layers[1]):
                    if is_bottom:
                        depths[1].append(self.thickness - (current_cover + layers[1][i].max_size / 2))
                    else:
                        depths[1].append(current_cover + layers[1][i].max_size / 2)
                    current_cover += layers[1][i].max_size
                elif i+1 < len(layers[0]):
                    max_size = max(layers[0][i].max_size,layers[0][i+1].max_size)

                    #add spacing Clause 7.4 -> A23.1 Clause 6.6.5
                    current_cover += max(
                        1.4*max_size,
                        1.4*self.aggregate_size,
                        30)

        if self.inner_layer == "Y":
            update_depths_impl(
                [self.layers_x_top,self.layers_y_top],
                [self.depths_x_top,self.depths_y_top],
                self.cover_top,False)
            update_depths_impl(
                [self.layers_x_bot,self.layers_y_bot],
                [self.depths_x_bot,self.depths_y_bot],
                self.cover_bot,True)
        else:
            update_depths_impl(
                [self.layers_y_top,self.layers_x_top],
                [self.depths_y_top,self.depths_x_top],
                self.cover_top,False)
            update_depths_impl(
                [self.layers_y_bot,self.layers_x_bot],
                [self.depths_y_bot,self.depths_x_bot],
                self.cover_bot,True)

    def update_sections(self):
        self.update_widths()
        self.update_depths()

        bars_x = []
        for i in range(0,len(self.layers_x_top)):
            bars_x.extend(self.layers_x_top[i].create_bars(self.steel,self.width_x,self.depths_x_top[i]))
        for i in range(0,len(self.layers_x_bot)):
            bars_x.extend(self.layers_x_bot[i].create_bars(self.steel,self.width_x,self.depths_x_bot[i]))

        bars_y = []
        for i in range(0,len(self.layers_y_top)):
            bars_y.extend(self.layers_y_top[i].create_bars(self.steel,self.width_y,self.depths_y_top[i]))
        for i in range(0,len(self.layers_y_bot)):
            bars_y.extend(self.layers_y_bot[i].create_bars(self.steel,self.width_y,self.depths_y_bot[i]))

        self.section_x = section.Section(self.concrete,shape.Rectangle(self.width_x,self.thickness),bars_x)
        self.section_x.concrete_factor = self.concrete_factor
        self.section_x.steel_factor = self.steel_factor

        self.section_y = section.Section(self.concrete,shape.Rectangle(self.width_y,self.thickness),bars_y)
        self.section_y.concrete_factor = self.concrete_factor
        self.section_y.steel_factor = self.steel_factor
