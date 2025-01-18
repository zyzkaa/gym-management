from lib2to3.fixes.fix_input import context
from time import strftime
from unicodedata import category

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import request

from users.models import User, Visit, Membership, Coach, Payment
from django.contrib.auth import login, logout

# dodaj wizyty, moze jakis qr kod?
# moze laczenie z zegarkami czy cos do treningow

from users.forms import ClientRegisterForm
from workout.models import Workout


def register(request):
    context = {
        'title' : 'Register'
    }
    form = ClientRegisterForm()
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            form.save()
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('/users/memberships')
        else:
            error = form.errors
            return HttpResponse('error' + str(error))

    context['form'] = form
    return render(request, 'users/register.html', context)

def login_user(request):
    context = {}
    form = AuthenticationForm()
    if request.method == 'POST':
      #  form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect('/users/profile')

    context['form'] = form
    return render(request, 'users/login.html', context)

def logout_user(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
    return redirect("/")

@login_required
def user_current_profile(request):
    user = request.user
    workouts = Workout.objects.filter(client=user)
    context = {
        'user': user,
        'workouts': workouts,
        }
    return render(request, 'users/profile.html', context)



def coach_profile(request):
    return render(request, 'users/coach_profile.html')

def user_profile(request):
    return render(request, 'users/user_profile.html')

from datetime import date, datetime
def add_visit(request, user_id):
    #   user_id = request.user_id
    try:
        user = User.objects.get(pk=user_id)
        visit = Visit.objects.create(client=user, date=date.today(), enter_time=datetime.now().strftime("%H:%M:%S"))
        visit.save()
        return HttpResponse('ok')
    except User.DoesNotExist:
        return HttpResponse('no such user')

def show_memberships(request):
    memberships = Membership.objects.all()
    context = {
        'memberships': memberships,
    }
    return render(request, 'users/memberships.html', context)

from dateutil.relativedelta import relativedelta
def payment(request, membership_id):
    if request.method == 'POST':
        user = request.user
        client = user.client
        client.membership = Membership.objects.filter(id=membership_id).get()
        client.save()
        payment_method = request.POST.get('method')
        months, price = request.POST.get('option').split(':')
        payments = [Payment.objects.create(
            date = date.today() + relativedelta(months=(month-1)),
            client = request.user,
            amount = price,
            method = payment_method,
            status = 'completed' if month==1 else 'scheduled',
        )  for month in range(1, int(months) + 1)]
        for payment in payments:
            payment.save()
        return HttpResponse("paid")

    try:
        membership = Membership.objects.filter(pk=membership_id).get()
        prices = {
            int(field.name.split('_')[-1]): getattr(membership, field.name)
            for field in membership._meta.get_fields()
            if field.name.startswith('price_')
        }

        context = {
            'membership': membership,
            'payment_options': Payment._meta.get_field('method').choices,
            'prices': prices,
        }
        return render(request, 'users/payment.html', context)
    except Membership.DoesNotExist:
        return HttpResponse('no such membership')

def cancel_membership(request):
    user = request.user
    user.client.membership = None
    user.client.save()
    payments = Payment.objects.filter(client=user).filter(status='scheduled')
    for payment in payments:
        payment.status = 'cancelled'
        payment.save()
    return redirect('/users/profile')

def show_coaches(request):
    coaches = User.objects.filter(is_coach=True)
    context = {
        'coaches': coaches,
    }
    return render(request, 'users/coaches.html', context)


# def register(request):
#     if request.method == "POST":
#         form = ClientRegisterForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = User(username=username, password=make_password(password))
#             user.save()
#             return HttpResponse("success")
#     else:
#         form = ClientRegisterForm()
#
#     return render(request, 'users/register.html', {form: form})


# # ...
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/detail.html", {"question": question})