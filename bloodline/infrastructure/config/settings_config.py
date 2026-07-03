from .field_definition import FieldDef

class SettingsKeys:
    AUTOSAVE: str = "autosave"


class SettingsSchema:
    AUTOSAVE: FieldDef = FieldDef(SettingsKeys.AUTOSAVE, True)