"""Configuration via environment variables, .env, and Docker secrets."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and secret files."""

    # Shark account
    shark_username: str
    shark_password: str
    shark_region: str = Field(default="us", pattern=r"^(us|eu)$")

    # MQTT broker
    mqtt_host: str
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_prefix: str = "shark2mqtt"

    # SharkNinja cloud (skegox)
    shark_household_id: str | None = None

    # Polling
    poll_interval: int = 300
    poll_interval_active: int = 20

    # Operating_Mode value sent for HA's pause command. 1 (PAUSE) is what
    # most models expect. Some models ignore 1 and report 0 while paused
    # from the Shark app, so this lets those users try 0.
    pause_operating_mode: int = Field(default=1, ge=0, le=1)

    # When false, never launch the automated Chromium login. An expired or
    # missing token then fails with a clear "log in again" error instead,
    # for setups where tokens come from a manual login.
    browser_login: bool = True

    # Prefix for Home Assistant discovery IDs, so a second copy of the
    # bridge can run beside the first without its entities colliding.
    # Empty (default) keeps today's IDs: unique_id "shark2mqtt_<dsn>" and
    # entity IDs such as vacuum.<name>. "claude" gives unique_id
    # "claude_shark2mqtt_<dsn>" and entity IDs such as vacuum.claude_<name>.
    # Use a different MQTT_PREFIX as well, or both copies share topics.
    entity_id_prefix: str = Field(default="", pattern=r"^[a-z0-9_]*$")

    # Token persistence
    token_dir: str = "/data"

    # Logging
    log_level: str = "INFO"

    # Floor plan image entity (rendered from the robot's MARD room file)
    map_image: bool = True
    map_show_scan: bool = False

    # Also publish Ayla-only robots on accounts where skegox has others
    # (half-migrated accounts, issue #46). Off by default.
    ayla_merge: bool = False

    # Operation modes
    auth_once: bool = False
    offline: bool = False

    model_config = {
        "env_file": ".env",
        "env_prefix": "",
        "case_sensitive": False,
        "secrets_dir": "/run/secrets" if Path("/run/secrets").is_dir() else None,
    }
