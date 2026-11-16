
from django.shortcuts import render


def home(request):
    context = {
        "platform_name": "VUA ServiceDesk",
        "headline": "Report and track maintenance requests",
        "active_requests": 0,
    }

    return render(request, "core/home.html", context)


def about(request):
    project_roles = [
        "Requester",
        "Coordinator",
        "Technician",
        "Administrator",
    ]

    return render(
        request,
        "core/about.html",
        {"project_roles": project_roles},
    )


def contact(request):
    context = {
        "department_name": "Software Engineering",
        "email": "info@veritas.edu.ng",
        "office_hours": "Monday - Friday, 9am - 4pm",
    }

    return render(request, "core/contact.html", context)


def workflow(request):
    stages = [
        "Request submitted",
        "Request triaged",
        "Technician assigned",
        "Request resolved",
    ]

    return render(
        request,
        "core/workflow.html",
        {"stages": stages},
    )


def custom_404(request, exception):
    return render(request, "404.html", status=404)
