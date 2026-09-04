# Decoupling Individual Users from Project Accounts

The legacy codebase couples authentication and research proposals into a single custom user model (`Project(AbstractUser)`), which prevents individual researchers and staff from maintaining personal identities. We decided that the target architectural direction is to separate individual human `User` models from the `Project` (scientific proposal / allocation) entity, allowing multiple users to belong to a project and carry their own permissions.
