from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from psycopg2 import OperationalError
from django.db.utils import IntegrityError
from core.db.manager import DataHubManager

# Note that these may fire multiple times and for users that already exist.


@receiver(pre_save, sender=User,
          dispatch_uid="dh_user_pre_save_unique_email")
def enforce_email_uniqueness(sender, instance, **kwargs):
    """
    Validates new user attributes at database save time.

    Check is made both here and in the pipeline form to ensure the provided
    email address is not being used by another user.
    """
    if instance is not None:
        email = instance.email
        username = instance.username
        if not email:
            raise IntegrityError("Email required.")
        if (sender.objects
                .filter(email=email)
                .exclude(username=username)
                .count()):
            raise IntegrityError(
                "The email address {0} is associated with another account."
                .format(email)
            )


@receiver(pre_save, sender=User,
          dispatch_uid="dh_user_pre_save_create_user_db_and_data_folder")
def create_user_db_and_data_folder_if_needed(sender, instance, **kwargs):
    """
    Creates a Postgres role and db and data folder to go with new Django users.

    Raises an exception if the role, database, or user data folder exists
    before this user.
    """
    username = instance.username
    hashed_password = instance.password

    # The Django user doesn't exist yet, so we can't just try to create a
    # DataHubManager connection as the user. We need to act as the db
    # superuser and check for any existing db role or database.
    db_exists = DataHubManager.database_exists(username)
    user_exists = DataHubManager.user_exists(username)
    user_data_folder_exists = DataHubManager.user_data_folder_exists(username)
    if db_exists and user_exists and user_data_folder_exists:
        # Make sure new users don't inherit orphaned roles or databases that
        # are missing a matching Django user.
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise IntegrityError("Failed to create user. That name is already"
                                 " in use by an orphaned user.")
    elif not db_exists and not user_exists and not user_data_folder_exists:
        try:
            DataHubManager.create_user(
                username=username,
                password=hashed_password)
        except OperationalError:
            raise
    else:
        raise Exception("Failed to create user. That name is already"
                        " in use by either a role, database, or data folder.")
