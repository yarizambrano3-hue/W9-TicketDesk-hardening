import csv

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Ticket

@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(
        owner=request.user
    ).order_by("-created")

    return render(request, "tickets/list.html", {"tickets": tickets})


@login_required
def ticket_create(request):
    if request.method == "POST":
        Ticket.objects.create(
            owner=request.user,
            title=request.POST.get("title", ""),
            description=request.POST.get("description", ""),
            severity=request.POST.get("severity", "medium"),
        )
        return redirect("ticket_list")

    return render(request, "tickets/new.html")


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(
        Ticket,
        pk=pk,
        owner=request.user
    )

    return render(request, "tickets/detail.html", {"ticket": ticket})


@login_required
@require_POST
def ticket_delete(request, pk):
    ticket = get_object_or_404(
        Ticket,
        pk=pk,
        owner=request.user
    )
    ticket.delete()

    return redirect("ticket_list")


@login_required
def search(request):
    q = request.GET.get("q", "")

    results = Ticket.objects.filter(
        owner=request.user,
        title__icontains=q
    ) if q else []

    return render(
        request,
        "tickets/search.html",
        {"q": q, "results": results}
    )


@staff_member_required
def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tickets.csv"'

    writer = csv.writer(response)
    writer.writerow(["id", "owner", "title", "severity", "description"])

    tickets = Ticket.objects.filter(
        owner=request.user
    ).select_related("owner")

    for ticket in tickets:
        writer.writerow([
            ticket.pk,
            ticket.owner.username,
            ticket.title,
            ticket.severity,
            ticket.description
        ])

    return response
