#
# http://www.java2s.com/Questions_And_Answers/Qt/Widget/QSplitter.htm
# http://stackoverflow.com/questions/2545577/qsplitter-becoming-undistinguishable-between-qwidget-and-qtabwidget
# http://lists.trolltech.com/qt-interest/2001-09/thread00029-0.html
#
import sys
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
import dsl
from solver import ConstraintSolver


def uiproperty(func):
    def getter(self):
        return self.node.attrs[func.__name__]
    def setter(self, value):
        if getattr(func, "_marker", NotImplemented) == value:
            return
        func._marker = value
        self.node.attrs[func.__name__] = value
        func(self, value)
        del func._marker
    return property(getter, setter)


class BaseRenderer(object):
    def __init__(self, node, solver):
        self.node = node
        self.solver = solver
        self.solver.watch(self.node.w, self.set_width)
        self.solver.watch(self.node.h, self.set_height)
        self.widget = None
        self._post_init()
    
    def _post_init(self):
        pass

    def build(self, parent):
        if self.widget is None:
            self.widget = self._build(parent)
            #self._install_propagated_attrs()
        return self.widget
        
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

    def set_width(self, newwidth):
        self.widget.resize(int(newwidth), self.widget.height())
    def set_height(self, newheight):
        self.widget.resize(self.widget.width(), int(newheight))

class RootWindowRenderer(BaseRenderer):
    def __init__(self, root):
        solver = ConstraintSolver(root)
        BaseRenderer.__init__(self, root, solver)
    
    def _build(self, parent):
        wnd = QtGui.QWidget()
        wnd.closeEvent = self._handle_closed
        self.widget = wnd
        renderer = BaseRenderer.for_node(self.node, self.solver)
        self.content = renderer.build(wnd)
        self._super_resizeEvent = wnd.resizeEvent
        wnd.resizeEvent = self._handle_resized
        if not self.solver.is_free("window_width"):
            wnd.setFixedWidth(self.solver["window_width"])
        if not self.solver.is_free("window_height"):
            wnd.setFixedHeight(self.solver["window_height"])

        self.node.init_watchers()
        wnd.show()
        return wnd

    @uiproperty
    def title(self, val):
        self.widget.setWindowTitle(val)

    @uiproperty
    def icon(self, filename):
        if not filename:
            return
        self.widget.setWindowIcon(QtGui.QIcon(filename))

    def _handle_resized(self, event):
        self._super_resizeEvent(event)
        self.content.move(0, 0)
        freevars = {}
        if self.solver.is_free("window_width"):
            freevars["window_width"] = event.size().width()
        if self.solver.is_free("window_height"):
            freevars["window_height"] = event.size().height()
        self.solver.update(freevars)
    
    def _handle_closed(self, event):
        #self.solver.flash("closed")
        event.accept()

@BaseRenderer.register(dsl.HLayoutNode)
class HLayoutRenderer(BaseRenderer):
    def _post_init(self):
        self.children = [BaseRenderer.for_node(child_node, self.solver)
            for child_node in self.node.children]

    def _build(self, parent):
        for child in self.children:
            if self.solver.is_free(child.node.w):
                if child.node.w.default is None:
                    child.node.w.default = 100
        
        scroll = QtGui.QScrollArea(parent)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll.setWidgetResizable(False)
        scroll.setLayout(QtGui.QVBoxLayout())
        hor = QtGui.QWidget()
        scroll.setWidget(hor)
        
        for child in self.children:
            child.build(hor)
            off = self.node._get_offset(child.node)
            def set_offset(val, child = child):
                #print "!! set_offset", child, val
                child.widget.move(int(val), 0)
            self.solver.watch(off, set_offset)
        self.solver.watch(self.node.total, lambda val: hor.setFixedWidth(val))
        self.solver.watch(self.node.h, lambda val: hor.setFixedHeight(val))
        return scroll
        

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
        return lbl
    
    @uiproperty
    def text(self, value):
        self.widget.setText(value)

@BaseRenderer.register(dsl.ButtonNode)
class ButtonRenderer(BaseRenderer):
    def _build(self, parent):
        btn = QtGui.QPushButton("", parent)
        btn.clicked.connect(self._handle_clicked)
        return btn
    
    @uiproperty
    def text(self, value):
        self.widget.setText(value)

    def _handle_clicked(self, event):
        self.solver.flash(self.node.clicked)



def run(node):
    app = QtGui.QApplication(sys.argv)
    app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    wnd = RootWindowRenderer(node)
    wnd.build(None)
    return app.exec_()



if __name__ == "__main__":
    root = dsl.LabelNode("hello") | dsl.LabelNode("world")
    run(root)







