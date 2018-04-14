from django.contrib import admin
from .models import basicinfo,basictree,assetsinfo,country,currency,stockinfo,indexinfo,marketinfo,financialinfo,classinfo

admin.site.register(basictree)
admin.site.register(basicinfo)
admin.site.register(assetsinfo)
admin.site.register(country)
admin.site.register(currency)
admin.site.register(stockinfo)
admin.site.register(indexinfo)
admin.site.register(marketinfo)
admin.site.register(financialinfo)
admin.site.register(classinfo)
