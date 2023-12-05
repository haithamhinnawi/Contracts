from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import ProfileManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class Profile(AbstractBaseUser, PermissionsMixin):
    '''
    This model describes the profile information of the user.
    '''
    type_choices = [
        ('Client', 'Client'),
        ('Contractor', 'Contractor'),
    ]
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    profession = models.CharField(max_length=200)
    balance = models.IntegerField(default=0)
    type = models.CharField(
        max_length=10,
        choices=type_choices,
        default='Client'
    )
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = ProfileManager()
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} - {self.type}"

class Contract(models.Model):
    '''
    This model describes details of a contract
    between client and contractor.
    '''
    status_choices = [
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('terminated', 'Terminated')
    ]
    client = models.ForeignKey(Profile, related_name='client_contracts', on_delete=models.CASCADE, limit_choices_to={'type': 'Client'})
    contractor = models.ForeignKey(Profile, related_name='contractor_contracts',on_delete=models.CASCADE, limit_choices_to={'type': 'Contractor'})
    terms = models.TextField(max_length=200)
    status = models.CharField(
        max_length=15,
        choices=status_choices,
        default='new'
    )
    def __str__(self) -> str:
        return f"Contract between {self.client.first_name} {self.client.last_name} and {self.contractor.first_name} {self.contractor.last_name} - {self.status}"

class Job(models.Model):
    '''
    This model describes job detail of specific contract.
    '''
    description = models.CharField(max_length=200)
    price = models.IntegerField()
    paid = models.BooleanField()
    payment_date = models.DateField()
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)