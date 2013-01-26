import dsl


def argdeco(func):
    def predeco(*args, **kwargs):
        def deco(func2):
            return func(func2, *args, **kwargs)
        return deco
    return predeco

class BaseModel(object):
    def render(self):
        raise NotImplementedError()

@argdeco
class FuncModel(BaseModel):
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

@argdeco
class MethodModel(BaseModel):
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

class ClassModel(BaseModel):
    def __init__(self, cls):
        self.cls = cls


class ArgModel(BaseModel):
    def __init__(self, label):
        self.label = label

class StrArgModel(ArgModel):
    def render(self):
        return dsl.InputNode()

class PasswordArgModel(StrArgModel):
    pass

class IntArgModel(ArgModel):
    pass

class PropertyModel(BaseModel):
    pass

class StrPropertyModel(PropertyModel):
    def __init__(self, label, default = NotImplemented):
        self.label = label
        self.default = default
    def __get__(self, inst, cls):
        if inst is None:
            return cls
        val = getattr(inst, "_%d" % (id(self),), self.default)
        if val is NotImplemented:
            raise AttributeError(self.label)
    def __set__(self, inst, value):
        setattr(inst, "_%d" % (id(self),), value)

def render(obj):
    pass



if __name__ == "__main__":
    import time
    import threading
    
    @ClassModel
    class Hello(object):
        the_time = StrPropertyModel("Current time:")
        
        def __init__(self):
            self.the_time = ""
            self.active = True
            threading.Thread(target = self._update_time)
        
        def _update_time(self):
            while self.active:
                self.the_time = time.ctime()
                time.sleep(1)
        
        @MethodModel(username = StrArgModel("Username"), password = StrArgModel("Password"))
        def login(self, username, password):
            pass
        
        layout = (
            the_time
            ---
            login
        )
        
        #def get_layout(self):
        #    return self.login










