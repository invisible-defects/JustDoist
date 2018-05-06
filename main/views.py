import datetime

import stripe
from django.http import JsonResponse, HttpResponseNotFound
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView

from main.forms import UserForm
from main.models import SuggestedProblem, PremiumSubscription
from main.oauth import OAuthSignIn
from justdoist.settings import (
    LOGIN_URL, STRIPE_PUBLIC_KEY,
    STRIPE_SECRET_KEY, PREMIUM_PRICE_PER_DAY, PREMIUM_PRICE_PER_WEEK
)
stripe.api_key = STRIPE_SECRET_KEY


# NOTE: for better project scalability
# we should consider to replace function-based views with class-based views
# and (probably) implement a RESTful API.
@login_required(login_url=LOGIN_URL)
def index(request):
    problem_q = request.user.get_problem()
    button = True

    if problem_q['status'] == 'no':
        problem = "Seems like you have no problems now.\nHooray!\nCome back later."
        button = False
    elif problem_q['status'] == 'time':
        problem = "Come back tomorrow for more advice!\nYou can work on your current problems now."
        button = False
    else:
        problem = problem_q['problem'].suggested_problem.body

    stats = request.user.get_stats()
    context = {
        "problem_text": problem.replace('\n', '<br>'),
        "button": button,
        "stats": stats,
    }
    return render(request, 'index.html', context=context, status=200)

def landingpage(request):
    return HttpResponseNotFound(render(request, "landingpage.html").content)


def handler404(request):
    return HttpResponseNotFound(render(request, "404.html").content)


def login(request):
    if request.user.is_authenticated:
        return redirect("index")
    return render(request, 'login.html')


@login_required(login_url=LOGIN_URL)
def authorize(request, provider):
    oauth = OAuthSignIn.get_provider(provider)
    return redirect(oauth.authorize(request))


@login_required(login_url=LOGIN_URL)
def oauth_callback(request, provider):
    oauth = OAuthSignIn.get_provider(provider)
    token = oauth.callback(request)

    # TODO: add failure page/message
    if token is None:
        return redirect('index')

    request.user.todoist_token = token
    request.user.update_avatar()
    request.user.save()
    return redirect('index')


@login_required(login_url=LOGIN_URL)
def progress(request, data):
    if data == 'add':
        pr = request.user.get_problem()['problem']
        pr.is_being_solved = True
        pr.save()
        request.user.last_problem_shown = datetime.datetime.now()
        request.user.save()

    problems = []
    problem_probs = request.user.suggested_problems.all().filter(is_being_solved=True)
    for prob in problem_probs:
        prob_raw = prob.suggested_problem
        problems.append({
            'title': prob_raw.title,
            # TODO: Extract this snippet to a function in purpose of increasing readability
            'percantage': min(
                int(int(prob.steps_completed) / int(prob_raw.steps_num) * 100),
                100
            ),
            'id': prob.suggested_problem.uid
        })

    context = {
        "probs": problems,
    }
    return render(request, 'progress.html', context=context)


@login_required(login_url=LOGIN_URL)
def change_color(request):
    if not request.user.has_subscription:
        return JsonResponse({"error": "user has no premium"}, status=422)
    color = request.GET.get('hex', None)
    if color is None:
        return JsonResponse({"error": "missing `hex` param"}, status=422)
    request.user.color = color
    request.user.save()
    return JsonResponse({"success": "color was changed"}, status=200)


@login_required(login_url=LOGIN_URL)
def default_progress(request):
    return redirect("/progress/no_add")


@login_required(login_url=LOGIN_URL)
def settings(request):
    context = {
        "premium": request.user.has_subscription,
        "email": request.user.email,
        "name": request.user.username,
    }
    return render(request, 'settings.html', context=context)


@login_required(login_url=LOGIN_URL)
def contact_us(request):
    return render(request, 'contact_us.html')


@login_required(login_url=LOGIN_URL)
def problem(request):
    uid = request.GET.get('problem_id', None)
    if uid is None:
        return JsonResponse({"error": "missing `problem_id` param"}, status=422)
    problem = SuggestedProblem.get(uid) 
    proba = problem.probabilities.all().filter(user=request.user).first()
    return JsonResponse(proba.json, status=200, safe=False)


@login_required(login_url=LOGIN_URL)
def add_task(request):
    task_text = request.GET.get('text', None)
    task_id = request.GET.get('id', None)
    step_num = request.GET.get('step', None)

    if task_text is None:
        return JsonResponse({"error": "missing `text` param"}, status=422)

    if task_id is None:
        return JsonResponse({"error": "missing `id` param"}, status=422)

    if step_num is None:
        return JsonResponse({"error": "missing `step` param"}, status=422)

    request.user.add_problem(task_text, task_id, step_num)
    return JsonResponse({"status": "ok"}, status=200)


@login_required(login_url=LOGIN_URL)
def link(request, service):
    # TODO: add better handler
    if service == 'todoist':
        return render(request, "todoist_login.html")
    return redirect("index.html")


@login_required(login_url=LOGIN_URL)
def statistics(request):
    stats = request.user.get_stats()
    return JsonResponse(stats, status=200)


class Register(CreateView):
    success_url = reverse_lazy('index')
    template_name = "registration.html"
    form_class = UserForm

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()

        return super().form_valid(form)


@login_required(login_url=LOGIN_URL)
def payments(request):
    # Redirect in the case of missing SMI integration
    if request.user.todoist_token is None:
        return redirect("index")

    # Redirect if user is already subscribed
    if request.user.has_subscription:
        return render(request, "settings.html", context={"showSubscriptionToast": True})

    context = {
        "stripe_key": STRIPE_PUBLIC_KEY,
        "price_weekly": PREMIUM_PRICE_PER_WEEK,
    }
    return render(request, 'payments.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url=LOGIN_URL)
def checkout(request, kind):
    if kind not in PremiumSubscription.KINDS:
        return render(
            request, "failure",
            context={"error": "Invalid subscription type"},
            status=422
        )

    try:
        days = PremiumSubscription.VALUES[kind]
        charge = stripe.Charge.create(
            # Stripe accepts amount in cents
            amount=int(days * PREMIUM_PRICE_PER_DAY * 100),
            currency="usd",
            source=request.POST.get("stripeToken"),
            description=f"{days}d subscription to JustDoist Premium"
        )
    except stripe.InvalidRequestError as e:
        return render(request, "failure", context={"error": e}, status=400)
    except stripe.error.CardError as e:
        return render(request, "failure", context={"error": e}, status=422)

    sub = PremiumSubscription(
        user=request.user,
        days=PremiumSubscription.VALUES[kind],
        charge_id=charge.id
    )
    sub.save()
    # TODO: add achievement check
    # request.user.achievements

    context = {
        "new_achievement": True,
        "achievement_image": "/static/img/logo.svg",
        "achievement_text": "Premium User",
    }
    return render(request, "success.html", context=context, status=200)


@login_required(login_url=LOGIN_URL)
def failure(request):
    return render(request, "failure.html")


@login_required(login_url=LOGIN_URL)
def success(request):
    if not request.user.has_subscription:
        return redirect("payments")
    return render(request, "success.html")
