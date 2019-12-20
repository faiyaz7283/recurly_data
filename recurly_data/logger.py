import logging
import socket
from logging.handlers import SysLogHandler
from typing import Optional
from recurly_data.config import PAPERTRAIL_DEST, PAPERTRAIL_PORT

class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True

class Logger():
    """Logger class."""

    def __init__(
            self,
            dest: str = PAPERTRAIL_DEST,
            port: int = PAPERTRAIL_PORT,
            level: int = logging.DEBUG,
            formatted_string: Optional[str] = None,
            date_format: str = "%b %d %H:%M:%S",
    ):
        self.syslog = SysLogHandler(address=(dest, port))
        self.syslog.addFilter(ContextFilter())

        if not formatted_string:
            formatted_string = (
                "%(asctime)s %(hostname)s Recurly_Data: %(message)s"
            )
        formatter = logging.Formatter(formatted_string, datefmt=date_format)
        self.syslog.setFormatter(formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(self.syslog)
        self.logger.setLevel(level)

    def debug(self, msg):
        """Log debug level messages."""
        return self.logger.debug(f"[DEBUG] {msg}")

    def info(self, msg):
        """Log info level messages."""
        return self.logger.info(f"[INFO] {msg}")

    def warning(self, msg):
        """Log warning level messages."""
        return self.logger.warning(f"[WARNING] {msg}")

    def error(self, msg):
        """Log error level messages."""
        return self.logger.error(f"[ERROR] {msg}")

    def critical(self, msg):
        """Log critical level messages."""
        return self.logger.critical(f"[CRITICAL] {msg}")

if __name__ == "__main__":
    log = Logger()
    log.debug("This is a debug level message.")
    log.info("This is a info level message.")
    log.warning("This is a warning level message.")
    log.error("This is a error level message.")
    log.critical("This is a critical level message.")
