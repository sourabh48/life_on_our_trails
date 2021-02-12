from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Post, Team
from .forms import CommentForm
from django.db.models import Count, Q


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    paginator = Paginator(queryset, 8)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset,
        'paginated_queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render(request, 'search_results.html', context)


def get_category_count():
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset


def index(request):
    latest = Post.objects.order_by('-timestamp')[0:3]
    featured = Post.objects.filter(featured=True)[0:5]
    main = Team.objects.filter(main=True)[0:2]
    context = {
        'mainteam' : main,
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'index.html', context)


def allblogs(request):
    category_count = get_category_count()
    post_list = Post.objects.all()
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    paginator = Paginator(post_list, 8)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render(request, 'allblogs.html', context)


def singleblog(request, id):
    category_count = get_category_count()
    post = get_object_or_404(Post, id=id)

    comments = post.comments.filter(active=True)
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            return redirect(reverse("post-detail", kwargs={
                'id': post.pk
            }))
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'category_count': category_count
    }
    return render(request, 'singleblog.html', context)


def videos(request):
    gaming = Post.objects.filter(gaming=True)[0:3]
    context = {
        'object_list': gaming
    }
    return render(request, 'videos.html', context)

def music(request):
    return render(request, 'music.html', {})


def ourteam(request):
    team_list = Team.objects.all()
    context = {
        'team_list': team_list,
    }
    return render(request, 'ourteam.html', context)


def resume(request, id):
    member = get_object_or_404(Team, id=id)
    skill = member.skill.order_by('-skillpercentage')
    experience = member.experience.all()
    education = member.education.all()

    context = {
        'member': member,
        'skill': skill,
        'experience': experience,
        'education': education
    }
    return render(request, 'resume.html', context)
