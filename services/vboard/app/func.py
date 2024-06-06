from django.template import engines
from django.contrib.auth.models import User
import random, string
import logging
from datetime import date, datetime
from .cfg import station_start, bid_start, admin_username, admin_password
from .models import Station, Bid
#from .views import log


def f_fromhost(request):
    if request.META.get('HTTP_X_REAL_IP'):
        return request.META.get('HTTP_X_REAL_IP')
    else:
        return request.META['REMOTE_ADDR']


def f_db_table_init():
    print("Exec> f_db_table_init..")
#    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": "f_db_table_init()", "user_id": "*",  "user": "*", "req": "*", "reqdata": "*"}, "agent": {"name": "*","ip": "*","type": "app"},"fromhost": "*"})
    try:
        users = User.objects.filter(username=admin_username).order_by('-id')
        if len(users) == 0:
            usr = User.objects.create_superuser(admin_username, f'{admin_username}@ctflab.tech', admin_password)
            try:
                usr.save()
    #            log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": "f_db_table_init() - reg admin django", "user_id": "*",  "user": f"{admin_username}", "req": "*", "reqdata": f"{admin_password}"}, "agent": {"name": "*","ip": "*","type": "app"},"fromhost": "*"})
            except:
                pass
    #            log.info({"event": {"datetime": datetime.today().isoformat(), "level": "ERROR", "result": "Failed", "function": "f_db_table_init() - reg admin django", "user_id": "*",  "user": f"{admin_username}", "req": "*", "reqdata": f"{admin_password}"}, "agent": {"name": "*","ip": "*","type": "app"},"fromhost": "*"})
        bids = Bid.objects.all()
        if len(bids) == 0:
            for b in bid_start:
                bid = Bid(
                    title=b['title'],
                    content=b['content'],
                    date=date.today(),
                    status=True,
                    bid_view_total = -1,
                )
                bid.save()
    #        log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": "f_db_table_init() - insert promo bid", "user_id": "*",  "user": "*", "req": "*", "reqdata": "*"}, "agent": {"name": "*","ip": "*","type": "app"},"fromhost": "*"})
        stations = Station.objects.all()
        if len(stations) == 0:
            for s in station_start:
                station = Station(
                    name=s['name'],
                    content=s['content'],
                )
                station.save()
    #        log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": "f_db_table_init() - insert station", "user_id": "*",  "user": "*", "req": "*", "reqdata": "*"}, "agent": {"name": "*","ip": "*","type": "app"},"fromhost": "*"})
    except:
        print("Dont init_db")


def f_promokeygen(user_id, idbid):
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
    str = ''.join(random.choice(chars) for _ in range(22))
    promo_key = f'pk{ user_id }{ idbid }-' + str
    return promo_key


def f_pagenotfound(req):
    engine = engines["django"]
    template = engine.from_string(f'<!DOCTYPE html><html><head><meta charset=\"UTF-8\"><title>VBoard - Page not found</title></head><body><h1>[V.B0ARD]</h1><h3>Page [{ req }] not found!</h3></body></html>')
    return template
