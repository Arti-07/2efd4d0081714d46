from .auth_routes import router as auth_router
from .personality_routes import router as personality_router
from .astro_routes import router as astro_router
from .vibe_routes import router as vibe_router
from .audio_routes import router as audio_router
from .image_routes import router as image_router

__all__ = ["auth_router", "personality_router", "astro_router", "vibe_router", "audio_router", "image_router"]
