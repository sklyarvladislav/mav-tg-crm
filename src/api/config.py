import os 
from dataclasses import dataclass

from adaptix import Retort 
from dynaconf import Dynaconf


@dataclass(slots=True)
class Config:
    pass

def get_config() -> Config:
    dynaconf = Dynaconf(
        settings_files=[os.getenv("CONFIG_FILE", "../config.toml")],
        envvar_prefix="MAV",
        load_dotenv=True,
        environments=True,
        default_env="default",
        merge_enabled=True,
        env_switcher="MAV_ENV",
    )
    retort = Retort()
    
    return retort.load(dynaconf, Config)

config: Config = get_config()
