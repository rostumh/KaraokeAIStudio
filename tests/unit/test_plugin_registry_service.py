import pytest
from app.application.errors import MediaImportError
from app.application.services.plugin_registry_service import PluginRegistryService
from app.domain.models.plugins import PluginDescriptor
def test_valid_descriptor():
 d=PluginDescriptor("example.plugin","Example","1.0","x","ACME","1.0",("export_profiles",));assert PluginRegistryService.validate_descriptor(d)==d
def test_rejects_incompatible_api():
 with pytest.raises(MediaImportError):PluginRegistryService.validate_descriptor(PluginDescriptor("example","E","1","","P","2.0",()))
