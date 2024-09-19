from config.components.base import DEBUG, env

if DEBUG:
    INTERNAL_IPS = env.str("INTERNAL_IPS").split(",")
