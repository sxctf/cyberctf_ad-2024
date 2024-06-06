from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# For vboard >>>

class Station(models.Model):
    name = models.CharField(max_length=32, default='Station')
    content = models.TextField(max_length=500, default='')
    color = models.TextField(max_length=10, default='000000')

    def __str__(self):
        return f'{self.id} - {self.name}'


class Bid(models.Model):
    idb = models.CharField(max_length=120, default='')
    title = models.CharField(max_length=32)
    content = models.TextField(max_length=500, default='')
    serial_key = models.TextField(max_length=40, default='')
    status = models.BooleanField(default=False)
    date = models.DateField()
    bid_view_total = models.IntegerField(default=0)
    bid_view_cur = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.id} - {self.title}'


class Promo(models.Model):
    promo_key = models.TextField(max_length=120, default='')
    status = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    idbid = models.ForeignKey(Bid, on_delete=models.PROTECT, null=True)


class Event(models.Model):
    type = models.IntegerField()
    time = models.DateTimeField()
    idp = models.IntegerField()

    def __str__(self):
        return f'{self.type} - {self.time} - {self.idp}'
