import logging

log = logging
log.basicConfig(
    format="%(asctime)s   %(levelname)s \t (%(lineno)-d) %(filename)-10s \t %(message)s",
    level=logging.INFO,
)
