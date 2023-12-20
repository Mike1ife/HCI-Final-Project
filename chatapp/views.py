from django.shortcuts import render, redirect
from .forms import UserForm, ResumeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, timedelta
from .models import QuestionAnswer, UserProfile
import openai
from dotenv import load_dotenv
import os
import copy
from bs4 import BeautifulSoup
import requests
from .prof import NTU_prof, NYCU_prof, NTHU_prof
import multiprocessing
import sys
load_dotenv()

# Create your views here.
openai.api_key = os.getenv("API_KEY")

app_name = "HCI Project"

default_history = [
    {
        "role": "system",
        "content": """
只使用繁體中文進行提問及回答
你是一個HCI大學的教授 正在面試準備進入研究所的大學生。
以學生的回答，在內心給出一個介於 0~100 的整數x 代表你對這名學生的評分，以 70 作為初始數值，並以 60 做為錄取標準，若學生的分數距離此標準過低，你也可以選擇提前結束這場面試。在任何回覆的最後面印出獨立的一行 "分數: x"。
無論如何 第一句話先請學生自我介紹
以學生的科系、報考動機、進入研究所後的規劃等方面，制定問題以"嚴格的口吻"進行提問
不要講太多無關問題的回答 一次以一個問題為主
參考的問題方向如下 但盡量讓每個問題都問過 且不要問得太深入 
1. 你好 我是HCI大學的教授 可以請你簡單介紹一下你自己嗎?
2. 想請問你為什麼選擇報考我們學校的研究所呢?
3. 可以分享一下你在學的學習經歷和相關的專長嗎?
4. 如果沒有考上你要怎麼辦? 是不是有打算出國念或工作
5. 在研究所二年內，想得到些什麼?
6. 對本所了解多少？你覺得本校的優點在哪？簡述系上老師的特色      
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


def NTU_worker(data):
    profs, link = data
    try:
        name = link.find('a').get('title').split('(')[1][:-1]
    except:
        name = link.find('a').get('title').split('（')[1][:-1]
    url = "https://csie.ntu.edu.tw" + link.find('a').get('href')
    profs[name] = NTU_prof(url)

def NYCU_worker(data):
    profs, member = data
    name = member.find('h2').find('small').get_text(strip=True)
    url = member.get('href')
    profs[name] = NYCU_prof(url)

def NTU_parse():    
    sys.setrecursionlimit(25000)
    url = "https://csie.ntu.edu.tw/zh_tw/member/Faculty"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all('span', class_="i-member-value member-data-value-name")
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()

    with multiprocessing.Pool(len(links)) as pool:
        pool.map(NTU_worker, [(shared_dict, link) for link in links])

    return dict(shared_dict)

def NYCU_parse():
    sys.setrecursionlimit(25000)
    url = "https://www.cs.nycu.edu.tw/members/prof"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    members = soup.find_all('a', class_='card-image')
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()

    with multiprocessing.Pool(len(members)) as pool:
        pool.map(NYCU_worker, [(shared_dict, member) for member in members])
    return dict(shared_dict)

def NTHU_parse():
    prof_dict = {}
    nbrs = ["1107", "461", "429", "1108", "430"]
    for nbr in nbrs:
        url = "https://dcs.site.nthu.edu.tw/app/index.php?Action=mobileloadmod&Type=mobile_rcg_mstr&Nbr=" + nbr
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        profs = soup.find_all("div", class_="meditor")
        for prof in profs:
            prof_info = NTHU_prof(url, prof)
            prof_dict[prof_info.ename_strip] = prof_info
    return prof_dict

schoolDict = {"NTU":NTU_parse, "NYCU":NYCU_parse, "NTHU":NTHU_parse} 

@login_required(login_url="signin")
def info(request):
    school = request.GET.get('s', '') 
    profname = request.GET.get('n', '')
    username = request.user.username    
    # return render(request, "info.html", context)
    if school == '' or school not in schoolDict:
        context = {"username": username, "app_name": app_name}
        return render(request, "info.html", context)
    else:        
        profs = schoolDict[school]() # return a dict of profs    
        prof_list = [prof.to_dict() for prof in profs.values()]
        prof_list.sort(key=lambda x: x['cname'], reverse=True)

        # for p in prof_list:
        #     print(p['research'])
        cschool = ""
        if school == "NTU":
            cschool = "台灣大學"
        elif school == "NYCU":
            cschool = "陽明交通大學"
        else:
            cschool = "清華大學"
        prof_found = any(p.get('ename_strip') == profname for p in prof_list)
        if profname == '' or not prof_found:
            context = {"username": username, "app_name": app_name, "cschool": cschool, 'school': school, 'profs': prof_list}
            return render(request, 'school.html', context)
        else:
            prof_info = None
            for prof in prof_list:
                if prof['ename_strip'] == profname:
                    prof_info = prof
                    break
            context = {"username": username, "app_name": app_name, "school": cschool, 'prof': prof_info}
            return render(request, 'prof.html', context)

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
        "username": username,
        "app_name": app_name,
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
        history[user].append(
            {"role": "user", "content":message}
        )

    print("Message generating...")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=history[user],
    )

    response_message = response.choices[0].message
    
    history[user].append({
        "role": response_message.role,
        "content":response_message.content
    })
    print("Message generating complete!")
    print(history[user])
    return response_message.content


def test(request):

    if request.method == "POST":
        # data = json.loads(request.body)
        # message = data["msg"]   
        message = request.POST.get("prompt")
        response = ask_openai(message, user=request.user, first=(request.POST.get("first") == "true"))
        # QuestionAnswer.objects.create(user=request.user, question=message, answer=response)
        # return JsonResponse({"msg": message, "res": response})
        return JsonResponse({"response": response})
    else:
        if request.user.is_authenticated:
            history[request.user] = copy.deepcopy(default_history)
            return render(request, "test.html")
            # return render(request, "test.html", {'current_time': str(datetime.now()),})
def my_view(request):
 
    bio = request.user.profile.bio
    avatar = request.user.profile.avatar

