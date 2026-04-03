from src.ww2ops.db.models import Simulation


class SimulationRepository:
    @staticmethod
    def get_for_user(simulation_id: int, user_id: int):
        return Simulation.query.filter_by(id=simulation_id, user_id=user_id).first()
