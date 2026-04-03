"""initial production schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-01 13:20:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('alliances',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('code', sa.String(length=24), nullable=False),
        sa.Column('side', sa.String(length=24), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('doctrine', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_table('geographic_regions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('theater', sa.String(length=120)),
        sa.Column('parent_region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('latitude', sa.Float()),
        sa.Column('longitude', sa.Float()),
        sa.Column('geojson', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('strategic_rating', sa.Integer()),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('name', 'theater', name='uq_region_name_theater')
    )
    op.create_table('nations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('side', sa.String(length=24)),
        sa.Column('alliance_id', sa.Integer(), sa.ForeignKey('alliances.id')),
        sa.Column('capital', sa.String(length=120)),
        sa.Column('ideology', sa.Text()),
        sa.Column('description', sa.Text()),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_table('campaigns',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('theater', sa.String(length=100)),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('start_date', sa.DateTime()),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('description', sa.Text()),
        sa.Column('outcome', sa.String(length=50)),
        sa.Column('strategic_value', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('leaders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nation_id', sa.Integer(), sa.ForeignKey('nations.id')),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=150)),
        sa.Column('role_type', sa.String(length=50)),
        sa.Column('biography', sa.Text()),
        sa.Column('ideology', sa.Text()),
        sa.Column('portrait_url', sa.String(length=255)),
        sa.Column('influence_score', sa.Float()),
        sa.Column('born_on', sa.Date()),
        sa.Column('died_on', sa.Date()),
        sa.Column('notable_quotes', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('battles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('campaign_id', sa.Integer(), sa.ForeignKey('campaigns.id')),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('location_name', sa.String(length=200)),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('axis_forces', sa.Integer()),
        sa.Column('allied_forces', sa.Integer()),
        sa.Column('axis_casualties', sa.Integer()),
        sa.Column('allied_casualties', sa.Integer()),
        sa.Column('victor_side', sa.String(length=24)),
        sa.Column('description', sa.Text()),
        sa.Column('latitude', sa.Float()),
        sa.Column('longitude', sa.Float()),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('operations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('battle_id', sa.Integer(), sa.ForeignKey('battles.id')),
        sa.Column('campaign_id', sa.Integer(), sa.ForeignKey('campaigns.id')),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code_name', sa.String(length=100)),
        sa.Column('side', sa.String(length=24)),
        sa.Column('objective', sa.Text()),
        sa.Column('outcome', sa.String(length=50)),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('description', sa.Text()),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('analysis', sa.Text()),
        sa.Column('intelligence_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('command_assignments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('leader_id', sa.Integer(), sa.ForeignKey('leaders.id'), nullable=False),
        sa.Column('operation_id', sa.Integer(), sa.ForeignKey('operations.id')),
        sa.Column('campaign_id', sa.Integer(), sa.ForeignKey('campaigns.id')),
        sa.Column('position', sa.String(length=150)),
        sa.Column('start_date', sa.DateTime()),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('resource_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('unit', sa.String(length=50)),
        sa.Column('category', sa.String(length=50)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('code')
    )
    op.create_table('simulations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('scenario_name', sa.String(length=200), nullable=False),
        sa.Column('start_year', sa.Integer(), nullable=False),
        sa.Column('side', sa.String(length=24), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('current_turn', sa.Integer(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('latest_outcome', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('resource_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nation_id', sa.Integer(), sa.ForeignKey('nations.id'), nullable=False),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('simulation_id', sa.Integer(), sa.ForeignKey('simulations.id')),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(length=255)),
        sa.Column('confidence_level', sa.Float()),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('nation_id', 'simulation_id', 'snapshot_date', name='uq_snapshot_nation_sim_date')
    )
    op.create_table('resource_balances',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('snapshot_id', sa.Integer(), sa.ForeignKey('resource_snapshots.id'), nullable=False),
        sa.Column('resource_type_id', sa.Integer(), sa.ForeignKey('resource_types.id'), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('reserved_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('allocated_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('snapshot_id', 'resource_type_id', name='uq_balance_snapshot_type')
    )
    op.create_table('simulation_decisions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('simulation_id', sa.Integer(), sa.ForeignKey('simulations.id'), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('decision_type', sa.String(length=64), nullable=False),
        sa.Column('actor_nation_id', sa.Integer(), sa.ForeignKey('nations.id')),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('simulation_outcomes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('simulation_id', sa.Integer(), sa.ForeignKey('simulations.id'), nullable=False),
        sa.Column('decision_id', sa.Integer(), sa.ForeignKey('simulation_decisions.id')),
        sa.Column('success_probability', sa.Float(), nullable=False),
        sa.Column('realized_success', sa.Boolean(), nullable=False),
        sa.Column('weighted_score', sa.Float(), nullable=False),
        sa.Column('narrative_summary', sa.Text(), nullable=False),
        sa.Column('impact_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('simulation_audit_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('simulation_id', sa.Integer(), sa.ForeignKey('simulations.id'), nullable=False),
        sa.Column('decision_id', sa.Integer(), sa.ForeignKey('simulation_decisions.id')),
        sa.Column('event_type', sa.String(length=80), nullable=False),
        sa.Column('detail', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('war_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('battle_id', sa.Integer(), sa.ForeignKey('battles.id')),
        sa.Column('operation_id', sa.Integer(), sa.ForeignKey('operations.id')),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('summary', sa.Text()),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('source', sa.String(length=255)),
        sa.Column('confidence_level', sa.Float()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('timeline_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('simulation_id', sa.Integer(), sa.ForeignKey('simulations.id')),
        sa.Column('war_event_id', sa.Integer(), sa.ForeignKey('war_events.id')),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('entry_type', sa.String(length=64), nullable=False),
        sa.Column('headline', sa.String(length=200), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('entry_date', sa.DateTime(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('intelligence_reports',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('simulation_id', sa.Integer(), sa.ForeignKey('simulations.id')),
        sa.Column('nation_id', sa.Integer(), sa.ForeignKey('nations.id')),
        sa.Column('region_id', sa.Integer(), sa.ForeignKey('geographic_regions.id')),
        sa.Column('report_date', sa.DateTime(), nullable=False),
        sa.Column('classification', sa.String(length=50)),
        sa.Column('source_type', sa.String(length=100)),
        sa.Column('report_type', sa.String(length=100)),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('decoded', sa.Boolean(), nullable=False),
        sa.Column('confidence_level', sa.Float()),
        sa.Column('source_reference', sa.String(length=255)),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_table('war_crimes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('war_event_id', sa.Integer(), sa.ForeignKey('war_events.id'), nullable=False),
        sa.Column('category', sa.String(length=120), nullable=False),
        sa.Column('location_name', sa.String(length=200)),
        sa.Column('victims', sa.Text()),
        sa.Column('perpetrators', sa.Text()),
        sa.Column('death_toll', sa.Integer()),
        sa.Column('description', sa.Text()),
        sa.Column('sources', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('media_url', sa.String(length=255)),
        sa.Column('sensitivity_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('war_event_id')
    )
    op.create_table('import_batches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('records_processed', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )


def downgrade():
    for table_name in ['import_batches', 'war_crimes', 'intelligence_reports', 'timeline_entries', 'war_events', 'simulation_audit_events', 'simulation_outcomes', 'simulation_decisions', 'resource_balances', 'resource_snapshots', 'simulations', 'resource_types', 'command_assignments', 'operations', 'battles', 'leaders', 'campaigns', 'nations', 'geographic_regions', 'users', 'alliances']:
        op.drop_table(table_name)
