
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from .models import Course, Enrollment, Choice, Submission

class CourseListView(ListView):
    model = Course
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

class CourseDetailView(DetailView):
    model = Course
    template_name = "onlinecourse/course_details_bootstrap.html"
    context_object_name = "course"

def registration_request(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("onlinecourse:login")
    else:
        form = UserCreationForm()

    return render(
        request,
        "onlinecourse/registration.html",
        {"form": form}
    )


def login_request(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("onlinecourse:index")

    return render(request, "onlinecourse/login.html")


def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    return redirect(
        "onlinecourse:course_details",
        pk=course.id
    )


def extract_answers(request):
    selected_ids = []

    for key, value in request.POST.items():
        if key.startswith("choice_"):
            selected_ids.append(int(value))

    return selected_ids


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course
    )

    selected_ids = extract_answers(request)

    submission = Submission.objects.create(
        enrollment=enrollment
    )

    choices = Choice.objects.filter(
        question__course=course,
        id__in=selected_ids
    )

    submission.choices.set(choices)

    return HttpResponseRedirect(
        reverse(
            "onlinecourse:exam_result",
            args=(course.id, submission.id)
        )
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    choices = submission.choices.select_related(
        "question"
    ).all()

    grade = sum(
        choice.question.grade
        for choice in choices
        if choice.is_correct
    )

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "submission": submission,
            "grade": grade,
            "choices": choices,
        }
    )
