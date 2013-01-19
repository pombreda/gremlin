import sys
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from gremlin.nodes import LabelNode


class BaseRenderer(object):
    def __init__(self, node):
        self.node = node
        self.widget = None

    def build(self, parent):
        if self.widget is None:
            self.widget = self._build(parent)
        return self.widget
    def _build(self, parent):
        raise NotImplementedError()
    
    _registry = {}
    @classmethod
    def register(cls, nodecls):
        def deco(rendcls):
            if nodecls in cls._registry:
                raise ValueError("%r already registered" % (nodecls,))
            cls._registry[nodecls] = rendcls
            return rendcls
        return deco
    
    @classmethod
    def for_node(cls, node):
        renderer = cls._registry[type(node)]
        return renderer(node)

@BaseRenderer.register(LabelNode)
class LabelRenderer(BaseRenderer):
    def _build(self, parent):
        lbl = QtGui.QLabel("", parent)
        lbl.setText(self.node.attrs["text"])
        return lbl


app = QtGui.QApplication(sys.argv)
app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

def run(node):
    renderer = BaseRenderer.for_node(node)
    renderer.build(None)
    renderer.widget.show()
    return app.exec_()



if __name__ == "__main__":
    root = LabelNode("hello")
    run(root)


