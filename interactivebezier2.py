#!/usr/bin/env python

from pyprocessing import *
from copy import deepcopy

def chunk(lst, length, overlap=0):
    step = length-overlap
    result = []
    for i in range(len(lst)):
        if i*step + length > len(lst): break
        result.append(lst[i*step : i*step + length])
    return result

def flatten(list_of_lists):
    return [val for sublist in list_of_lists for val in sublist]

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255, 0,   0)
GREEN  = (0,   255, 0)
BLUE   = (0,   0,   255)

def set_fill_and_stroke_state(fill_color, stroke_color, stroke_weight):
    if fill_color:
        fill(*fill_color)
    else:
        noFill()

    if stroke_color:
        stroke(*stroke_color)
    else:
        noStroke()

    if stroke_weight:
        strokeWeight(stroke_weight)

WIDTH = 1000
HEIGHT = 800
SCALE = 20
ORIGIN = { 'x': 0.1, 'y': 2 }

def draw_ellipse(x, y, width, height, fill_color=None, stroke_color=None, stroke_weight=1):
    set_fill_and_stroke_state(fill_color, stroke_color, stroke_weight)
    ellipse((x+ORIGIN['x'])*SCALE, (y+ORIGIN['y'])*SCALE, width, height)

def draw_line(x1, y1, x2, y2, fill_color=None, stroke_color=None, stroke_weight=1):
    set_fill_and_stroke_state(fill_color, stroke_color, stroke_weight)
    line((x1+ORIGIN['x'])*SCALE, (y1+ORIGIN['y'])*SCALE,
            (x2+ORIGIN['x'])*SCALE, (y2+ORIGIN['y'])*SCALE)

def draw_axis(axis, level = 0, fill_color=None, stroke_color=None, stroke_weight=1):
    set_fill_and_stroke_state(fill_color, stroke_color, stroke_weight)
    if axis == 'x':
        line((level+ORIGIN['x'])*SCALE, 0,
                (level+ORIGIN['x'])*SCALE, screen.height)
    elif axis == 'y':
        line(0, (level+ORIGIN['y'])*SCALE,
             screen.width, (level+ORIGIN['y'])*SCALE)

def draw_grid(x0, y0, xscale, yscale):
    set_fill_and_stroke_state(None, (200, 200, 200), 0.1)
    x, y = x0*SCALE, y0*SCALE

    while(x > 0):
        line(x, 0, x, HEIGHT)
        x -= xscale

    while(x < WIDTH):
        line(x, 0, x, HEIGHT)
        x += xscale

    while(y > 0):
        line(0, y, WIDTH, y)
        y -= yscale

    while(y < HEIGHT):
        line(0, y, WIDTH, y)
        y += yscale

def draw_bezier(x1, y1, x2, y2, x3, y3, x4, y4, fill_color=None, stroke_color=None, stroke_weight=1):
    set_fill_and_stroke_state(fill_color, stroke_color, stroke_weight)
    bezier((x1+ORIGIN['x'])*SCALE, (y1+ORIGIN['y'])*SCALE,
            (x2+ORIGIN['x'])*SCALE, (y2+ORIGIN['y'])*SCALE,
            (x3+ORIGIN['x'])*SCALE, (y3+ORIGIN['y'])*SCALE,
            (x4+ORIGIN['x'])*SCALE, (y4+ORIGIN['y'])*SCALE)


class Scene:
    @property
    def breadth_first_traversal(self):
        """Iterator traverses a tree in breadth-first order.

        The first argument should be the tree root; visitable should be an
        iterable with all searchable nodes; children should be a function
        which takes a node and return an iterator of the node's children.
        """
        visited = []
        queue = deepcopy(self.children)
        while len(queue) > 0:
            node = queue.pop(0)
            visited.append(node)
            if node.children is not None:
                for child in node.children:
                    queue.append(child)
        return visited

    def __init__(self):
        self.children = []
        self.elements = sorted(self.breadth_first_traversal, key = lambda el: -el.zIndex)

    def update(self):
        self.elements = sorted(self.breadth_first_traversal, key = lambda el: -el.zIndex)

    def draw(self):
        for el in reversed(self.elements):
            el.update()
            el.draw()

    def add(self, element):
        self.children.append(element)
        self.update()

    def handleMousePressed(self, mousex, mousey):
        for el in self.elements:
            hovering, cursor = el.isHover(mousex, mousey)
            if hovering:
                el.select()
                return True
        return False

    def handleMouseMoved(self, mousex, mousey):
        for el in self.elements:
            hovering, cursor = el.isHover(mousex, mousey)
            if hovering:
                return hovering, cursor
        return False

    def handleMouseDragged(self, mousex, mousey, pmousex, pmousey):
        for el in self.elements:
            if el.isSelected:
                el.drag(mousex, mousey, pmousex, pmousey)

    def handleMouseReleased(self):
        for el in self.elements:
            el.release()


