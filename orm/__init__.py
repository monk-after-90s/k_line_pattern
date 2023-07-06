from .database import alrb_asess_fctry, bar_asess_fctry
from .models import Dbbaroverview, Dbbardata, PatternRecognizeRecord, KPatternGroup, KPattern

import asyncio


async def close_engines():
    from .database import bar_engine, alpha_rabit_engine
    await asyncio.gather(bar_engine.dispose(),
                         alpha_rabit_engine.dispose())
