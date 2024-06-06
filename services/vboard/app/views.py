from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.template import engines
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in,user_logged_out, user_login_failed
from django.dispatch import receiver
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import date, datetime, timezone
import random
import logging
from .models import *
from .forms import *
from .func import *
from .cfg import PROMO_COUNT, BID_VIEW_COUNT, STATION_TIME

log = logging.getLogger(__name__)

# Create your views here.

def fv_root(request):
    #log.error("Index start", extra={"user": request.user.pk})
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id,  "user": request.user.username, "req": request.method, "reqdata": request.GET}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    return render(request, 'app/index.html')


def fv_app_index(request):
    return render(request, 'app/index.html')


def fv_usreg(request):
    if request.method == 'POST':
        form = UsregForm(request.POST)
        if form.is_valid():
            usr = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            try:
                usr.save()
                log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.POST}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
                return HttpResponseRedirect("/app/login")
            except:
                log.info({"event": {"datetime": datetime.today().isoformat(), "level": "ERROR", "result": "Failed", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.POST}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
                return HttpResponseRedirect("/app/usreg")
    else:
        form = UsregForm()
    return render(request, 'app/usreg.html', context={'formpage': form})



@receiver(user_logged_in)
def login_logger(request, user, **kwargs):
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.POST}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})


@receiver(user_login_failed)
def login_failed_logger(request, *args, **kwargs):
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "ERROR", "result": "Failed", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.POST}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})


@receiver(user_logged_out)
def logout_logger(request, user, **kwargs):
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.POST}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})


@login_required(login_url='login')
def fv_bid(request):
    bid = Bid.objects.filter(user=request.user).order_by('-id')
    pk = Promo.objects.filter(Q(user=request.user) & Q(status=False)).order_by('-id')
    paginator = Paginator(bid, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {
        'bid' : page_obj,
        'pk' : pk,
        'formpage' : PromoForm()
    }
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.GET}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    return render(request, 'app/bid.html', data)


@login_required(login_url='login')
def fv_bid_add(request):
    if request.method == 'POST':
        formpage = BidForm(request.POST)
        if formpage.is_valid():
            bid = Bid(
                title=formpage.cleaned_data['title'],
                content=formpage.cleaned_data['content'],
                serial_key=formpage.cleaned_data['serial_key'],
                date=date.today(),
                user = request.user
            )
            bid.save()
            bid.idb = f'b{ request.user.id }-{ bid.id }'
            bid.save()
            log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"IDB: {bid.idb} data: {request.POST}" }, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
            pk = Promo.objects.filter(Q(user=request.user)).order_by('-id')
            idbid = 0
            if len(pk) > 0:
                idbid = pk[0].idbid.id
            bids = Bid.objects.filter(Q(id__gt=idbid) & Q(user=request.user) & Q(bid_view_total=0) & Q(status=False)).order_by('-id')
            if len(bids) > PROMO_COUNT:
                pk = Promo(
                    promo_key = f_promokeygen(request.user.id, bid.id),
                    user = request.user,
                    idbid = bid
                )
                pk.save()
                log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"IDB: {bid.idb} Generate promo_key: {pk.promo_key}"}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
            return HttpResponseRedirect("/app/bid")
    else:
        formpage = BidForm()
    return render(request, 'app/bid_add.html', context={'formpage': formpage})


@login_required(login_url='login')
def fv_bid_id(request, rq_idb):
    bid = Bid.objects.filter(Q(idb=rq_idb) & Q(user=request.user)).order_by('-id')
    data = {'bid' : bid }
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"IDB: {bid[0].idb} data: {request.GET}" }, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    return render(request, 'app/bid.html', data)


@login_required(login_url='login')
def fv_bid_edit(request, rq_idb):
    bid = Bid.objects.get(idb=rq_idb)
    if request.method == 'POST':
        formpage = BidForm(request.POST)
        if formpage.is_valid():
            if len(formpage.cleaned_data['title']) > 0: bid.title=formpage.cleaned_data['title']
            if len(formpage.cleaned_data['content']) > 0: bid.content=formpage.cleaned_data['content']
            if len(formpage.cleaned_data['serial_key']) > 0: bid.serial_key=formpage.cleaned_data['serial_key']
            bid.save()
            log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"IDB: {bid.idb} data: {request.POST}" }, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
            return render(request, 'app/bid.html', {'bid':{bid}, 'Comment':"Update bid..."})
    else:
        if bid.user == request.user:
            formpage = BidForm({
                'title' : bid.title,
                'content' : bid.content,
                'serial_key' : bid.serial_key
            })
        else: return HttpResponseRedirect("/app/bid")
    return render(request, 'app/bid_add.html', context={'formpage': formpage})


