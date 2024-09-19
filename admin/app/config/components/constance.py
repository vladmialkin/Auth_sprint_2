from config.components.redis import REDIS_HOST, REDIS_PORT

CONSTANCE_BACKEND = "constance.backends.redisd.CachingRedisBackend"

CONSTANCE_REDIS_CONNECTION = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": 0,
}

CONSTANCE_REDIS_CACHE_TIMEOUT = 60 * 5  # 5 minutes

CONSTANCE_CONFIG = {
    "PAGINATION_PAGE_SIZE": (15, "Размер страницы пагинации", int),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Пагинация": ("PAGINATION_PAGE_SIZE",),
}
