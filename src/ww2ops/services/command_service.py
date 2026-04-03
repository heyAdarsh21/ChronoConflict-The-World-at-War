import json

from src.ww2ops.db.models import Leader
from src.ww2ops.repositories.command_repository import CommandRepository


class CommandService:
    def list_leaders(self, country=None, role_type=None, search=None, page=1, per_page=12):
        query = CommandRepository.query_leaders(country=country, role_type=role_type, search=search)
        pagination = query.order_by(Leader.influence_score.desc().nullslast()).paginate(page=page, per_page=per_page, error_out=False)
        countries = sorted({leader.nation.name for leader in Leader.query.all() if leader.nation})
        role_types = sorted({leader.role_type for leader in Leader.query.all() if leader.role_type})
        return {
            "leaders": [
                {
                    "id": leader.id,
                    "name": leader.name,
                    "country": leader.nation.name if leader.nation else "Unknown",
                    "side": leader.nation.side if leader.nation else "unknown",
                    "title": leader.title,
                    "role_type": leader.role_type,
                    "portrait_url": leader.portrait_url,
                    "influence_score": leader.influence_score or 0,
                    "biography_excerpt": (leader.biography or "")[:200] + ("..." if leader.biography and len(leader.biography) > 200 else ""),
                    "key_operations": json.dumps((leader.metadata_json or {}).get("key_operations", [])),
                    "born_on": leader.born_on.isoformat() if leader.born_on else None,
                    "died_on": leader.died_on.isoformat() if leader.died_on else None,
                    "assignments_count": len(leader.assignments),
                }
                for leader in pagination.items
            ],
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
            "countries": countries,
            "role_types": role_types,
        }

    def get_leader(self, leader_id: int):
        leader = Leader.query.get_or_404(leader_id)

        # Build co-commander network from shared operations/campaigns
        peers = set()
        for assignment in leader.assignments:
            if assignment.operation:
                for other in assignment.operation.assignments:
                    if other.leader_id != leader.id and other.leader:
                        peers.add((other.leader.id, other.leader.name, other.leader.nation.name if other.leader.nation else "Unknown"))
            if assignment.campaign:
                for other in assignment.campaign.assignments:
                    if other.leader_id != leader.id and other.leader:
                        peers.add((other.leader.id, other.leader.name, other.leader.nation.name if other.leader.nation else "Unknown"))

        return {
            "id": leader.id,
            "name": leader.name,
            "country": leader.nation.name if leader.nation else "Unknown",
            "side": leader.nation.side if leader.nation else "unknown",
            "title": leader.title,
            "role_type": leader.role_type,
            "biography": leader.biography,
            "ideology": leader.ideology,
            "portrait_url": leader.portrait_url,
            "notable_quotes": json.dumps(leader.notable_quotes or []),
            "key_operations": json.dumps((leader.metadata_json or {}).get("key_operations", [])),
            "influence_score": leader.influence_score,
            "born_on": leader.born_on.isoformat() if leader.born_on else None,
            "died_on": leader.died_on.isoformat() if leader.died_on else None,
            "assignments": [
                {
                    "id": assignment.id,
                    "position": assignment.position,
                    "start_date": assignment.start_date.isoformat() if assignment.start_date else None,
                    "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                    "notes": assignment.notes,
                    "context": {
                        "type": "operation" if assignment.operation else "campaign",
                        "id": assignment.operation.id if assignment.operation else (assignment.campaign.id if assignment.campaign else None),
                        "name": assignment.operation.name if assignment.operation else (assignment.campaign.name if assignment.campaign else "Unknown"),
                        "code_name": assignment.operation.code_name if assignment.operation else None,
                        "start_date": assignment.operation.start_date.isoformat() if assignment.operation and assignment.operation.start_date else None,
                        "end_date": assignment.operation.end_date.isoformat() if assignment.operation and assignment.operation.end_date else None,
                        "outcome": assignment.operation.outcome if assignment.operation else (assignment.campaign.outcome if assignment.campaign else None),
                        "region": assignment.operation.region.name if assignment.operation and assignment.operation.region else None,
                        "theater": assignment.campaign.theater if assignment.campaign else None,
                    },
                }
                for assignment in leader.assignments
            ],
            "command_network": [
                {"id": pid, "name": pname, "country": pcountry}
                for pid, pname, pcountry in sorted(peers, key=lambda x: x[1])
            ],
        }
