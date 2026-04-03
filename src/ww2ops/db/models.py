from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.ww2ops.db.types import jsonb_type
from src.ww2ops.extensions import db


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="historian", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    simulations: Mapped[list["Simulation"]] = relationship(back_populates="user")


class Alliance(TimestampMixin, db.Model):
    __tablename__ = "alliances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    side: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    doctrine: Mapped[dict | None] = mapped_column(jsonb_type)

    nations: Mapped[list["Nation"]] = relationship(back_populates="alliance")


class GeographicRegion(TimestampMixin, db.Model):
    __tablename__ = "geographic_regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    theater: Mapped[str | None] = mapped_column(String(120), index=True)
    parent_region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    geojson: Mapped[dict | None] = mapped_column(jsonb_type)
    strategic_rating: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)

    parent_region: Mapped["GeographicRegion | None"] = relationship(remote_side=[id], backref="children")

    __table_args__ = (
        UniqueConstraint("name", "theater", name="uq_region_name_theater"),
        Index("ix_region_lat_lng", "latitude", "longitude"),
    )


class Nation(TimestampMixin, db.Model):
    __tablename__ = "nations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    side: Mapped[str | None] = mapped_column(String(24), index=True)
    alliance_id: Mapped[int | None] = mapped_column(ForeignKey("alliances.id"))
    capital: Mapped[str | None] = mapped_column(String(120))
    ideology: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)

    alliance: Mapped["Alliance | None"] = relationship(back_populates="nations")
    leaders: Mapped[list["Leader"]] = relationship(back_populates="nation")


class Leader(TimestampMixin, db.Model):
    __tablename__ = "leaders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nation_id: Mapped[int | None] = mapped_column(ForeignKey("nations.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(150))
    role_type: Mapped[str | None] = mapped_column(String(50), index=True)
    biography: Mapped[str | None] = mapped_column(Text)
    ideology: Mapped[str | None] = mapped_column(Text)
    portrait_url: Mapped[str | None] = mapped_column(String(255))
    influence_score: Mapped[float | None] = mapped_column(Float)
    born_on: Mapped[date | None] = mapped_column(Date)
    died_on: Mapped[date | None] = mapped_column(Date)
    notable_quotes: Mapped[list | None] = mapped_column(jsonb_type)
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)

    nation: Mapped["Nation | None"] = relationship(back_populates="leaders")
    assignments: Mapped[list["CommandAssignment"]] = relationship(back_populates="leader")


class Campaign(TimestampMixin, db.Model):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    theater: Mapped[str | None] = mapped_column(String(100), index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(String(50))
    strategic_value: Mapped[int | None] = mapped_column(Integer)

    region: Mapped["GeographicRegion | None"] = relationship()
    operations: Mapped[list["Operation"]] = relationship(back_populates="campaign")
    assignments: Mapped[list["CommandAssignment"]] = relationship(back_populates="campaign")


class Battle(TimestampMixin, db.Model):
    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    location_name: Mapped[str | None] = mapped_column(String(200))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    axis_forces: Mapped[int | None] = mapped_column(Integer)
    allied_forces: Mapped[int | None] = mapped_column(Integer)
    axis_casualties: Mapped[int | None] = mapped_column(Integer)
    allied_casualties: Mapped[int | None] = mapped_column(Integer)
    victor_side: Mapped[str | None] = mapped_column(String(24), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)

    campaign: Mapped["Campaign | None"] = relationship()
    region: Mapped["GeographicRegion | None"] = relationship()
    operations: Mapped[list["Operation"]] = relationship(back_populates="battle")

    __table_args__ = (Index("ix_battles_lat_lng", "latitude", "longitude"),)


class Operation(TimestampMixin, db.Model):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    battle_id: Mapped[int | None] = mapped_column(ForeignKey("battles.id"), index=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code_name: Mapped[str | None] = mapped_column(String(100), index=True)
    side: Mapped[str | None] = mapped_column(String(24), index=True)
    objective: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(String(50))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    parameters: Mapped[dict | None] = mapped_column(jsonb_type)
    analysis: Mapped[str | None] = mapped_column(Text)
    intelligence_notes: Mapped[str | None] = mapped_column(Text)

    battle: Mapped["Battle | None"] = relationship(back_populates="operations")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="operations")
    region: Mapped["GeographicRegion | None"] = relationship()
    assignments: Mapped[list["CommandAssignment"]] = relationship(back_populates="operation")


class CommandAssignment(TimestampMixin, db.Model):
    __tablename__ = "command_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    leader_id: Mapped[int] = mapped_column(ForeignKey("leaders.id"), nullable=False, index=True)
    operation_id: Mapped[int | None] = mapped_column(ForeignKey("operations.id"), index=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), index=True)
    position: Mapped[str | None] = mapped_column(String(150))
    start_date: Mapped[datetime | None] = mapped_column(DateTime)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)

    leader: Mapped["Leader"] = relationship(back_populates="assignments")
    operation: Mapped["Operation | None"] = relationship(back_populates="assignments")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="assignments")


class ResourceType(TimestampMixin, db.Model):
    __tablename__ = "resource_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str | None] = mapped_column(String(50), index=True)


class ResourceSnapshot(TimestampMixin, db.Model):
    __tablename__ = "resource_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nation_id: Mapped[int] = mapped_column(ForeignKey("nations.id"), nullable=False, index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    simulation_id: Mapped[int | None] = mapped_column(ForeignKey("simulations.id"), index=True)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(255))
    confidence_level: Mapped[float | None] = mapped_column(Float)
    metrics: Mapped[dict | None] = mapped_column(jsonb_type)

    nation: Mapped["Nation"] = relationship()
    region: Mapped["GeographicRegion | None"] = relationship()
    balances: Mapped[list["ResourceBalance"]] = relationship(back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("nation_id", "simulation_id", "snapshot_date", name="uq_snapshot_nation_sim_date"),)


