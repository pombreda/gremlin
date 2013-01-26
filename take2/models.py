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
class ArgModel(BaseModel):
    pass

@argdeco
class StrArgModel(ArgModel):
    pass

@argdeco
class PasswordArgModel(StrArgModel):
    pass

@argdeco
class IntArgModel(ArgModel):
    pass

@argdeco
class ClassModel(BaseModel):
    pass

