# posts/views.py

import os
import uuid
import math
import json
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import openai

from .forms import CommentForm, PostCreateForm
from .models import Post, Profile, Comment, Category, Tag

# ============================================================
# OPENAI CONFIG (uses .env -> settings.OPENAI_API_KEY)
# ============================================================

openai.api_key = os.getenv("OPENAI_API_KEY") or getattr(
    settings, "OPENAI_API_KEY", None
)


# ============================================================
# PERMISSION HELPERS
# ============================================================

def is_admin(user):
    return user.is_authenticated and user.is_staff


def user_owns_post(user, post):
    return user.is_authenticated and post.author == user


def post_permission_required(view_func):
    """
    Ensures the user can modify the specified post.
    URL must pass <post_id>.
    Injects `post` into the view: def view(request, post, ...)
    """

    @wraps(view_func)
    def _wrapped_view(request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)

        if not (user_owns_post(request.user, post) or is_admin(request.user)):
            messages.error(request, "You are not allowed to perform this action!")
            return redirect("singleblog", id=post_id)

        return view_func(request, post, *args, **kwargs)

    return _wrapped_view


# ============================================================
# UTILS
# ============================================================

def paginate_queryset(request, queryset, per_page=8):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get("page")

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def calculate_reading_time_from_html(html_content: str) -> int:
    """Estimate reading time from HTML content."""
    text = strip_tags(html_content or "").strip()
    words = len([w for w in text.split() if w])
    return max(1, math.ceil(words / 200)) if words else 1


def generate_unique_slug(base_title: str) -> str:
    """Generate a unique slug from a title."""
    from django.utils.text import slugify

    base_slug = slugify(base_title) or "post"
    slug = base_slug
    idx = 1
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{idx}"
        idx += 1
    return slug


def ensure_tags_from_payload(existing_ids_str: str, new_tags_str: str):
    """
    Build a list of Tag instances from:
      - CSV of existing tag IDs (hidden: name="tags")
      - CSV of new tag names (hidden: name="new_tags")
    Used with your Medium-style tag manager.
    """
    tags = []

    # Existing tag IDs
    if existing_ids_str:
        try:
            ids = [int(pk) for pk in existing_ids_str.split(",") if pk.strip()]
            tags.extend(list(Tag.objects.filter(id__in=ids)))
        except ValueError:
            # If parsing fails, just ignore bad IDs
            pass

    # New tag names
    from django.utils.text import slugify

    if new_tags_str:
        for raw in new_tags_str.split(","):
            name = raw.strip()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)[:100]},
            )
            tags.append(tag)

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for t in tags:
        if t.id not in seen:
            seen.add(t.id)
            unique.append(t)
    return unique


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return None


# ============================================================
# USER PROFILE / EDIT / PASSWORD / DASHBOARD
# ============================================================

@login_required
@never_cache
def profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile_obj, _ = Profile.objects.get_or_create(user=user_obj)

    posts = Post.objects.filter(author=user_obj).order_by("-created_at")
    comments = Comment.objects.filter(user=user_obj).order_by("-created_on")

    return render(
        request,
        "profile.html",
        {
            "user_obj": user_obj,
            "profile": profile_obj,
            "posts": posts,
            "comments": comments,
        },
    )


@login_required
@never_cache
def edit_profile(request, username):
    if request.user.username != username:
        messages.error(request, "You cannot edit another user's profile.")
        return redirect("profile", username=request.user.username)

    user = request.user
    profile_obj, _ = Profile.objects.get_or_create(user=user)

    # Import here to avoid circulars
    from .forms import (
        ProfileForm,
        EducationFormSet,
        ExperienceFormSet,
        SkillFormSet,
    )

    if request.method == "POST":
        # Core user fields
        user.username = request.POST.get("username") or user.username
        user.email = request.POST.get("email") or user.email
        user.save()

        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        edu_formset = EducationFormSet(
            request.POST, instance=profile_obj, prefix="education"
        )
        exp_formset = ExperienceFormSet(
            request.POST, instance=profile_obj, prefix="experience"
        )
        skill_formset = SkillFormSet(
            request.POST, instance=profile_obj, prefix="skill"
        )

        if (
                form.is_valid()
                and edu_formset.is_valid()
                and exp_formset.is_valid()
                and skill_formset.is_valid()
        ):
            form.save()
            edu_formset.save()
            exp_formset.save()
            skill_formset.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("edit_profile", username=user.username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile_obj)
        edu_formset = EducationFormSet(instance=profile_obj, prefix="education")
        exp_formset = ExperienceFormSet(instance=profile_obj, prefix="experience")
        skill_formset = SkillFormSet(instance=profile_obj, prefix="skill")

    return render(
        request,
        "edit_profile.html",
        {
            "user": user,
            "profile": profile_obj,
            "form": form,
            "edu_formset": edu_formset,
            "exp_formset": exp_formset,
            "skill_formset": skill_formset,
        },
    )


