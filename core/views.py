from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, TemplateView

from accounts.mixins import StaffRequiredMixin
from gallery.models import MediaItem

from . import content
from .forms import ContactForm
from .models import ContactMessage


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        featured = list(MediaItem.objects.filter(is_featured=True)[:6])
        if not featured:
            featured = list(MediaItem.objects.all()[:6])
        ctx.update(
            featured=featured,
            services=content.SERVICES,
            steps=content.STEPS,
            pillars=content.PILLARS,
        )
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(values=content.VALUES, pillars=content.PILLARS)
        return ctx


class ServicesView(TemplateView):
    template_name = "core/services.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(services=content.SERVICES, steps=content.STEPS)
        return ctx


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["faqs"] = content.FAQS
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Thank you! Your message is in and we will get back to you soon. ¡Gracias!",
        )
        return super().form_valid(form)


# --------------------------------------------------------------------------
# Staff-only inbox for contact messages
# --------------------------------------------------------------------------
class MessageListView(StaffRequiredMixin, ListView):
    model = ContactMessage
    template_name = "manage/messages.html"
    context_object_name = "contact_messages"
    paginate_by = 15


class MessageToggleReadView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        msg.is_read = not msg.is_read
        msg.save(update_fields=["is_read"])
        return redirect(request.POST.get("next") or "messages_manage")


class MessageDeleteView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        get_object_or_404(ContactMessage, pk=pk).delete()
        messages.success(request, "Message deleted.")
        return redirect("messages_manage")
