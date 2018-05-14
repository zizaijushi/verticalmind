# from django.db import models
# from django.urls import reverse
#
# #    业务逻辑控制表    basicinfo   basictree    assetsinfo
#
# class basicinfo(models.Model):
#     TRADE_CODE = models.CharField(max_length=20, primary_key=True, verbose_name='标的代码', help_text='标的代码')
#     ASSETS = models.ForeignKey('assetsinfo', on_delete=models.SET_NULL, null=True, verbose_name='标的所属资产代码', help_text='标的所属资产代码')
#     COUNTRY = models.ForeignKey('country', on_delete=models.SET_NULL, null=True, verbose_name='标的所属国家', help_text='标的所属国家')
#
#     class Meta:
#         ordering = ['COUNTRY','ASSETS','TRADE_CODE']
#         indexes = [
#             models.Index(fields=['TRADE_CODE']),
#         ]
#         verbose_name = '标的表'
#
#     def __str__(self):
#         return self.TRADE_CODE
#
#     def get_absolute_url(selfs):
#         return reverse('object',args=[str(selfs.TRADE_CODE)])
#
# class basictree(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo', on_delete=models.CASCADE, related_name='parent', verbose_name='父节点', help_text='父节点')
#     CHILD_CODE = models.ForeignKey('basicinfo', on_delete=models.CASCADE, related_name='child', verbose_name='子节点', help_text='子节点')
#     DT = models.DateField(verbose_name='关联日期', help_text='关联日期')
#     DEPTH = models.IntegerField(verbose_name='子节点所在层级', help_text='子节子节点')
#
#     class Meta:
#         ordering = ['TRADE_CODE','CHILD_CODE','DT']
#         unique_together = ('TRADE_CODE','CHILD_CODE','DT')
#         indexes = [
#             models.Index(fields=['TRADE_CODE'],name='basictree_tc'),
#             models.Index(fields=['CHILD_CODE'], name='basictree_cc'),
#             models.Index(fields=['DT'],name='basictree_dt'),
#             models.Index(fields=['CHILD_CODE', 'DT'],name='basictree_ccdt'),
#             models.Index(fields=['TRADE_CODE', 'DT']),
#         ]
#         verbose_name = '关系表'
#
#     def __str__(self):
#         return "Node %s has a child %s in No.%s level(%s)" % (self.TRADE_CODE,self.CHILD_CODE,self.DEPTH,self.DT)
#
# #   资产基本信息表 stockinfo   indexinfo   fundinfo    bondinfo    futureinfo  curnyinfo   classinfo
#
# class stockinfo(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo',on_delete=models.CASCADE, verbose_name='股票代码', help_text='股票代码')
#     DT = models.DateField(help_text="更新日期", verbose_name='更新日期')
#     SEC_NAME = models.CharField(max_length=100, verbose_name='个股名称', help_text='个股名称')
#     IPO_DATE = models.DateField(verbose_name='IPO时间', help_text='IPO时间')
#     COUNTRY = models.ForeignKey('country', on_delete=models.SET_NULL, null=True, verbose_name='国家', help_text='国家')
#     PROVINCE = models.CharField(max_length=50, verbose_name='省份', help_text='省份')
#     CITY = models.CharField(max_length=50, verbose_name='城市', help_text='城市')
#     CURRENCY = models.ForeignKey('currency',on_delete=models.SET_NULL, verbose_name='货币', help_text='货币', null=True)
#     PHONE = models.CharField(max_length=50, verbose_name='电话', help_text='更新日期')
#     OFFICE = models.TextField(verbose_name='办公室', help_text='办公室')
#     NATURE = models.CharField(max_length=255, verbose_name='公司性质', help_text='公司性质')
#     BRIEFING = models.TextField(verbose_name='简介', help_text='简介')
#     BUSINESS = models.TextField(verbose_name='商业模式', help_text='商业模式')
#     MAJORPRODUCT = models.TextField(verbose_name='主营项目', help_text='主营项目')
#
#     class Meta:
#         unique_together = ('TRADE_CODE','DT')
#         indexes = [
#             models.Index(fields=['TRADE_CODE'],name='stockinfo_tc'),
#             models.Index(fields=['DT'],name='stockinfo_dt'),
#             models.Index(fields=['TRADE_CODE','DT']),
#         ]
#         verbose_name = '股票信息表'
#
#     def __str__(self):
#         return '%s(%s)' % (self.SEC_NAME,self.DT)
#
# class indexinfo(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo',on_delete=models.CASCADE, verbose_name='指数代码', help_text='指数代码')
#     DT = models.DateField(help_text="更新日期", verbose_name='更新日期')
#     SEC_NAME = models.CharField(max_length=100, verbose_name='指数名称', help_text='指数名称')
#
#     class Meta:
#         unique_together = ('TRADE_CODE','DT')
#         indexes = [
#             models.Index(fields=['TRADE_CODE'],name='stockinfo_tc'),
#             models.Index(fields=['DT'],name='stockinfo_dt'),
#             models.Index(fields=['TRADE_CODE','DT']),
#         ]
#         verbose_name = '指数信息表'
#
#     def __str__(self):
#         return '%s(%s)' % (self.SEC_NAME,self.DT)
#
# class classinfo(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo',on_delete=models.CASCADE, verbose_name='类别代码', help_text='类别代码')
#     DT = models.DateField(help_text="更新日期", verbose_name='更新日期')
#     SEC_NAME = models.CharField(max_length=100, verbose_name='类别名称', help_text='类别名称')
#
#     class Meta:
#         verbose_name = '类别信息表'
#
#     def __str__(self):
#         return '%s(%s)' % (self.TRADE_CODE,self.DT)
#
#
#
# #   市场基本数据表 marketinfo  financialinfo   fundnavinfo futureinfo
#
# class marketinfo(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo', on_delete=models.CASCADE, verbose_name='市场数据代码', help_text='市场数据代码')
#     # SEC_NAME = models.CharField(max_length=100, verbose_name='市场数据名称', help_text='市场数据名称')
#     DT = models.DateField(verbose_name='日期', help_text='日期')
#     OPEN = models.DecimalField(max_digits=10,decimal_places=4, verbose_name='开盘价', help_text='开盘价')
#     HIGH = models.DecimalField(max_digits=10,decimal_places=4, verbose_name='最高价', help_text='最高价')
#     LOW = models.DecimalField(max_digits=10,decimal_places=4, verbose_name='最低价', help_text='最低价')
#     CLOSE = models.DecimalField(max_digits=10,decimal_places=4, verbose_name='收盘价', help_text='收盘价')
#     AVGPRICE = models.DecimalField(max_digits=10,decimal_places=4, verbose_name='平均价', help_text='平均价')
#     FACTOR = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='复权因子', help_text='复权因子')
#     VOLUME = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='成交量', help_text='成交量')
#     AMT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='成交额', help_text='成交额')
#     MKT_CAP_ARD = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='总市值', help_text='总市值（对应WIND总市值2）')
#     MKT_FREESHARES = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='流通市值', help_text='流通市值')
#
#     class Meta:
#         unique_together = ('TRADE_CODE','DT')
#         indexes = [
#             models.Index(fields=['TRADE_CODE'],name='marketinfo_tc'),
#             models.Index(fields=['DT'],name='marketinfo_dt'),
#             models.Index(fields=['TRADE_CODE','DT']),
#         ]
#         verbose_name = '市场基础数据表'
#
#     def __str__(self):
#         return '%s(%s)' % (self.TRADE_CODE,self.DT)
#
# class financialinfo(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo', on_delete=models.CASCADE, verbose_name='代码', help_text='代码')
#     REPORTDATE = models.DateField(verbose_name='报告期', help_text='报告期')
#     ISSUINGDATE = models.DateField(verbose_name='财报披露日期', help_text='财报披露日期')
#     # SEC_NAME = models.CharField(max_length=100, verbose_name='名称', help_text='名称', null=True)
#     MONETARY_CAP = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='货币资产', help_text='货币资产', null=True)
#     TRADABLE_FIN_ASSETS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='交易性金融资产', help_text='交易性金融资产', null=True)
#     NOTES_RCV = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='应收票据', help_text='应收票据', null=True)
#     ACCT_RCV = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='应收账款', help_text='应收账款', null=True)
#     OTH_RCV = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='其它应收款', help_text='其它应收款', null=True)
#     PREPAY = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='预付账款', help_text='预付账款', null=True)
#     INVENTORIES = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='存货', help_text='存货', null=True)
#     OTH_CUR_ASSETS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='其他流动资产', help_text='其他流动资产', null=True)
#     TOT_CUR_ASSETS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='流动资产合计', help_text='流动资产合计', null=True)
#     FIX_ASSETS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='固定资产', help_text='固定资产', null=True)
#     INTANG_ASSETS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='无形资产', help_text='无形资产', null=True)
#     CONST_IN_PROG = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='在建工程', help_text='在建工程', null=True)
#     GOODWILL = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='商誉', help_text='商誉', null=True)
#     TOT_ASSETS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='资产总计', help_text='资产总计', null=True)
#     ADV_FROM_CUST = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='预收账款', help_text='预收账款', null=True)
#     NOTES_PAYABLE = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='应付票据', help_text='应付票据', null=True)
#     ACCT_PAYABLE = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='应付账款', help_text='应付账款', null=True)
#     INTERESTDEBT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='带息债务', help_text='带息债务', null=True)
#     TOT_CUR_LIAB = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='流动负债合计', help_text='流动负债合计', null=True)
#     TOT_LIAB = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='负债合计', help_text='负债合计', null=True)
#     UNDISTRIBUTED_PROFIT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='未分配利润', help_text='未分配利润', null=True)
#     EQY_BELONGTO_PARCOMSH = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='归属母公司股东的权益', help_text='归属母公司股东的权益', null=True)
#     OPER_REV = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='营业收入', help_text='营业收入', null=True)
#     OPER_COST = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='营业成本', help_text='营业成本', null=True)
#     SELLING_DIST_EXP = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='销售费用', help_text='销售费用', null=True)
#     GERL_ADMIN_EXP = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='管理费用', help_text='管理费用', null=True)
#     FIN_EXP_IS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='财务费用', help_text='财务费用', null=True)
#     OPPROFIT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='营业利润', help_text='营业利润', null=True)
#     NET_PROFIT_IS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='净利润', help_text='净利润', null=True)
#     NP_BELONGTO_PARCOMSH = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='归属于母公司普通股东综合收益总额', help_text='归属于母公司普通股东综合收益总额', null=True)
#     CASH_RECP_SG_AND_RS = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='销售商品、提供劳务收到的现金', help_text='销售商品、提供劳务收到的现金', null=True)
#     NET_CASH_FLOWS_OPER_ACT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='经营活动产生的现金流量净额', help_text='经营活动产生的现金流量净额', null=True)
#     CASH_PAY_ACQ_CONST_FIOLTA = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='构建固定资产、无形资产和其他长期资产支付的现金', help_text='构建固定资产、无形资产和其他长期资产支付的现金', null=True)
#     NET_CASH_FLOWS_INV_ACT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='投资活动产生的现金流量净额', help_text='投资活动产生的现金流量净额', null=True)
#     NET_CASH_FLOWS_FNC_ACT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='筹资活动产生的现金流量净额', help_text='筹资活动产生的现金流量净额', null=True)
#     CASH_PAY_BEH_EMPL = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='支付给职工以及为职工支付的现金', help_text='支付给职工以及为职工支付的现金', null=True)
#     CASH_CASH_EQU_END_PERIOD = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='期末现金及现金等价物余额', help_text='期末现金及现金等价物余额', null=True)
#     DEPR_FA_COGA_DPBA = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='固定资产折旧、油气资产这好、生产性生物资产折旧', help_text='固定资产折旧、油气资产这好、生产性生物资产折旧', null=True)
#     SEGMENT_INDUSTRY_SALES = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='主营构成（按行业）-项目收入', help_text='主营构成（按行业）-项目收入', null=True)
#     SEGMENT_INDUSTRY_PROFIT = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='主营构成（按行业）-项目利润', help_text='主营构成（按行业）-项目利润', null=True)
#     STMNOTE_SEG_1501 = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='海外业务收入', help_text='海外业务收入', null=True)
#     STMNOTE_PROFITAPR_3 = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='可分配利润', help_text='可分配利润', null=True)
#     STMNOTE_PROFITAPR_4 = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='支付普通股股利', help_text='支付普通股股利', null=True)
#     RESEARCHANDDEVELOPMENTEXPENSES = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='研发费用', help_text='研发费用', null=True)
#     HOLDER_PCTBYFUND = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='基金持股比例', help_text='基金持股比例', null=True)
#     HOLDER_PCTBYQFII = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='QFII持股比例', help_text='QFII持股比例', null=True)
#     HOLDER_PCTBYSSFUND = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='社保持股比例', help_text='社保持股比例', null=True)
#     EXTRAORDINARY = models.DecimalField(max_digits=20,decimal_places=4, verbose_name='非经常性损益', help_text='非经常性损益', null=True)
#     EMPLOYEE = models.IntegerField(verbose_name='员工数', help_text='员工数', null=True)
#     EMPLOYEE_BA = models.IntegerField(verbose_name='本科', help_text='本科', null=True)
#     EMPLOYEE_MS = models.IntegerField(verbose_name='硕士', help_text='硕士', null=True)
#
#     class Meta:
#         unique_together = ('TRADE_CODE','REPORTDATE','ISSUINGDATE')
#         indexes = [
#             models.Index(fields=['TRADE_CODE'],name='fainfo_tc'),
#             models.Index(fields=['REPORTDATE'],name='fainfo_rdt'),
#             models.Index(fields=['ISSUINGDATE'], name='ISSUINGDATE'),
#             models.Index(fields=['TRADE_CODE','REPORTDATE']),
#         ]
#         verbose_name = '财务基础数据表'
#
#     def __str__(self):
#         return '%s(%s,issuing %s)' % (self.TRADE_CODE,self.REPORTDATE,self.ISSUINGDATE)
#
# #   其他数据表，例如货币/等    currency    assetsinfo
#
# class currency(models.Model):
#     CURRENCY_CODE = models.CharField(max_length=20,primary_key=True, verbose_name='货币代码', help_text='货币代码')
#     CURRENCY_NAME = models.CharField(max_length=20, verbose_name='货币名称', help_text='货币名称')
#
#     def __str__(self):
#         return self.CURRENCY_NAME
#
#     class Meta:
#         verbose_name = '货币表'
#
# class assetsinfo(models.Model):
#     ASSET_CODE = models.CharField(max_length=20, primary_key=True, verbose_name='资产代码', help_text='资产代码')
#     ASSET_NAME = models.CharField(max_length=50, verbose_name='资产名称', help_text='资产名称')
#
#     def __str__(self):
#         return self.ASSET_NAME
#
#     class Meta:
#         indexes = [
#             models.Index(fields=['ASSET_CODE']),
#         ]
#         verbose_name = '资产表'
#
# class country(models.Model):
#     COUNTRY_CODE = models.CharField(max_length=20,primary_key=True, verbose_name='代码', help_text='代码')
#     COUNTRY_NAME = models.CharField(max_length=20, verbose_name='国家名称', help_text='国家名称')
#     COUNTRY_EN = models.CharField(max_length=20, verbose_name='ENGLISH', help_text='ENGLISH')
#
#     def __str__(self):
#         return self.COUNTRY_NAME
#
#     class Meta:
#         verbose_name = '国家表'
#
#
# #   基础数据扩展表 obos超买超卖
#
# class obos(models.Model):
#     ID = models.IntegerField(auto_created=True,primary_key=True,default=1)
#     TRADE_CODE = models.ForeignKey('basicinfo', verbose_name='板块代码', on_delete=models.CASCADE)
#     DT = models.DateField(verbose_name='日期')
#     VALUE = models.DecimalField(verbose_name='超买超卖数值',max_digits=10,decimal_places=4)
#     SIGNAL = models.IntegerField(verbose_name='阈值信号')
#     AA = models.IntegerField(verbose_name='test')
#
#     def __str__(self):
#         return '%s(%s)' % (self.TRADE_CODE,self.DT)
#
#     class Meta:
#         verbose_name = '超买超卖表'
#         indexes = [
#             models.Index(fields=['TRADE_CODE','DT']),
#             models.Index(fields=['TRADE_CODE'], name='obos_tc')
#         ]