@login_required
@never_cache
def change_password(request, username):
    if request.user.username != username:
        messages.error(request, "Unauthorized access.")
        return redirect("profile", username=request.user.username)

    if request.method == "POST":
        old_pass = request.POST.get("old_password")
        new_pass = request.POST.get("new_password")
        confirm_pass = request.POST.get("confirm_password")

        if not request.user.check_password(old_pass):
            messages.error(request, "Old password is incorrect.")
            return redirect("change_password", username=username)

        if new_pass != confirm_pass:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password", username=username)

        request.user.set_password(new_pass)
        request.user.save()
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password updated successfully.")
        return redirect("profile", username=username)

    return render(request, "change_password.html")


@login_required
@never_cache
def dashboard(request):
    user = request.user
    profile_obj, _ = Profile.objects.get_or_create(user=user)

    posts = Post.objects.filter(author=user).order_by("-created_at")
    comments = Comment.objects.filter(user=user).order_by("-created_on")

    return render(
        request,
        "dashboard.html",
        {
            "user": user,
            "profile": profile_obj,
            "posts": posts,
            "comments": comments,
        },
    )


# ============================================================
# AUTH: SIGNUP / LOGIN / LOGOUT
# ============================================================

@never_cache
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("signup")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "auth.html")


@never_cache
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("index")

        messages.error(request, "Invalid username or password!")
        return redirect("login")

    return render(request, "auth.html")


@never_cache
def custom_logout(request):
    # Full session wipe
    request.session.flush()
    auth_logout(request)

    response = redirect("login")
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    messages.success(request, "You have been logged out successfully.")
    return response


# ============================================================
#  INDEX PAGE (Homepage)
# ============================================================

@never_cache
def index(request):
    featured = Post.objects.filter(status="published").order_by("-created_at")[:4]
    latest = Post.objects.filter(status="published").order_by("-created_at")[:8]

    # Use your team profiles on homepage
    main_team = Profile.objects.filter(show_in_team=True)[:4]

    return render(
        request,
        "index.html",
        {
            "mainteam": main_team,
            "object_list": featured,
            "latest": latest,
        },
    )


# ============================================================
# BLOG LIST
# ============================================================

@never_cache
def allblogs(request):
    post_list = Post.objects.filter(status="published").order_by("-created_at")

    # CATEGORY FILTER
    active_category = request.GET.get("category")
    cleaned_category = active_category.strip().lower() if active_category else None

    if cleaned_category and cleaned_category != "all":
        post_list = post_list.filter(category__name__iexact=cleaned_category)

    paginated_queryset = paginate_queryset(request, post_list, per_page=8)

    # AJAX INFINITE SCROLL HANDLER
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "components/blog_cards.html", {"queryset": paginated_queryset}, request=request
        )
        return JsonResponse(
            {
                "html": html,
                "has_next": paginated_queryset.has_next(),
            }
        )

    if cleaned_category and cleaned_category != "all":
        breadcrumb_title = f"Category: {cleaned_category.title()}"
    else:
        breadcrumb_title = "All Stories"

    return render(
        request,
        "allblogs.html",
        {
            "queryset": paginated_queryset,
            "categories": Category.objects.all(),
            "active_category": cleaned_category,
            "breadcrumb_title": breadcrumb_title,
            "page_request_var": "page",
        },
    )


# ============================================================
# SINGLE BLOG + COMMENTS
# ============================================================

@never_cache
def singleblog(request, id):
    post = get_object_or_404(Post, id=id)
    comments = post.comments.filter(active=True)

    # Previous Post (newer)
    previous_post = (
        Post.objects.filter(status="published", created_at__gt=post.created_at)
        .order_by("created_at")
        .first()
    )

    # Next Post (older)
    next_post = (
        Post.objects.filter(status="published", created_at__lt=post.created_at)
        .order_by("-created_at")
        .first()
    )

    new_comment = None

    if request.method == "POST":
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post

            if request.user.is_authenticated:
                new_comment.user = request.user

            new_comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect(reverse("singleblog", kwargs={"id": post.id}))
    else:
        form = CommentForm()

    breadcrumb_title = post.title
    breadcrumb_category = (
        post.category.name if hasattr(post, "category") and post.category else None
    )

    return render(
        request,
        "singleblog.html",
        {
            "post": post,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": form,
            "previous_post": previous_post,
            "next_post": next_post,
            "breadcrumb_title": breadcrumb_title,
            "breadcrumb_category": breadcrumb_category,
        },
    )


# ============================================================
# SEARCH
# ============================================================

