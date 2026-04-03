from src.ww2ops.services.seed_service import SeedService


def seed_database():
    SeedService().seed_reference_data()