class ResourceBalance(TimestampMixin, db.Model):
    __tablename__ = "resource_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("resource_snapshots.id"), nullable=False, index=True)
    resource_type_id: Mapped[int] = mapped_column(ForeignKey("resource_types.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    reserved_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    allocated_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    snapshot: Mapped["ResourceSnapshot"] = relationship(back_populates="balances")
    resource_type: Mapped["ResourceType"] = relationship()

    __table_args__ = (
        UniqueConstraint("snapshot_id", "resource_type_id", name="uq_balance_snapshot_type"),
        Index("ix_resource_balances_snapshot_resource", "snapshot_id", "resource_type_id"),
    )


class Simulation(TimestampMixin, db.Model):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    scenario_name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    side: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    seed: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="in_progress", nullable=False, index=True)
    current_turn: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parameters: Mapped[dict | None] = mapped_column(jsonb_type)
    latest_outcome: Mapped[dict | None] = mapped_column(jsonb_type)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="simulations")
    decisions: Mapped[list["SimulationDecision"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    outcomes: Mapped[list["SimulationOutcome"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    audits: Mapped[list["SimulationAuditEvent"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")


class IntelligenceReport(TimestampMixin, db.Model):
    __tablename__ = "intelligence_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int | None] = mapped_column(ForeignKey("simulations.id"), index=True)
    nation_id: Mapped[int | None] = mapped_column(ForeignKey("nations.id"), index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    report_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    classification: Mapped[str | None] = mapped_column(String(50), index=True)
    source_type: Mapped[str | None] = mapped_column(String(100))
    report_type: Mapped[str | None] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    decoded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence_level: Mapped[float | None] = mapped_column(Float)
    source_reference: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)

    simulation: Mapped["Simulation | None"] = relationship()
    nation: Mapped["Nation | None"] = relationship()
    region: Mapped["GeographicRegion | None"] = relationship()


class WarEvent(TimestampMixin, db.Model):
    __tablename__ = "war_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    battle_id: Mapped[int | None] = mapped_column(ForeignKey("battles.id"), index=True)
    operation_id: Mapped[int | None] = mapped_column(ForeignKey("operations.id"), index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)
    source: Mapped[str | None] = mapped_column(String(255))
    confidence_level: Mapped[float | None] = mapped_column(Float)

    region: Mapped["GeographicRegion | None"] = relationship()
    battle: Mapped["Battle | None"] = relationship()
    operation: Mapped["Operation | None"] = relationship()

    __table_args__ = (Index("ix_war_events_date_type", "event_date", "event_type"),)


class WarCrime(TimestampMixin, db.Model):
    __tablename__ = "war_crimes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    war_event_id: Mapped[int] = mapped_column(ForeignKey("war_events.id"), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    location_name: Mapped[str | None] = mapped_column(String(200))
    victims: Mapped[str | None] = mapped_column(Text)
    perpetrators: Mapped[str | None] = mapped_column(Text)
    death_toll: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[list | None] = mapped_column(jsonb_type)
    media_url: Mapped[str | None] = mapped_column(String(255))
    sensitivity_notes: Mapped[str | None] = mapped_column(Text)

    war_event: Mapped["WarEvent"] = relationship()


class TimelineEntry(TimestampMixin, db.Model):
    __tablename__ = "timeline_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int | None] = mapped_column(ForeignKey("simulations.id"), index=True)
    war_event_id: Mapped[int | None] = mapped_column(ForeignKey("war_events.id"), index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("geographic_regions.id"), index=True)
    entry_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    headline: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    entry_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    payload: Mapped[dict | None] = mapped_column(jsonb_type)


class SimulationDecision(TimestampMixin, db.Model):
    __tablename__ = "simulation_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False, index=True)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_nation_id: Mapped[int | None] = mapped_column(ForeignKey("nations.id"), index=True)
    payload: Mapped[dict] = mapped_column(jsonb_type, nullable=False)

    simulation: Mapped["Simulation"] = relationship(back_populates="decisions")
    actor_nation: Mapped["Nation | None"] = relationship()

    __table_args__ = (Index("ix_simulation_decision_lookup", "simulation_id", "turn_number", "decision_type"),)


class SimulationOutcome(TimestampMixin, db.Model):
    __tablename__ = "simulation_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False, index=True)
    decision_id: Mapped[int | None] = mapped_column(ForeignKey("simulation_decisions.id"), index=True)
    success_probability: Mapped[float] = mapped_column(Float, nullable=False)
    realized_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    weighted_score: Mapped[float] = mapped_column(Float, nullable=False)
    narrative_summary: Mapped[str] = mapped_column(Text, nullable=False)
    impact_payload: Mapped[dict] = mapped_column(jsonb_type, nullable=False)

    simulation: Mapped["Simulation"] = relationship(back_populates="outcomes")
    decision: Mapped["SimulationDecision | None"] = relationship()


class SimulationAuditEvent(TimestampMixin, db.Model):
    __tablename__ = "simulation_audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False, index=True)
    decision_id: Mapped[int | None] = mapped_column(ForeignKey("simulation_decisions.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    detail: Mapped[dict] = mapped_column(jsonb_type, nullable=False)

    simulation: Mapped["Simulation"] = relationship(back_populates="audits")
    decision: Mapped["SimulationDecision | None"] = relationship()


class ImportBatch(TimestampMixin, db.Model):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    metadata_json: Mapped[dict | None] = mapped_column(jsonb_type)


Index("ix_simulations_user_status", Simulation.user_id, Simulation.status)
