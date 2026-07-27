import logging
from pathlib import Path
def configure_lyrics_logger(path:Path)->logging.Logger:
    logger=logging.getLogger('lyrics');logger.setLevel(logging.INFO)
    target=str(path.resolve())
    if not any(isinstance(h,logging.FileHandler) and h.baseFilename==target for h in logger.handlers):
        path.parent.mkdir(parents=True,exist_ok=True);h=logging.FileHandler(path,encoding='utf-8');h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'));logger.addHandler(h)
    return logger
