from django.db import models


class DataBaseModels(models.Model):
    """
    Abstract base model that includes timestamp fields for creation and updates.

    Attributes:
    - created_at: A DateTime field that records the time when the object is created. 
                  Automatically set to the current date and time when the object is first created.
    - updated_at: A DateTime field that records the time when the object is last updated.
                  Automatically set to the current date and time every time the object is updated.
    
    Meta:
    - abstract: This is an abstract base class, so it won't create a separate table in the database.
                Instead, it provides these fields to any model that inherits from it.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
