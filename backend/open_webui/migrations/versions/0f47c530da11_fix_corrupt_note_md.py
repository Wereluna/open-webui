"""fix corrupt note md content

Revision ID: 0f47c530da11
Revises: 1ce6ade7d93b
Create Date: 2026-08-05 21:06:03.932000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, select, table, update
from open_webui.utils.notes import ensure_md_string

# revision identifiers, used by Alembic.
revision: str = '0f47c530da11'
down_revision: Union[str, None] = '1ce6ade7d93b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    note_table = table(
        'note',
        column('id', sa.Text),
        column('data', sa.JSON),
    )

    result = conn.execute(select(note_table.c.id, note_table.c.data)).yield_per(100)
    fixed_count = 0

    for note_id, data in result:
        if data is None:
            continue
        md = (data.get('content') or {}).get('md')
        if md is None or isinstance(md, str):
            continue

        fixed_md = ensure_md_string(md)
        fixed_data = {
            **data,
            'content': {**(data.get('content') or {}), 'md': fixed_md},
        }
        conn.execute(
            update(note_table)
            .where(note_table.c.id == note_id)
            .values(data=fixed_data)
        )
        fixed_count += 1

    print(f'fix_corrupt_note_md: fixed {fixed_count} note(s)')


def downgrade() -> None:
    # Irreversible: original non-string md content cannot be recovered
    pass
