from django.shortcuts import render, redirect
from .forms import UserForm, ResumeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, timedelta
from .models import QuestionAnswer, UserProfile
import openai
import json
from dotenv import load_dotenv
import os
import copy

load_dotenv()


# Create your views here.
openai.api_key = os.getenv("API_KEY")

app_name = "HCI Project"

default_history = [
    {
        "role": "system",
        "content": """
我想要進行研究所面試的練習，強化我的面試技巧。你將會是扮演面試我的教授。對話開始後請直接進入角色情境，不要說多餘的話。
你需要設計模擬情境，讓我可以跟你進行一來一往的對話。你問一句後，要等我回答之後，你再問下一句。
你將扮演這個情境的教授角色，我將扮演接受面試的學生，你會根據我的大學科系、報考動機、進入研究所後的規劃等方面，制定問題。
一個問題接著一個問題的形式，用專業的口吻問我問題，直到你覺得，我的回應已經足夠讓你判斷我有沒有資格錄取。
如果我在面試上表現的非常不錯，你還會出更專業的問題給我。過程當中你不需要解釋或者教學，只要扮演一個研究所教授即可。
在你決定結束面試後，請依照我的表現做評分。滿分100分，60分及格。每個人的基本分是30分。
""",
    },
]

history = {}


def index(request):
    context = {"app_name": app_name}
    return render(request, "index.html", context)


@login_required(login_url="signin")
def mockgpt(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=7)

    questions = QuestionAnswer.objects.filter(user=request.user)
    t_questions = questions.filter(created=today)
    y_questions = questions.filter(created=yesterday)
    s_questions = questions.filter(created__gte=seven_days_ago, created__lte=today)

    context = {
        "t_questions": t_questions,
        "y_questions": y_questions,
        "s_questions": s_questions,
    }

    return render(request, "chatapp/mockgpt.html", context)


def info(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "info.html", context)


