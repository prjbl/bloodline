from .field_definition import FieldDef

class SectionKeys:
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"


class WindowKeys:
    GEOMETRY: str = "geometry"
    MAXIMIZED: str = "maximized"
    ENABLED: str = "enabled"
    LOCKED: str = "locked"


class WindowSchema:
    GEOMETRY_ROOT: FieldDef = FieldDef(WindowKeys.GEOMETRY, "600x350")
    GEOMETRY_TOPLEVEL: FieldDef = FieldDef(WindowKeys.GEOMETRY, "+0+0")
    MAXIMIZED: FieldDef = FieldDef(WindowKeys.MAXIMIZED, False)
    ENABLED: FieldDef = FieldDef(WindowKeys.ENABLED, True)
    LOCKED: FieldDef = FieldDef(WindowKeys.LOCKED, False)