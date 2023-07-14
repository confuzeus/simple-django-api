from django.db import models


class EmailAddressManager(models.Manager):
    def primary(self):
        return self.get(is_primary=True)
