from typing import TypedDict

UserAuthTokensDict = TypedDict("UserAuthTokensDict", {"refresh": str, "access": str})
