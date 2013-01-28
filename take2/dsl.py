from linsys import LinEq, LinVar
import itertools


class BaseNode(object):
    _counter = itertools.count()
    
    def __init__(self):
        self.id = self._counter.next()
        self.width_constraint = None
        self.height_constraint = None
        self.w = LinVar("_w%d" % (self.id,), "cons")
        self.h = LinVar("_h%d" % (self.id,), "cons")

    def get_constraints(self):
        if self.width_constraint is not None:
            yield LinEq(self.w, self.width_constraint)
        if self.height_constraint is not None:
            yield LinEq(self.h, self.height_constraint)

    def X(self, width = None, height = None):
        if width is not None:
            self.width_constraint = width
        if height is not None:
            self.height_constraint = height
        return self
    def __or__(self, other):
        return HLayoutNode.join(self, other)
    def __sub__(self, other):
        return VLayoutNode.join(self, other)
    def __neg__(self):
        return self

    def _repr_dims(self, text):
        if self.width_constraint or self.height_constraint:
            text += ".X(%r, %r)" % (self.width_constraint, self.height_constraint)
        return text


#=======================================================================================================================
# Layouts
#=======================================================================================================================
class LayoutNode(BaseNode):
    SYMBOL = None
    
    def __init__(self, children):
        BaseNode.__init__(self)
        self.children = children
        self.total = LinVar("_t%d" % (self.id,), "cons")
        self.scroll = LinVar("_s%d" % (self.id,), "padding")

    def __repr__(self):
        return self._repr_dims(self.SYMBOL.join(("(%r)" if isinstance(child, LayoutNode) else "%r") % (child,) 
            for child in self.children))

    @classmethod
    def join(cls, lhs, rhs):
        if isinstance(lhs, cls) and isinstance(rhs, cls):
            lhs.children.extend(rhs.children)
            return lhs
        elif isinstance(lhs, cls):
            lhs.children.append(rhs)
            return lhs
        elif isinstance(rhs, cls):
            rhs.children.insert(0, lhs)
            return rhs
        else:
            return cls([lhs, rhs])
    @classmethod
    def foreach(cls, iterable):
        return cls(list(iterable))
    
    @classmethod
    def _get_padder(cls, child):
        return LinVar("_p%d" % (child.id,), "padding")
    @classmethod
    def _get_offset(cls, child):
        return LinVar("_o%d" % (child.id,), "offset")

    def get_constraints(self):
        for cons in BaseNode.get_constraints(self):
            yield cons
        for child in self.children:
            for cons in child.get_constraints():
                yield cons

class HLayoutNode(LayoutNode):
    SYMBOL = " | "
    
    def get_constraints(self):
        for cons in LayoutNode.get_constraints(self):
            yield cons
        for i, child in enumerate(self.children):
            yield LinEq(self._get_offset(child), sum(child.w for child in self.children[:i]))
        total = sum(child.w for child in self.children)
        yield LinEq(self.total, total)
        yield LinEq(self.w, self.total + self.scroll)
        for child in self.children:
            yield LinEq(self.h, child.h + self._get_padder(child))

class VLayoutNode(LayoutNode):
    SYMBOL = "\n---\n"

    def get_constraints(self):
        for cons in LayoutNode.get_constraints(self):
            yield cons
        for i, child in enumerate(self.children):
            yield LinEq(self._get_offset(child), sum(child.h for child in self.children[:i]))
        total = sum(child.h for child in self.children)
        yield LinEq(self.total, total)
        yield LinEq(self.h, self.total + self.scroll)
        for child in self.children:
            yield LinEq(self.w, child.w + self._get_padder(child))

#=======================================================================================================================
# Atoms
#=======================================================================================================================
class AtomNode(BaseNode):
    def __init__(self, **attrs):
        BaseNode.__init__(self)
        self.attrs = attrs
        self.watchers = {}
    def __repr__(self):
        return self._repr_dims("%s(%s)" % (self.__class__.__name__[:-4], ", ".join("%s = %r" % (k, v) 
            for k, v in self.attrs.items() if v is not None)))
    def get_constraints(self):
        for cons in BaseNode.get_constraints(self):
            yield cons
        for k, v in self.attrs.items():
            if v is None:
                continue
            obj = getattr(self, k, None)
            if isinstance(obj, LinVar):
                yield LinEq(obj, v)
    
    def set(self, attr, value):
        if self.attrs.get(value, NotImplemented) != value:
            self.attrs[attr] = value
            for cb in self.watchers.get(attr, ()):
                cb(value)
    def watch(self, attr, callback):
        if attr not in self.watchers:
            self.watchers[attr] = []
        self.watchers[attr].append(callback)

class LabelNode(AtomNode):
    def __init__(self, text = ""):
        AtomNode.__init__(self, text = text)

class ImageNode(AtomNode):
    def __init__(self, filename = ""):
        AtomNode.__init__(self, filename = filename)

class InputNode(AtomNode):
    def __init__(self, text = ""):
        AtomNode.__init__(self, text = text)

class ButtonNode(AtomNode):
    def __init__(self, text = "", clicked = None):
        AtomNode.__init__(self, text = text, clicked = clicked)
        self.clicked = LinVar("_clicked%d" % (self.id,), "action")

class CheckNode(AtomNode):
    def __init__(self, text = "", checked = None):
        AtomNode.__init__(self, text = text, checked = checked)
        self.checked = LinVar("_checked%d" % (self.id,), "action")

class RadioNode(AtomNode):
    def __init__(self, text = "", checked = None):
        AtomNode.__init__(self, text = text, checked = checked)
        self.checked = LinVar("_checked%d" % (self.id,), "action")

class ListNode(AtomNode):
    def __init__(self, text = "", selected = None, items = None):
        if items is None:
            items = []
        AtomNode.__init__(self, text = text, selected = selected, items = items)
        self.selected = LinVar("_selected%d" % (self.id,), "action")

class PaddingNode(AtomNode):
    def __init__(self):
        AtomNode.__init__(self)
    @classmethod
    def X(cls, width = None, height = None):
        return AtomNode.X(cls(), width, height)


if __name__ == "__main__":
    w = LinVar("w")
    x = (LabelNode("Hello").X(w, 30) | LabelNode("foo").X(w)) --- ButtonNode("bar").X(w*3)
    print x
    print list(x.get_constraints())