class Element:
    zIndex = -1
    children = None

    def __init__(self, parent):
        self.parent = parent
        self.isSelected = False

    def select(self):
        self.isSelected = True

    def release(self):
        self.isSelected = False

    def drag(self, mousex, mousey, pmousex, pmousey):
        pass

    def isHover(self, mousex, mousey):
        return False, False

    def update(self):
        self.parent.update()

    def draw(self):
        pass


class Grid(Element):
    zIndex = 1

    def drag(self, mousex, mousey, pmousex, pmousey):
        ORIGIN['x'] += (mousex - pmousex) / SCALE
        ORIGIN['y'] += (mousey - pmousey) / SCALE

    def isHover(self, mousex, mousey):
        return True, False

    def draw(self):
        background(255, 255, 255)
        draw_grid(ORIGIN['x'], ORIGIN['y'], SCALE, SCALE)
        draw_axis('x', 0, None, (200, 200, 200), 0.1)

class KeyframeCursor(Element):
    zIndex = 2
    WIDTH = 30

    def __init__(self, parent):
        super().__init__(parent)
        self.x = 1

    def drag(self, mousex, mousey, pmousex, pmousey):
        self.moveTo(mousex / SCALE - ORIGIN['x'])

    def moveTo(self, x):
        self.x = round(x)

    def isHover(self, mousex, mousey):
        return (dist((self.x+ORIGIN['x'])*SCALE, 0, mousex, 0) <= self.WIDTH), True

    def draw(self):
        background(255, 255, 255)
        draw_axis('x', self.x, None, (200, 200, 200), self.WIDTH)

class Point(Element):
    zIndex = 4
    RADIUS = 10

    def __init__(self, x, y, parent):
        super().__init__(parent)
        self.x, self.y = x, y

    def drag(self, mousex, mousey, pmousex, pmousey):
        self.moveTo(mousex / SCALE - ORIGIN['x'],
                    mousey / SCALE - ORIGIN['y'])

    def isHover(self, mousex, mousey):
        return ( dist((self.x+ORIGIN['x'])*SCALE , (self.y+ORIGIN['y'])*SCALE, mousex, mousey) <= self.RADIUS ), True

    def moveBy(self, dx, dy):
        self.x += dx
        self.y += dy

    def moveTo(self, x, y):
        if 'shift' in io_state['keyboard']:
            self.x = round(x)
        else:
            self.x = x
        self.y = y

    def draw(self):
        if self.isSelected:
            draw_ellipse(self.x, self.y, self.RADIUS, self.RADIUS, BLUE, BLUE, 1)
        else:
            draw_ellipse(self.x, self.y, self.RADIUS, self.RADIUS, None, BLUE, 1)


class Keyframe(Point):
    def __init__(self, handle_left_coord, keyframe_coord, handle_right_coord, parent, keyframe_type=None):
        super().__init__(*keyframe_coord, parent=parent)
        self.type = keyframe_type
        self.handle_left = Handle(*handle_left_coord, parent=self, handle_type='left')
        self.handle_right = Handle(*handle_right_coord, parent=self, handle_type='right')
        self.children = [self.handle_left, self.handle_right]

    def moveTo(self, x, y):
        dx = round(x) - self.x
        dy = y - self.y
        self.handle_left.moveBy(dx, dy)
        self.handle_right.moveBy(dx, dy)
        self.x = round(x)
        self.y = y

    def update(self):
        self.children = []
        if self.type != 'first':
            self.children.append(self.handle_left)
        if self.type != 'last':
            self.children.append(self.handle_right)

    def __repr__(self):
        return 'Keyframe of {bezier}'.format(bezier = self.parent)


class Handle(Point):
    def __init__(self, x, y, parent, handle_type):
        super().__init__(x, y, parent)
        self.type = handle_type

    def moveTo(self, x, y, recursive=True):
        if 'ctrl' in io_state['keyboard'] and recursive:
            if self.type == 'left':
                opposite = self.parent.handle_right
            else:
                opposite = self.parent.handle_left
            opposite.moveTo(2.0*self.parent.x - self.x,
                            2.0*self.parent.y - self.y,
                            recursive=False)
        if self.type == 'left':
            self.x = min(x, self.parent.x)
        else:
            self.x = max(x, self.parent.x)
        self.y = y

    def draw(self):
        draw_line(self.x, self.y, self.parent.x, self.parent.y, None, RED, 1)
        super().draw()


