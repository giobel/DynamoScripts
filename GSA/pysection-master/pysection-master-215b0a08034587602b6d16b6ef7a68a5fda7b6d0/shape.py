import math

class Shape:
    """A shape compressed to 1 dimension"""

    def __init__(self,offset=0):
        self.offset = offset

    def area(self):
        return 0

    def area_slice(self,start,end):
        return 0

    def limits(self):
        return 0, 0

    def centroid(self):
        return 0

    def centroid_slice(self,start,end):
        return 0

    def reflect(self): #returns itself reflected about the 0 axis
        return Shape(-self.offset)

    def shift(self,distance): #shifts the offset by the stated amount
        self.offset += distance

class Rectangle(Shape):
    """A rectangle"""

    def __init__(self,width,height,offset=0):
        Shape.__init__(self,offset)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def area_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.height < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.height, end-self.offset)

        return self.width * (end - start)

    def limits(self):
        return self.offset, self.offset + self.height

    def centroid(self):
        return self.offset + self.height / 2

    def centroid_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.height < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.height, end-self.offset)

        return self.offset + (end + start) / 2

    def reflect(self): #returns itself reflected about the 0 axis
        return Rectangle(self.width,self.height,-self.offset-self.height)

class Circle(Shape):
    """A circle"""

    def __init__(self,diameter,offset=0):
        Shape.__init__(self,offset)
        self.diameter = diameter
        self.radius = self.diameter / 2

    def area(self):
        return math.pi * self.radius * self.radius

    def area_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.diameter < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.diameter, end-self.offset)

        return self.segment_area(end) - self.segment_area(start)

    def segment_area(self,x):
        #the area of a sector minus the area enclosed by its chord and radii
        #x is the distance from the top of the circle (not from the origin)
        #https://en.wikipedia.org/wiki/Circular_sector

        height = self.radius - x
        halfchord = math.sqrt(2 * self.radius * x - x*x)
        angle = math.acos(1-x/self.radius)

        #area = sector area - triangle area

        return angle*self.radius*self.radius - halfchord*height

    def limits(self):
        return self.offset, self.offset + self.diameter

    def centroid(self):
        return self.offset + self.diameter / 2

    def centroid_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.diameter < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.diameter, end-self.offset)

        area_start = self.segment_area(start)
        area_end = self.segment_area(end)

        area_total = area_end-area_start

        if area_total == 0:
            return 0

        centroid_start = self.segment_centroid(start)
        centroid_end = self.segment_centroid(end)

        return self.offset + (area_end*centroid_end - area_start*centroid_start) / area_total

    def segment_centroid(self,x):
        #the centroid of a sector minus the area enclosed by its chord and radii
        #x is the distance from the top of the circle (not from the origin)
        #https://en.wikipedia.org/wiki/Circular_sector

        height = self.radius - x
        halfchord = math.sqrt(2 * self.radius * x - x*x)
        angle = math.acos(1-x/self.radius)

        #centroid = radius - (2/3 halfchord^3) / area
        #from: https://en.wikipedia.org/wiki/List_of_centroids

        area = angle*self.radius*self.radius - halfchord*height

        if area == 0:
            return 0

        return self.radius - 2 / 3 * math.pow(halfchord,3) / area

    def reflect(self): #returns itself reflected about the 0 axis
        return Circle(self.diameter,-self.offset-self.diameter)

class TriangleNeg(Shape):
    """A triangle pointing towards the negative"""
    #
    #        *-------*
    #         \     /
    #   ^      \   /
    #   |       \ /
    #   0        *
    #

    def __init__(self,base,height,offset=0):
        Shape.__init__(self,offset)
        self.base = base
        self.height = height

    def area(self):
        return self.base * self.height / 2

    def area_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.height < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.height, end-self.offset)

        return (end*end - start*start) * self.base/self.height / 2

    def limits(self):
        return self.offset, self.offset + self.height

    def centroid(self):
        return self.offset + self.height * 2 / 3

    def centroid_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.height < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.height, end-self.offset)

        area_start = start*start * self.base/self.height / 2
        area_end = end*end * self.base/self.height / 2

        area_total = area_end-area_start

        if area_total == 0:
            return 0

        centroid_start = start * 2 / 3
        centroid_end = end * 2 / 3

        return self.offset + (area_end*centroid_end - area_start*centroid_start) / area_total

    def reflect(self): #returns itself reflected about the 0 axis
        return TrianglePos(self.base,self.height,-self.offset-self.height)

