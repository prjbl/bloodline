from pydantic import Field

from ..shared_models import AllowModel
from infrastructure.config import SettingsSchema

class SettingsModel(AllowModel):
    autosave: bool = Field(default=SettingsSchema.AUTOSAVE.default, alias=SettingsSchema.AUTOSAVE.alias)