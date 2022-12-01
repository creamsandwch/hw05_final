from django.core.paginator import Paginator


def paginate(request, obj_list, obj_count):
    paginator = Paginator(obj_list, obj_count)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
