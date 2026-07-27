import pytest
from app.application.errors import MediaImportError
from app.infrastructure.plugins.plugin_context import RestrictedPluginContext
def test_profile_filters_unknown_values():
 c=RestrictedPluginContext();c.register_export_profile("plugin.web","Web",{"codec":"h264","shell":"bad"});assert c.export_profiles["plugin.web"][1]=={"codec":"h264"}
def test_profile_requires_namespace():
 with pytest.raises(MediaImportError):RestrictedPluginContext().register_export_profile("web","Web",{"codec":"h264"})
