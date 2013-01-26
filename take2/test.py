from linsys import LinVar
from dsl import LabelNode, InputNode, PaddingNode, ImageNode, ButtonNode, CheckNode, RadioNode
from qtrenderer import run


a = LinVar("a")
b = LinVar("b")
ui = (
    (LabelNode("First name").X(a, None) | InputNode().X(b, None)).X(None, 30)
    ---
    (LabelNode("Age").X(a, None) | InputNode().X(b, None)).X(None, 30)
    ---
    (PaddingNode.X(a, None) | ButtonNode("Send")).X(None, 30)
)

run(ui)