@login_required(login_url='login')
def fv_bid_del(request, rq_idb):
    try:
        bid = Bid.objects.filter(Q(idb=rq_idb) & Q(user=request.user)).order_by('-id'),
        bid[0].delete()
        log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.GET}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    except:
        pass
    return HttpResponseRedirect("/app/bid")


@login_required(login_url='login')
def fv_promo_active(request):
    if request.method == 'POST':
        form = PromoForm(request.POST)
        if form.is_valid():
            pk = Promo.objects.filter(Q(user=request.user) & Q(promo_key=form.cleaned_data['promo_key'])).order_by('-id')
            bid = Bid.objects.filter(Q(idb=form.cleaned_data['idb'])).order_by('-id')
            if (len(bid) > 0 and len(pk) > 0):
                pk[0].status = True
                pk[0].save()
                bid[0].status = True
                bid[0].bid_view_total = BID_VIEW_COUNT
                bid[0].save()
                comment = f'Apply promo-key: { pk[0].promo_key }'
                log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"IDB: {bid[0].idb} {comment}"}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
            else:
                promo_key = form.cleaned_data['promo_key']
                comment = f'Not Apply promo-key: { promo_key }'
                bid = 0
                log.info({"event": {"datetime": datetime.today().isoformat(), "level": "Error", "result": "Failed", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"IDB: Not found"}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
            return render(request, 'app/bid.html', {'bid':bid, 'comment':comment})
    else: return HttpResponseRedirect("/app/bid")


@login_required(login_url='login')
def fv_station(request):
    field = request.GET.get('field')
    station_count = Station.objects.annotate(**{field: Count("name")})
    data = {'station': station_count}
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.GET}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    return render(request, 'app/station.html', data)


def fv_tablo(request):
    bid = Bid.objects.filter(Q(status=True) & (Q(bid_view_total__gt=0) | Q(bid_view_total=-1))).order_by('-id')
    bidv = 0
    if len(bid) > 0:
        i = random.randint(0, (len(bid)-1))
        bidv = bid[i]
        bid[i].bid_view_cur = bid[i].bid_view_cur + 1
        if bid[i].bid_view_cur == bid[i].bid_view_total: bid[i].bid_view_total = 0
        bid[i].save()
    evt = Event.objects.filter(type=1).order_by('id')
    if len(evt) == 0:
        evt = Event(
            type = 1,
            time = datetime.now(timezone.utc),
            idp = 0
        )
        evt.save()
    evt = Event.objects.filter(type=1).order_by('id')
    station = Station.objects.all().order_by('id')
    stationv = []
    i = evt[0].idp
    delta = ((datetime.now(timezone.utc) - evt[0].time)).total_seconds()
    im_station = len(station)
    if len(station) > 0 and len(evt) > 0 and delta > STATION_TIME:
        ndelta = int (delta // STATION_TIME)
        if ndelta > im_station: i = i + int(delta % im_station)
        else: i = i + ndelta
        if i > (im_station - 1): i = int(i % im_station)
        evt[0].time = datetime.now(timezone.utc)
        evt[0].idp = i
        evt[0].save()
    if i == 0:
        stationv = [station[i], station[(i+1)], station[(i+2)]]
    elif i == (im_station-1):
        stationv = [station[(i-1)], station[i], station[0]]
    else:
        stationv = [station[(i-1)], station[i], station[(i+1)]]
    data = {
            'bid' : bidv,
            'station' : stationv
    }
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": request.GET}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    return render(request, 'app/tablo.html', data)


def fv_rparam(request, rparam: str):
    template = f_pagenotfound(rparam)
    log.info({"event": {"datetime": datetime.today().isoformat(), "level": "INFO", "result": "Succeess", "function": request.path, "user_id": request.user.id, "user": request.user.username, "req": request.method, "reqdata": f"rparam={rparam} GET:{request.GET}"}, "agent": {"name": request.META['SERVER_NAME'],"ip": request.META['HTTP_HOST'],"type": "app"},"fromhost": f_fromhost(request)})
    return HttpResponseNotFound(template.render({}, request))


def fv_init(request):
    f_db_table_init()
    return render(request, 'app/index.html')

