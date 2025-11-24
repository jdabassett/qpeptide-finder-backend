"""
Factory for creating Digest test data.
"""

# TODO this needs work
# import random

# from factory import LazyFunction, SubFactory
# from factory.alchemy import SQLAlchemyModelFactory

# from app.enums.digest_statuses import DigestStatusEnum
# from app.enums.proteases import ProteaseEnum
# from app.models.digest import Digest
# from tests.factories.models.protein_factory import ProteinFactory
# from tests.factories.models.user_factory import UserFactory


# class DigestFactory(SQLAlchemyModelFactory):
#     """Factory for creating Digest instances."""

#     class Meta:
#         model = Digest
#         sqlalchemy_session_persistence = "commit"

#     status = DigestStatusEnum.PROCESSING
#     user = SubFactory(UserFactory)
#     protein = SubFactory(ProteinFactory)

#     @post_generation
#     def create_proteases(self, create, extracted, **kwargs):
#         """Create associated proteases after digest is created."""
#         if not create:
#             return

#         from app.models.digest_proteases import DigestProtease

#         # Default: create one random protease
#         proteases = extracted if extracted else [random.choice(list(ProteaseEnum))]

#         for order, protease in enumerate(proteases):
#             DigestProtease(
#                 digest_id=self.id,
#                 protease=protease,
#                 order=order
#             )