@never_cache
def search(request):
    query = request.GET.get("q", "").strip()

    if query:
        queryset = Post.objects.filter(status="published").filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()
    else:
        queryset = Post.objects.none()

    paginated_queryset = paginate_queryset(request, queryset, per_page=8)

    breadcrumb_title = (
        f"Search Results for: '{query}'" if query else "Search Results"
    )

    return render(
        request,
        "search_results.html",
        {
            "queryset": paginated_queryset,
            "query": query,
            "breadcrumb_title": breadcrumb_title,
            "page_request_var": "page",
        },
    )


# ============================================================
# AI ENDPOINTS (WRITE / IMPROVE / FIX)
# ============================================================

@login_required
@require_POST
def ai_write(request):
    """
    Draft from title: expects JSON { "prompt": "..." }
    Returns: { "result": "<p>...</p>" }
    """
    data = _json_body(request)
    if data is None:
        return HttpResponseBadRequest("Invalid JSON")

    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return JsonResponse({"error": "No prompt provided."}, status=400)

    full_prompt = (
        "Write a detailed, engaging blog article section in HTML. "
        "Use <p>, <h2>, <h3>, and <ul>/<li> where helpful. "
        "Do NOT include <html> or <body> tags.\n\n"
        f"Title: {prompt}"
    )

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}],
    )
    text = completion["choices"][0]["message"]["content"]

    return JsonResponse({"result": text})


@login_required
@require_POST
def ai_improve(request):
    """
    Improve writing: expects JSON { "content": "<html...>" }
    """
    data = _json_body(request)
    if data is None:
        return HttpResponseBadRequest("Invalid JSON")

    content = (data.get("content") or "").strip()
    if not content:
        return JsonResponse({"error": "No content provided."}, status=400)

    prompt = (
        "Improve the following blog post HTML for clarity, structure, and tone. "
        "Keep the same structure and return HTML only (no <html> or <body> tags):\n\n"
        f"{content}"
    )

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    text = completion["choices"][0]["message"]["content"]

    return JsonResponse({"result": text})


@login_required
@require_POST
def ai_fix(request):
    """
    Fix grammar: expects JSON { "content": "<html...>" }
    """
    data = _json_body(request)
    if data is None:
        return HttpResponseBadRequest("Invalid JSON")

    content = (data.get("content") or "").strip()
    if not content:
        return JsonResponse({"error": "No content provided."}, status=400)

    prompt = (
        "Fix grammar, punctuation, and typos in the following blog HTML. "
        "Do NOT change meaning. Return HTML only (no <html> or <body> tags):\n\n"
        f"{content}"
    )

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    text = completion["choices"][0]["message"]["content"]

    return JsonResponse({"result": text})


# ============================================================
# TAG SUGGEST API (for tag autocomplete)
# ============================================================

def tag_suggest(request):
    """
    GET /tags/suggest/?q=travel
    Returns: { "results": [{ "id": 1, "name": "Travel" }, ...] }
    """
    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"results": []})

    tags = Tag.objects.filter(name__icontains=q).order_by("name")[:15]
    data = [{"id": t.id, "name": t.name} for t in tags]
    return JsonResponse({"results": data})


# ============================================================
# POST CRUD - CREATE / EDIT / DELETE
# ============================================================

