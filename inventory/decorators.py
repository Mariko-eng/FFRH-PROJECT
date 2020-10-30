from django.shortcuts import redirect
from django.http import HttpResponse


def already_signed_in(view_func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request,*args,**kwargs)
    return wrapper_func


def main_admin_authorized(status = None):
    def call_view_func(view_func2):
        def wrapper_func(request,*args,**kwargs):
            group = request.user.groups.all()
            names = []
            for gp in group:
                names.append(str(gp.name))

            if status in names:
                return view_func2(request,*args,**kwargs)
            else:
                return HttpResponse("<h1>You are not authorized to access this page!</h1>")
        return wrapper_func
    return call_view_func


# def sub_admin_authorized(status = None):
#     def call_view_func(view_func2):
#         def wrapper_func(request):
#             group = request.user.groups.all()
#             names = []
#             for gp in group:
#                 names.append(str(gp.name))
#
#             if status in names:
#                 return view_func2(request)
#             else:
#                 return HttpResponse("<h1>You are not authorized to access this page!</h1>")
#         return wrapper_func
#     return call_view_func
