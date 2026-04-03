from src.ww2ops.db.models import Leader


class CommandRepository:
    @staticmethod
    def query_leaders(country=None, role_type=None, search=None):
        query = Leader.query
        if country:
            query = query.filter(Leader.nation.has(name=country))
        if role_type:
            query = query.filter(Leader.role_type == role_type)
        if search:
            like_term = f"%{search}%"
            query = query.filter((Leader.name.ilike(like_term)) | (Leader.biography.ilike(like_term)))
        return query
