from .models import CompanyProfile

def company_context(request):
    return {"company": CompanyProfile.objects.first()}
