from .models import Mailing


def mailing_context(request):
    mailing_id = None
    if request.path.startswith('/mailing/') and 'pk' in request.resolver_match.kwargs:
        mailing_id = request.resolver_match.kwargs['pk']
    return {'current_mailing_id': mailing_id}
