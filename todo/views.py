from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

from todo.models import Task


# Create your views here.
def index(request):
    if request.method == "POST":
        task = Task(
            title=request.POST["title"],
            due_at=make_aware(parse_datetime(request.POST["due_at"])),
        )
        task.save()

    tasks = Task.objects.all()
    query = request.GET.get("q")

    if request.GET.get("order") == "due":
        tasks = Task.objects.order_by("due_at")
    elif query:
        tasks = Task.objects.filter(title__icontains=query).order_by("-posted_at")
    else:
        tasks = Task.objects.order_by("-posted_at")

    context = {
        "tasks": tasks,
        "query": query or "",
    }
    return render(request, "todo/index.html", context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task.view_count += 1
    task.save()

    context = {
        "task": task,
    }
    return render(request, "todo/detail.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == "POST":
        task.title = request.POST["title"]
        task.due_at = make_aware(parse_datetime(request.POST["due_at"]))
        task.save()
        return redirect(detail, task_id)

    context = {"task": task}
    return render(request, "todo/edit.html", context)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)
