import os
from decouple import config
print(f"DEBUG from config: {config('DEBUG', default=False, cast=bool)}")
