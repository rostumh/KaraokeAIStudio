from app.infrastructure.plugins.plugin_manager import PluginManager
class Repo:
 def __init__(self):self.x={}
 def load(self):return dict(self.x)
 def save(self,x):self.x=x
def test_enablement_persists():
 r=Repo();m=object.__new__(PluginManager);m._repository=r;m.set_enabled("x",True);assert r.x["x"] is True
