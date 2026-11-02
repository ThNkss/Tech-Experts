from django.contrib import messages
from django.utils.translation import get_language
from apps.company.engineering_copy import ENGINEERING_COPY
from apps.core.templatetags.site_copy import ui
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from apps.products.models import Product, ProductCategory
from apps.projects.models import Project, Industry
from apps.contact.forms import InquiryForm


def public_products():
    return Product.objects.filter(published=True).select_related('cover', 'category')


def public_projects():
    return Project.objects.filter(published=True, publication_authorized=True).select_related('cover', 'industry')


@require_GET
def home(request):
    return render(request, 'home.html')


@require_GET
def product_list(request):
    products = public_products()
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category__slug=category)
    return render(request, 'products/list.html', {'page_obj': Paginator(products, 12).get_page(request.GET.get('page')), 'categories': ProductCategory.objects.all(), 'selected_category': category})


@require_GET
def product_detail(request, slug):
    product = get_object_or_404(public_products(), slug=slug)
    return render(request, 'products/detail.html', {'product': product,
        'features': product.features.filter(published=True).select_related('image'),
        'gallery': product.gallery.select_related('asset'),
        'sections': product.sections.filter(published=True).select_related('image'),
        'faqs': product.faqs.filter(published=True),
        'specifications': product.specifications.all(),
        'projects': public_projects().filter(products=product)})


@require_GET
def project_list(request):
    projects = public_projects()
    product = request.GET.get('product', '')
    industry = request.GET.get('industry', '')
    if product:
        projects = projects.filter(products__slug=product, products__published=True)
    if industry:
        projects = projects.filter(industry__slug=industry)
    return render(request, 'projects/list.html', {'page_obj': Paginator(projects.distinct(), 12).get_page(request.GET.get('page')),
        'products': public_products(), 'industries': Industry.objects.all(), 'selected_product': product, 'selected_industry': industry})


@require_GET
def project_detail(request, slug):
    project = get_object_or_404(public_projects(), slug=slug)
    parties = list(project.parties.filter(published=True))
    primary_roles = ['client', 'contractor', 'consultant', 'end_client']
    extra_roles = ['financier', 'software_developer']
    party_groups = [{'role': role, 'names': [party for party in parties if party.role == role]}
        for role in primary_roles + extra_roles
        if role in primary_roles or any(party.role == role for party in parties)]
    return render(request, 'projects/detail.html', {'project': project,
        'products': project.products.filter(published=True).select_related('cover', 'category'),
        'gallery': project.gallery.select_related('asset'),
        'parties': parties, 'party_groups': party_groups})


@require_GET
def engineering(request):
    language = 'fa' if (get_language() or 'en').startswith('fa') else 'en'
    return render(request, 'engineering.html', {'copy': ENGINEERING_COPY[language]})


@require_GET
def company(request):
    return render(request, 'company.html')


@require_http_methods(['GET', 'POST'])
def contact(request):
    initial = {'kind': 'demo' if request.GET.get('kind') == 'demo' else 'contact'}
    product = public_products().filter(slug=request.GET.get('product', '')).first()
    if product:
        initial['product'] = product
    form = InquiryForm(request.POST if request.method == 'POST' else None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['website']:
            return redirect('contact')
        # Session throttle avoids collecting visitor IP addresses. Use shared cache
        # and edge rate limiting when deploying across multiple processes.
        if not request.session.session_key:
            request.session.create()
        key = f'inquiry:{request.session.session_key}'
        if cache.add(key, True, timeout=60):
            form.save()
            messages.success(request, ui('پیام شما ثبت شد. همکاران ما با شما تماس خواهند گرفت.'))
            return redirect('contact')
        form.add_error(None, ui('لطفاً یک دقیقه تا ارسال پیام بعدی صبر کنید.'))
    return render(request, 'contact.html', {'form': form})
