"""Centralized product branding and runtime identifiers."""

PRODUCT_NAME = "KittnTabbR-AI"
PRODUCT_SLUG = "kittntabbr-ai"
LOGGER_NAME = PRODUCT_SLUG
MACOS_LAUNCHD_LABEL = "com.kittntabbr.ai"
WINDOWS_TASK_NAME = PRODUCT_NAME
WINDOWS_TASK_FILE = f"{PRODUCT_SLUG}_task.xml"
LINUX_SERVICE_NAME = f"{PRODUCT_SLUG}.service"
