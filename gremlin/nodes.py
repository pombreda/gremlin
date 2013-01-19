import itertools
from gremlin.linsys import LinVar, LinEq


class BaseNode(object):
    _counter = itertools.count()
    
    def __init__(self):
        self._id = self._counter.next()
        self.width = LinVar("_w%d" % (self._id,), "cons")
        self.height = LinVar("_h%d" % (self._id,), "cons")
        self.width_constraint = None
        self.height_constraint = None
    def get_constraints(self):
        if self.width_constraint:
            yield LinEq(self.width, self.width_constraint)
        if self.height_constraint:
            yield LinEq(self.height, self.height_constraint)
    
    def __or__(self, other):
        return HLayoutNode.join(self, other)
    def __sub__(self, other):
        return VLayoutNode.join(self, other)
    def __neg__(self):
        return self
    def X(self, width = None, height = None):
        if width:
            self.width_constraint = width
        if height:
            self.height_constraint = height
        return self
    
class LayoutNode(BaseNode):
    SEP = None
    def __init__(self, children):
        BaseNode.__init__(self)
        self.children = children
        self._scroller = LinVar("_s%d" % (self._id,), "padding")
        self._total = LinVar("_t%d" % (self._id), "cons")

    def __repr__(self):
        text = "(%s)" % (self.SEP.join(repr(child) for child in self.children),)
        if self.width_constraint or self.height_constraint:
            text += ".X(%r, %r)" % (self.width_constraint, self.height_constraint)
        return text

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

    def _get_constraints(self):
        return ()

    def get_constraints(self):
        for cons in BaseNode.get_constraints(self):
            yield cons
        for child in self.children:
            for cons in child.get_constraints():
                yield cons
        for cons in self._get_constraints():
            yield cons

    def _get_padder(self, node):
        return LinVar("_p%d" % (node._id,), "padding")
    def _get_offset(self, node):
        return LinVar("_o%d" % (node._id,), "offset")


class HLayoutNode(LayoutNode):
    SEP = " | "
    def _get_constraints(self):
        yield LinEq(self.width, sum(child.width for child in self.children) + self._scroller)
        offset = 0
        for child in self.children:
            yield LinEq(self.height, child.height + self._get_padder(child))
            yield LinEq(self._get_offset(child), offset)
            offset += child.width
        yield LinEq(self._total, offset)

class VLayoutNode(LayoutNode):
    SEP = " --- "
    def _get_constraints(self):
        yield LinEq(self.height, sum(child.height for child in self.children) + self._scroller)
        offset = 0
        for child in self.children:
            yield LinEq(self.width, child.width + self._get_padder(child))
            yield LinEq(self._get_offset(child), offset)
            offset += child.height
        yield LinEq(self._total, offset)

class AtomNode(BaseNode):
    def __init__(self, **attrs):
        BaseNode.__init__(self)
        self.attrs = attrs
    
    def __repr__(self):
        text = "%s(%s)" % (self.__class__.__name__, ", ".join("%s = %r" % (k, v) for k, v in self.attrs.items()))
        if self.width_constraint or self.height_constraint:
            text += ".X(%r, %r)" % (self.width_constraint, self.height_constraint)
        return text

    def _get_constraints(self):
        return ()

    def get_constraints(self):
        for cons in BaseNode.get_constraints(self):
            yield cons
        for cons in self._get_constraints():
            yield cons

class LabelNode(AtomNode):
    def __init__(self, text, **kwargs):
        AtomNode.__init__(self, text = text, **kwargs)

class InputNode(AtomNode):
    def __init__(self, text = "", **kwargs):
        AtomNode.__init__(self, text = text, **kwargs)

class ImageNode(AtomNode):
    def __init__(self, filename, **kwargs):
        AtomNode.__init__(self, filename = filename, **kwargs)

class ButtonNode(AtomNode):
    def __init__(self, text, clicked = None, **kwargs):
        AtomNode.__init__(self, text = text, clicked = clicked, **kwargs)
        self.clicked = LinVar("_clicked%d" % (self._id,), "flow")

#=======================================================================================================================
# Solving
#=======================================================================================================================
class Solver(object):
    def __init__(self, node):
        self.node = node




if __name__ == "__main__":
    k = LinVar("k")
    r = (InputNode() | ButtonNode("Send", clicked = k).X(80, 30)).X(200, 30)
    print r
    print list(r.get_constraints())




















