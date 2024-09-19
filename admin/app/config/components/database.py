from config.components.base import env

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
        "OPTIONS": {"options": "-c search_path=public,content"},
    }
}