@login_required
@never_cache
def create_post(request):
    """
    Create a new blog post.

    Frontend:
      - Quill editor writes HTML into hidden #content-input
      - Tag manager writes CSV of IDs into name="tags"
      - New tags CSV into name="new_tags"

    Backend rules are enforced by PostCreateForm.clean().
    """
    if request.method == "POST":
        form = PostCreateForm(request.POST, request.FILES)

        if form.is_valid():
            cleaned = form.cleaned_data

            title = (cleaned.get("title") or "").strip()
            content_html = cleaned.get("content") or ""
            meta_title = (cleaned.get("meta_title") or "").strip()
            meta_description = (cleaned.get("meta_description") or "").strip()
            status = (cleaned.get("status") or "draft").strip()

            category_obj = cleaned.get("category")
            new_category_name = (cleaned.get("new_category") or "").strip()

            # Category: existing or create new
            if not category_obj and new_category_name:
                from django.utils.text import slugify

                category_obj, _ = Category.objects.get_or_create(
                    name=new_category_name,
                    defaults={"slug": slugify(new_category_name)},
                )

            # Build post instance
            post = Post(
                title=title,
                content=content_html,
                image=cleaned.get("image"),
                status=status,
                publish_at=cleaned.get("publish_at"),
                author=request.user,
                category=category_obj,
            )

            # Reading time
            post.read_time = calculate_reading_time_from_html(content_html)

            # Auto slug
            post.slug = generate_unique_slug(title)

            # SEO defaults
            if not meta_title:
                post.meta_title = (title or "")[:70]
            else:
                post.meta_title = meta_title

            if not meta_description:
                plain = strip_tags(content_html or "").strip()
                post.meta_description = plain[:175]
            else:
                post.meta_description = meta_description

            post.save()

            # Tags from hidden fields (CSV)
            existing_tag_ids_str = (cleaned.get("tags") or "").strip()
            new_tags_str = (cleaned.get("new_tags") or "").strip()

            tag_objects = ensure_tags_from_payload(
                existing_tag_ids_str, new_tags_str
            )
            if tag_objects:
                post.tags.set(tag_objects)
            else:
                post.tags.clear()

            messages.success(request, "Post created successfully!")
            return redirect("singleblog", id=post.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PostCreateForm()

    categories = Category.objects.all().order_by("name")
    all_tags = Tag.objects.all().order_by("name")

    return render(
        request,
        "create_post.html",
        {
            "form": form,
            "categories": categories,
            "all_tags": all_tags,
        },
    )


@login_required
@never_cache
@post_permission_required
def edit_post(request, post):
    """
    Edit an existing post. Uses the same PostCreateForm + rules.
    """
    if request.method == "POST":
        form = PostCreateForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            cleaned = form.cleaned_data

            title = (cleaned.get("title") or "").strip()
            content_html = cleaned.get("content") or ""
            meta_title = (cleaned.get("meta_title") or "").strip()
            meta_description = (cleaned.get("meta_description") or "").strip()
            status = (cleaned.get("status") or "draft").strip()

            category_obj = cleaned.get("category")
            new_category_name = (cleaned.get("new_category") or "").strip()

            if not category_obj and new_category_name:
                from django.utils.text import slugify

                category_obj, _ = Category.objects.get_or_create(
                    name=new_category_name,
                    defaults={"slug": slugify(new_category_name)},
                )

            post.title = title
            post.content = content_html
            post.image = cleaned.get("image") or post.image
            post.status = status
            post.publish_at = cleaned.get("publish_at")
            post.category = category_obj

            # Reading time
            post.read_time = calculate_reading_time_from_html(content_html)

            # Slug stays same unless missing
            if not post.slug:
                post.slug = generate_unique_slug(title)

            # SEO defaults
            if not meta_title:
                post.meta_title = (title or "")[:70]
            else:
                post.meta_title = meta_title

            if not meta_description:
                plain = strip_tags(content_html or "").strip()
                post.meta_description = plain[:175]
            else:
                post.meta_description = meta_description

            post.save()

            # Tags
            existing_tag_ids_str = (cleaned.get("tags") or "").strip()
            new_tags_str = (cleaned.get("new_tags") or "").strip()
            tag_objects = ensure_tags_from_payload(
                existing_tag_ids_str, new_tags_str
            )
            if tag_objects:
                post.tags.set(tag_objects)
            else:
                post.tags.clear()

            messages.success(request, "Post updated successfully!")
            return redirect("singleblog", id=post.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # Pre-fill tags CSV for JS (IDs of current tags)
        existing_ids_str = ",".join(str(t.id) for t in post.tags.all())
        initial = {"tags": existing_ids_str}
        form = PostCreateForm(instance=post, initial=initial)

    categories = Category.objects.all().order_by("name")
    all_tags = Tag.objects.all().order_by("name")

    return render(
        request,
        "create_post.html",  # reuse same template for edit
        {
            "form": form,
            "categories": categories,
            "all_tags": all_tags,
            "editing": True,
            "post_obj": post,
        },
    )


@login_required
@never_cache
@post_permission_required
def delete_post(request, post):
    post_id = post.id
    post.delete()
    messages.success(request, "Post deleted successfully!")
    return redirect("allblogs")


# ============================================================
# STATIC PAGES
# ============================================================

@never_cache
def videos(request):
    return render(request, "business_list.html")


@never_cache
def ourteam(request):
    team_list = Profile.objects.filter(show_in_team=True)
    return render(request, "ourteam.html", {"team_list": team_list})


@never_cache
def resume(request, id):
    member = get_object_or_404(Profile, id=id)

    skills = member.skills.all().order_by("-skillpercentage")
    experience = member.experiences.all()
    education = member.educations.all()

    return render(
        request,
        "resume.html",
        {
            "member": member,
            "skill": skills,
            "experience": experience,
            "education": education,
        },
    )


# ============================================================
# QUILL IMAGE UPLOAD ENDPOINT
# ============================================================

@csrf_exempt
def editor_image_upload(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # unique filename
        ext = image.name.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        file_path = os.path.join("posts/uploads/", filename)
        saved_path = default_storage.save(file_path, image)

        return JsonResponse(
            {
                "success": 1,
                "url": settings.MEDIA_URL + saved_path,
            }
        )

    return JsonResponse({"success": 0, "error": "No image uploaded"})
