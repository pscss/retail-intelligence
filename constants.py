"""Project-wide constants — may migrate to config/env vars over time."""

# Pagination
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000

# Cache TTLs (seconds)
CACHE_TTL_INFERENCE = 3600  # 1 hour
CACHE_TTL_EMBEDDING = 86400  # 24 hours
CACHE_TTL_SESSION = 1800  # 30 minutes
CACHE_TTL_RATE_LIMIT = 60  # 1 minute

# FAISS
FAISS_TOP_K_DEFAULT = 5
FAISS_TOP_K_MAX = 20

# Inference
MAX_INPUT_LENGTH = 512  # max tokens for transformer input
CONFIDENCE_THRESHOLD = 0.5  # minimum confidence to return a result


# Seed configuration
SEED_MAX_PRODUCTS = 92353  # full dunnhumby dataset 500
SEED_MAX_FAQS = 26000  # full Bitext dataset 1000
SEED_BATCH_SIZE = 10000
PRODUCTS_FILE = "data/product.csv"