def NTU(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTU/NTU.html", context)


def HT_Lin(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTU/HT_Lin.html", context)


def Ruey_Feng_Chang(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTU/Ruey_Feng_Chang.html", context)


def P_Lin(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTU/P_Lin.html", context)


def NYCU(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NYCU/NYCU.html", context)


def Lan_Da_Van(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NYCU/Lan_Da_Van.html", context)


def Yen_Yu_Lin(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NYCU/Yen_Yu_Lin.html", context)


def Jung_Hong_Chuang(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NYCU/Jung_Hong_Chuang.html", context)


def NTHU(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTHU/NTHU.html", context)


def Che_Rung_Lee(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTHU/Che_Rung_Lee.html", context)


def Shang_Hong_Lai(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTHU/Shang_Hong_Lai.html", context)


def Ching_Te_Chiu(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTHU/Ching_Te_Chiu.html", context)


def mock(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "mock.html", context)


from django.contrib.auth.models import User
from .models import UserProfile


def identity(request):
    username = request.user.username
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    context = {
        "username": username,
        "app_name": app_name,
        "research_area": profile.research_area,
        "education": profile.education,
        "key_skills": profile.key_skills,
        "work_experiences": profile.work_experiences,
        "relevant_coursework": profile.relevant_coursework,
        "extracurricular": profile.extracurricular,
        "language_skills": profile.language_skills,
    }
    return render(request, "identity.html", context)


@login_required(login_url="signin")
def edit_resume(request):
    username = request.user.username
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)
    if request.method == "POST":
        form = ResumeForm(request.POST)
        if form.is_valid():
            # Access user information from the form data
            research_area = form.cleaned_data["research_area"]
            education = form.cleaned_data["education"]
            key_skills = form.cleaned_data["key_skills"]
            work_experiences = form.cleaned_data["work_experiences"]
            relevant_coursework = form.cleaned_data["relevant_coursework"]
            extracurricular = form.cleaned_data["extracurricular"]
            language_skills = form.cleaned_data["language_skills"]
            profile.research_area = research_area
            profile.education = education
            profile.key_skills = key_skills
            profile.work_experiences = work_experiences
            profile.relevant_coursework = relevant_coursework
            profile.extracurricular = extracurricular
            profile.language_skills = language_skills
            profile.save()
            return redirect("identity")
    else:
        initial = {
            "research_area": profile.research_area,
            "education": profile.education,
            "key_skills": profile.key_skills,
            "work_experiences": profile.work_experiences,
            "relevant_coursework": profile.relevant_coursework,
            "extracurricular": profile.extracurricular,
            "language_skills": profile.language_skills,
        }
        if profile.research_area != "請輸入您的研究領域":
            form = ResumeForm(initial)
        else:
            form = ResumeForm()
    return render(request, "resume.html", {"form": form})


@login_required(login_url="signin")
def edit_resume(request):
    username = request.user.username
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    if request.method == "POST":
        form = ResumeForm(request.POST)

        if form.is_valid():
            # Access user information from the form data
            research_area = form.cleaned_data["research_area"]
            education = form.cleaned_data["education"]
            key_skills = form.cleaned_data["key_skills"]
            work_experiences = form.cleaned_data["work_experiences"]
            relevant_coursework = form.cleaned_data["relevant_coursework"]
            extracurricular = form.cleaned_data["extracurricular"]
            language_skills = form.cleaned_data["language_skills"]

            profile.research_area = research_area
            profile.education = education
            profile.key_skills = key_skills
            profile.work_experiences = work_experiences
            profile.relevant_coursework = relevant_coursework
            profile.extracurricular = extracurricular
            profile.language_skills = language_skills
            profile.save()

            return redirect("identity")
    else:
        initial = {
            "research_area": profile.research_area,
            "education": profile.education,
            "key_skills": profile.key_skills,
            "work_experiences": profile.work_experiences,
            "relevant_coursework": profile.relevant_coursework,
            "extracurricular": profile.extracurricular,
            "language_skills": profile.language_skills,
        }
        if profile.research_area != "請輸入您的研究領域":
            form = ResumeForm(initial)
        else:
            form = ResumeForm()

    return render(request, "resume.html", {"form": form})


from .models import UserProfile


def signup(request):
    # if request.user.is_authenticated:
    #     return redirect("info")

    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.research_area = request.POST.get("research_area")
            # Set other additional attributes as needed
            user_profile.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect("info")
    context = {"form": form, "app_name": app_name}
    return render(request, "chatapp/signup.html", context)


def signin(request):
    err = None
    if request.user.is_authenticated:
        return redirect("info")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("info")

        else:
            err = "Invalid Credentials"

    context = {"error": err, "app_name": app_name}
    return render(request, "chatapp/signin.html", context)


def signout(request):
    logout(request)
    return redirect("signin")


def ask_openai(message, user=None, first=False):
    if user not in history:
        history[user] = copy.deepcopy(default_history)
    print("User: " + str(user))
    print(history[user])

    # Add message to history

    if not first:
        history[user].append({"role": "user", "content": message})

    print("Message generating...")

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=history[user],
    )

    response_message = response.choices[0].message

    history[user].append(
        {"role": response_message.role, "content": response_message.content}
    )
    print("Message generating complete!")
    print(history[user])
    return response_message.content


def test(request):
    if request.method == "POST":
        message = request.POST.get("prompt")
        response = ask_openai(
            message, user=request.user, first=(request.POST.get("first") == "true")
        )

        # Retrieve or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        conference_history = user_profile.conference_history if not created else []

        if request.POST.get("first") == "true":
            conference_history = []
            message = f"{request.user.username} 進入了面試會議"

        # Update the conference history with the latest interaction
        interaction = {"message": message, "response": response}
        conference_history.append(interaction)

        # Save the updated history back to the user profile
        user_profile.conference_history = conference_history
        user_profile.save()

        return JsonResponse({"response": response})
    else:
        if request.user.is_authenticated:
            history[request.user] = copy.deepcopy(default_history)
            return render(request, "test.html")


def mock_history(request):
    username = request.user.username
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    conference_history = user_profile.conference_history if not created else []
    return render(
        request,
        "history.html",
        {"username": username, "conference_history": conference_history},
    )


def my_view(request):
    bio = request.user.profile.bio
    avatar = request.user.profile.avatar


def avatar(request):
    return render(request, "avatar.html")
