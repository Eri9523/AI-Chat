from domain.entities.user import UserEntity
from domain.repositories.user_repository import IUserRepository
from infrastructure.database.models.user_model import UserModel


class MongoUserRepository(IUserRepository):
    def find_by_id(self, id: str) -> UserEntity | None:
        user = UserModel.objects(id=id).first()
        if not user:
            return None
        return self._to_domain(user)
    
    def find_by_email(self, email: str) -> UserEntity | None:
        user = UserModel.objects(email=email.lower()).first()
        if not user:
            return None
        return self._to_domain(user)
    
    def create(self, user: UserEntity) -> UserEntity:
        new_user = UserModel(
            email=user.email,
            name=user.name,
            password=user.password,
            phone=user.phone,
            address = user.address
        )

        saved = new_user.save()
        return self._to_domain(saved)
    
    def update(self, id: str, user_data: dict) -> UserEntity | None:
        user = UserModel.objects(id=id).modify(
            new=True,
            **user_data
        )
        if not user:
            return None
        return self._to_domain(user)
    
    def delete(self, id: str) -> bool:
        result = UserModel.objects(id=id).delete()
        return result > 0
    
    def _to_domain(self, user_doc) -> UserEntity:
        return UserEntity(
            id=str(user_doc.id),
            email=user_doc.email,
            name=user_doc.name,
            password=user_doc.password,
            phone=user_doc.phone,
            address=user_doc.address,
            created_at=user_doc.created_at,
            updated_at=user_doc.updated_at
        )