class TrianglePos(Shape):
    """A triangle pointing towards the positive"""
    #
    #            *
    #           / \
    #   ^      /   \
    #   |     /     \
    #   0    *-------*
    #

    def __init__(self,base,height,offset=0):
        Shape.__init__(self,offset)
        self.base = base
        self.height = height

    def area(self):
        return self.base * self.height / 2

    def area_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.height < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.height, end-self.offset)

        h1 = self.height - start
        h2 = self.height - end

        return (h1*h1 - h2*h2) * self.base/self.height / 2

    def limits(self):
        return self.offset, self.offset + self.height

    def centroid(self):
        return self.offset + self.height / 3

    def centroid_slice(self,start,end):
        #ensure start and end are in order
        if end < start:
            return self.area_slice(end,start)

        #area is 0 if slice is outside of shape
        if end < self.offset or self.offset + self.height < start:
            return 0

        #clamp start and end to the limits of the shape
        start = max(0, start-self.offset)
        end = min(self.height, end-self.offset)

        h1 = self.height - start
        h2 = self.height - end

        area_1 = h1*h1 * self.base/self.height / 2
        area_2 = h2*h2 * self.base/self.height / 2

        area_total = area_1-area_2

        if area_total == 0:
            return 0

        centroid_1 = start + h1 / 3
        centroid_2 = end + h2 / 3

        return self.offset + (area_1*centroid_1 - area_2*centroid_2) / area_total

    def reflect(self): #returns itself reflected about the 0 axis
        return TriangleNeg(self.base,self.height,-self.offset-self.height)

class Compound(Shape):
    """A group of shapes forming a larger shape"""

    def __init__(self,fills,holes=None,offset=0):
        if holes == None:
            holes = []

        Shape.__init__(self,offset)
        self.fills = fills
        self.holes = holes

    def area(self):
        result = 0

        for fill in self.fills:
            result += fill.area()

        for hole in self.holes:
            result -= hole.area()

        return result

    def area_slice(self,start,end):
        start -= self.offset
        end -= self.offset

        result = 0

        for fill in self.fills:
            result += fill.area_slice(start,end)

        for hole in self.holes:
            result -= hole.area_slice(start,end)

        return result

    def limits(self):
        if not self.fills:
            return 0, 0

        lower = []
        upper = []

        for fill in self.fills:
            l, u = fill.limits()

            lower.append(l)
            upper.append(u)

        return min(lower)+self.offset, max(upper)+self.offset

    def centroid(self):
        if not self.fills:
            return 0

        total = 0
        area = 0

        for fill in self.fills:
            c = fill.centroid()
            a = fill.area()

            total += c*a
            area += a

        for hole in self.holes:
            c = hole.centroid()
            a = -hole.area()

            total += c*a
            area += a

        if area == 0:
            return 0

        return self.offset + total / area

    def centroid_slice(self,start,end):
        if not self.fills:
            return 0

        start -= self.offset
        end -= self.offset

        total = 0
        area = 0

        for fill in self.fills:
            c = fill.centroid_slice(start,end)
            a = fill.area_slice(start,end)

            total += c*a
            area += a

        for hole in self.holes:
            c = hole.centroid_slice(start,end)
            a = -hole.area_slice(start,end)

            total += c*a
            area += a

        if area == 0:
            return 0

        return self.offset + total / area

    def reflect(self): #returns itself reflected about the 0 axis
        fills = []
        holes = []

        for fill in self.fills:
            fills.append(fill.reflect())

        for hole in self.holes:
            holes.append(hole.reflect())

        return Compound(fills,holes,-self.offset)
