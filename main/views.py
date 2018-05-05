import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView

from main.forms import UserForm
from main.models import SuggestedProblem
from main.oauth import OAuthSignIn
from justdoist.settings import LOGIN_URL


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
        "problem_text": problem,
        "button": button,
        "stats": stats,
    }
    return render(request, 'index.html', context=context)


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
    request.user.save()
    return redirect('index')


@login_required(login_url=LOGIN_URL)
def profile(request, data):
    if data == 'add':
        pr = request.user.get_problem()['problem']
        pr.is_being_solved = True
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
            'id': prob.problem_num
        })

    return render(request, 'profile.html', context={"probs": problems})


@login_required(login_url=LOGIN_URL)
def settings(request):
    return render(request, 'settings.html')


@login_required(login_url=LOGIN_URL)
def contact_us(request):
    return render(request, 'contact_us.html')


@login_required(login_url=LOGIN_URL)
def problem(request):
    uid = request.GET.get('problem_id', None)
    if uid is None:
        return JsonResponse({"error": "missing `problem_id` param"}, status=422)
    problem = SuggestedProblem.get(uid) 
    steps =  problem.steps.replace("*", "")
    trackers = problem.steps_trackers
    # TODO: Finish func


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
