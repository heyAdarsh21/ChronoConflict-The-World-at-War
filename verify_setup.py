"""
Verification script to check if WW2 Intelligence Operations Simulator is ready to run
"""

from app import app
from database import db
from models import Battle, Operation, Resource, Territory, IntelligenceReport, User

def verify_setup():
    """Verify that the application is properly set up"""
    print("=" * 50)
    print("WW2 Intelligence Operations Simulator - Setup Verification")
    print("=" * 50)
    print()
    
    with app.app_context():
        # Check database connection
        try:
            db.session.execute(db.text("SELECT 1"))
            print("[OK] Database connection: OK")
        except Exception as e:
            print(f"[FAIL] Database connection: FAILED - {e}")
            return False
        
        # Check tables
        tables = ['battles', 'operations', 'resources', 'territories', 'intelligence_reports', 'users', 'simulations']
        print("\nDatabase Tables:")
        for table in tables:
            try:
                result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  [OK] {table}: {count} records")
            except Exception as e:
                print(f"  [FAIL] {table}: ERROR - {e}")
                return False
        
        # Check seed data
        print("\nSeed Data Status:")
        print(f"  Battles: {Battle.query.count()}")
        print(f"  Operations: {Operation.query.count()}")
        print(f"  Resources: {Resource.query.count()}")
        print(f"  Territories: {Territory.query.count()}")
        print(f"  Intelligence Reports: {IntelligenceReport.query.count()}")
        print(f"  Users: {User.query.count()}")
        
        # Check routes
        print("\nRegistered Routes:")
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"  {rule.methods} {rule.rule}")
        print("\n".join(sorted(set(routes))[:10]))  # Show first 10 routes
        print("  ...")
        
        print("\n" + "=" * 50)
        print("[OK] SETUP VERIFICATION COMPLETE")
        print("=" * 50)
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nOr use the startup scripts:")
        print("  run.bat (Windows)")
        print("  run.ps1 (PowerShell)")
        print("\nThen access: http://localhost:5000")
        print()
        
        return True

if __name__ == '__main__':
    verify_setup()

