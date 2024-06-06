from django.contrib import admin
from .models import Bid

# Register your models here.
#admin.site.register(Author)


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['date', 'idb', 'user', 'title', 'status']
    ordering = ['-id']
    search_fields = ['title']
    fields = ['idb', 'title', 'content', 'serial_key', 'user', 'status']
    readonly_fields = ['serial_key', 'user', 'idb']
    list_per_page = 10