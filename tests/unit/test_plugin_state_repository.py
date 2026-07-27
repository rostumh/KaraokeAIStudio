from pathlib import Path
from app.infrastructure.repositories.plugin_state_repository import PluginStateRepository
def test_round_trip(tmp_path:Path):
 r=PluginStateRepository(tmp_path/"plugins.json");r.save({"example":True});assert r.load()=={"example":True}
