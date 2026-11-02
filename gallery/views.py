from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, ListView, TemplateView, UpdateView

from accounts.mixins import StaffRequiredMixin
from core.models import ContactMessage

from .forms import MediaItemForm, MediaUploadForm
from .models import MediaItem


# --------------------------------------------------------------------------
# Public gallery
# --------------------------------------------------------------------------
class GalleryView(ListView):
    model = MediaItem
    template_name = "gallery/gallery.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        qs = MediaItem.objects.all()
        category = self.request.GET.get("category", "")
        media_type = self.request.GET.get("type", "")
        if category in MediaItem.Category.values:
            qs = qs.filter(category=category)
        if media_type in MediaItem.MediaType.values:
            qs = qs.filter(media_type=media_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx.update(
            categories=MediaItem.Category.choices,
            current_category=self.request.GET.get("category", ""),
            current_type=self.request.GET.get("type", ""),
            qs=params.urlencode(),
        )
        return ctx


# --------------------------------------------------------------------------
# Staff dashboard (login + is_staff required)
# --------------------------------------------------------------------------
class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "manage/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = MediaItem.objects
        ctx.update(
            total=items.count(),
            image_count=items.filter(media_type=MediaItem.MediaType.IMAGE).count(),
            video_count=items.filter(media_type=MediaItem.MediaType.VIDEO).count(),
            featured_count=items.filter(is_featured=True).count(),
            unread_count=ContactMessage.objects.filter(is_read=False).count(),
            recent=items.select_related("uploaded_by")[:6],
        )
        return ctx


class MediaManageListView(StaffRequiredMixin, ListView):
    model = MediaItem
    template_name = "manage/media_list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        qs = MediaItem.objects.select_related("uploaded_by")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if category in MediaItem.Category.values:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx.update(
            categories=MediaItem.Category.choices,
            q=self.request.GET.get("q", ""),
            current_category=self.request.GET.get("category", ""),
            qs=params.urlencode(),
        )
        return ctx


class MediaUploadView(StaffRequiredMixin, FormView):
    template_name = "manage/media_form.html"
    form_class = MediaUploadForm
    success_url = reverse_lazy("media_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Upload photos & videos"
        ctx["multi"] = True
        return ctx

    def form_valid(self, form):
        data = form.cleaned_data
        files = data["files"]
        base_title = data["title"].strip()
        for index, f in enumerate(files, start=1):
            if base_title:
                title = f"{base_title} ({index})" if len(files) > 1 else base_title
            else:
                title = MediaUploadForm.title_from_filename(f.name)
            MediaItem.objects.create(
                title=title,
                description=data["description"],
                category=data["category"],
                file=f,
                is_featured=data["is_featured"],
                uploaded_by=self.request.user,
            )
        count = len(files)
        messages.success(self.request, f"{count} file{'s' if count != 1 else ''} uploaded successfully.")
        return super().form_valid(form)


class MediaUpdateView(StaffRequiredMixin, UpdateView):
    model = MediaItem
    form_class = MediaItemForm
    template_name = "manage/media_form.html"
    success_url = reverse_lazy("media_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Edit item"
        ctx["multi"] = False
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Changes saved.")
        return super().form_valid(form)


class MediaDeleteView(StaffRequiredMixin, DeleteView):
    model = MediaItem
    template_name = "manage/media_confirm_delete.html"
    success_url = reverse_lazy("media_list")

    def form_valid(self, form):
        messages.success(self.request, "Item deleted.")
        return super().form_valid(form)
