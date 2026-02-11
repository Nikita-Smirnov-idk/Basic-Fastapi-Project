"""YC company batch_code+name index for list ordering

Revision ID: c1f2a3b4c5d6
Revises: 9a1644c4107c
Create Date: 2026-02-12

"""
from alembic import op


revision = "c1f2a3b4c5d6"
down_revision = "9a1644c4107c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_yccompany_batch_code_name",
        "yccompany",
        ["batch_code", "name"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_yccompany_batch_code_name", table_name="yccompany")
