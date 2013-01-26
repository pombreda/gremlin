import sys
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
import dsl
from solver import ConstraintSolver


class BaseRenderer(object):
    def __init__(self, node, solver):
        self.node = node
        self.solver = solver
    
    def _build(self, parent):
        raise NotImplementedError()
    
    _registry = {}
    @classmethod
    def register(cls, nodecls):
        def deco(cls2):
            if nodecls in cls._registry:
                raise AttributeError("%r is already registered" % (nodecls,))
            cls._registry[nodecls] = cls2
            return cls2
        return deco
    @classmethod
    def for_node(cls, node, solver):
        renderer = cls._registry[type(node)]
        return renderer(node, solver)

def uiproperty(func):
    def getter(self):
        return self.node.attrs[func.__name__]
    def setter(self, value):
        if self.node.attrs[func.__name__] != value:
            self.node.attrs[func.__name__] = value
            func(self, value)
    return property(getter, setter)

@BaseRenderer.register(dsl.HLayoutNode)
class HLayoutRenderer(BaseRenderer):
    def _build(self, parent):
        pass

@BaseRenderer.register(dsl.PaddingNode)
class PaddingRenderer(BaseRenderer):
    def _build(self, parent):
        lbl = QtGui.QLabel("", parent)
        return lbl

@BaseRenderer.register(dsl.LabelNode)
class LabelRenderer(BaseRenderer):
    def _build(self, parent):
        lbl = QtGui.QLabel("", parent)
        def watch_text(val):
            self.text = val
        self.node.watch("text", watch_text)
        #lbl.setText(self.node.attrs["text"])
        return lbl
    
    @uiproperty
    def text(self, value):
        self._widget.setText(value)

@BaseRenderer.register(dsl.ButtonNode)
class ButtonRenderer(BaseRenderer):
    def _build(self, parent):
        btn = QtGui.QPushButton("", parent)
        btn.clicked.connect(self._handle_clicked)
        return btn
    
    @uiproperty
    def text(self, value):
        self._widget.setText(value)

    def _handle_clicked(self, event):
        self.solver.flash(self.node.clicked)



def run(node):
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    solver = ConstraintSolver(node)
    print "solver:", solver
    renderer = BaseRenderer.for_node(node, solver)
    wdt = renderer._build(None)
    wdt.show()
    return app.exec_()



if __name__ == "__main__":
    root = dsl.LabelNode("hello").X(300, 200)
    run(root)







