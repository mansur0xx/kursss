"""keycloak_id not null (three-step migration)

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-26 17:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Ескі жазбаларда NULL болса, уақытша legacy-<id> мәнін толтыру
    op.execute("UPDATE users SET keycloak_id = 'legacy-' || id WHERE keycloak_id IS NULL")
    # 2. Енді ғана NOT NULL шектеуін қою
    op.alter_column(
        "users",
        "keycloak_id",
        existing_type=sa.String(length=64),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "keycloak_id",
        existing_type=sa.String(length=64),
        nullable=True,
    )
