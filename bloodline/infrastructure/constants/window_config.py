from .base_constant import Const

class SectionKeys:
    ROOT: str = "root"
    TOPLEVEL: str = "toplevel"


class WindowKeys:
    GEOMETRY: str = "geometry"
    MAXIMIZED: str = "maximized"
    LOCKED: bool = "locked"


class WindowSchema:
    GEOMETRY_ROOT: Const = Const(WindowKeys.GEOMETRY, "600x350")
    GEOMETRY_TOPLEVEL: Const = Const(WindowKeys.GEOMETRY, "+0+0")
    MAXIMIZED: Const = Const(WindowKeys.MAXIMIZED, False)
    LOCKED: Const = Const(WindowKeys.LOCKED, False)