class Bezier(Element):
    zIndex = 3

    def __init__(self, keyframes, parent):
        super().__init__(parent)
        self.children = [ Keyframe(handle_left_coord, keyframe_coord, handle_right_coord, parent=self)
                            for (handle_left_coord, keyframe_coord, handle_right_coord) in keyframes ]

    def update(self):
        self.children.sort(key = lambda kf: kf.x)

        for kf in self.children:
            kf.type = 'center'

        self.children[0].type = 'first'
        self.children[-1].type = 'last'

        for kf in self.children:
            kf.update()

        self.parent.update()

    def draw(self):
        for kf1, kf2 in zip(self.children[:-1], self.children[1:]):
            norm = sqrt( (0.01 + (kf1.x - kf1.handle_right.x)**2 + (kf2.x-kf2.handle_left.x)**2) / (0.01 + (kf1.x-kf2.x)**2) )
            if norm >= 1:
                draw_bezier(kf1.x, kf1.y,
                            kf1.x + (kf1.handle_right.x-kf1.x) / norm, kf1.y + (kf1.handle_right.y-kf1.y) / norm,
                            kf2.x + (kf2.handle_left.x-kf2.x) / norm,  kf2.y + (kf2.handle_left.y-kf2.y) / norm,
                            kf2.x, kf2.y,
                            None, BLACK, 2)
                #draw_ellipse(kf1.x + (kf1.handle_right.x-kf1.x) / norm, kf1.y + (kf1.handle_right.y-kf1.y) / norm, 5, 5, BLACK, BLACK, 0)
                #draw_ellipse(kf2.x + (kf2.handle_left.x-kf2.x) / norm, kf2.y + (kf2.handle_left.y-kf2.y) / norm, 5, 5, BLACK, BLACK, 0)
            else:
                draw_bezier(kf1.x, kf1.y,
                            kf1.handle_right.x, kf1.handle_right.y,
                            kf2.handle_left.x,  kf2.handle_left.y,
                            kf2.x, kf2.y,
                            None, BLACK, 2)


#########################################################

io_state = { 'mouse': set(), 'keyboard': set() }

def setup():
    global scene

    size(WIDTH, HEIGHT)
    noFill()
    rectMode(CENTER)
    ellipseMode(CENTER)

    scene = Scene()
    scene.add(Grid(parent = scene))

    scene.add(KeyframeCursor(parent = scene))

    scene.add(Bezier( [((-3.2945265769958496, -2.0), (1.0, 0.0), (5.29452657699585, 0.0)),
                                  ((7.70547342300415, 2.0), (12.0, 0.0), (16.684938430786133, 0.0)),
                                  ((19.315061569213867, -2.0), (24.0, 0.0), (28.684938430786133, 0.0))], parent = scene))

    scene.add(Bezier( [((-3.2945265769958496, 8.0), (1.0, 0.0), (5.29452657699585, 0.0)),
                                ((7.70547342300415, 10.0), (12.0, 0.0), (16.684938430786133, 0.0)),
                                ((19.315061569213867, 8.0), (24.0, 0.0), (28.684938430786133, 0.0))], parent = scene))

def draw():
    scene.draw()

    if 'dragging' in io_state['mouse']:
        cursor(MOVE)
    elif 'hovering' in io_state['mouse']:
        cursor(HAND)
    else:
        cursor(ARROW)

def mousePressed():
    if scene.handleMousePressed(mouse.x, mouse.y):
        io_state['mouse'].add('dragging')

def mouseMoved():
    hovering, cursor = scene.handleMouseMoved(mouse.x, mouse.y)
    if cursor:
        io_state['mouse'].add('hovering')
    else:
        io_state['mouse'].discard('hovering')

def mouseDragged():
    if 'dragging' in io_state['mouse']:
        scene.handleMouseDragged(mouse.x, mouse.y, pmouse.x, pmouse.y)

def mouseReleased():
    if 'dragging' in io_state['mouse']:
        io_state['mouse'].discard('dragging')
        scene.handleMouseReleased()

def keyPressed():
    global SCALE, ORIGIN

    CTRL = 65507
    SHIFT = 65505
    PLUS = 65451
    MINUS = 65453

    if key.char == CODED:
        if key.code == CTRL:
            io_state['keyboard'].add('ctrl')
        elif key.code == SHIFT:
            io_state['keyboard'].add('shift')
        elif key.code == PLUS:
            SCALE += 0.5
        elif key.code == MINUS:
            SCALE -= 0.5
    elif key.char == 'a':
        io_state['keyboard'].add('a')

def keyReleased():
    io_state['keyboard'].clear()

run()
