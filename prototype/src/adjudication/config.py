from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    default_reg_window_hours: float | None = None
    stale_reference_days: int = 30
    auto_close_enabled: bool = False
    llm_provider: str = "stub"

def load_settings():
    return Settings()
