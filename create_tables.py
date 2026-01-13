from app.core.database import engine
from app.models.base import Base
# Import all models to ensure they are registered with Base
from app.models.organization import Organization
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.organization_member import OrganizationMember
from app.models.member_role import MemberRole
from app.models.role_permission import RolePermission

def create_tables():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
