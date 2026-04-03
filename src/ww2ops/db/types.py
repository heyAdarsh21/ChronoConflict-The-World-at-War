from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB


jsonb_type = JSON().with_variant(JSONB, "postgresql")
