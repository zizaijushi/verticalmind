# Generated by Django 2.0.2 on 2018-03-22 05:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='assetsinfo',
            fields=[
                ('ASSET_CODE', models.CharField(help_text='资产代码', max_length=20, primary_key=True, serialize=False, verbose_name='资产代码')),
                ('ASSET_NAME', models.CharField(help_text='资产名称', max_length=50, verbose_name='资产名称')),
            ],
        ),
        migrations.CreateModel(
            name='basicinfo',
            fields=[
                ('TRADE_CODE', models.CharField(help_text='标的代码', max_length=20, primary_key=True, serialize=False, verbose_name='标的代码')),
                ('ASSETS', models.ForeignKey(help_text='标的所属资产代码', null=True, on_delete=django.db.models.deletion.SET_NULL, to='market.assetsinfo', verbose_name='标的所属资产代码')),
            ],
            options={
                'ordering': ['ASSETS', 'TRADE_CODE'],
            },
        ),
        migrations.CreateModel(
            name='basictree',
            fields=[
                ('ID', models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False)),
                ('DT', models.DateField(help_text='关联日期', verbose_name='关联日期')),
                ('DEPTH', models.IntegerField(help_text='子节子节点', verbose_name='子节点所在层级')),
                ('CHILD_CODE', models.ForeignKey(help_text='子节点', on_delete=django.db.models.deletion.CASCADE, related_name='child', to='market.basicinfo', verbose_name='子节点')),
                ('TRADE_CODE', models.ForeignKey(help_text='父节点', on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='market.basicinfo', verbose_name='父节点')),
            ],
            options={
                'ordering': ['TRADE_CODE', 'CHILD_CODE', 'DT'],
            },
        ),
        migrations.CreateModel(
            name='classinfo',
            fields=[
                ('ID', models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False)),
                ('DT', models.DateField(help_text='更新日期', verbose_name='更新日期')),
                ('SEC_NAME', models.CharField(help_text='类别名称', max_length=100, verbose_name='类别名称')),
                ('TRADE_CODE', models.ForeignKey(help_text='类别代码', on_delete=django.db.models.deletion.CASCADE, to='market.basicinfo', verbose_name='类别代码')),
            ],
        ),
        migrations.CreateModel(
            name='currency',
            fields=[
                ('CURRENCY_CODE', models.CharField(help_text='货币代码', max_length=20, primary_key=True, serialize=False, verbose_name='货币代码')),
                ('CURRENCY_NAME', models.CharField(help_text=')', max_length=20, verbose_name='货币名称')),
            ],
        ),
        migrations.CreateModel(
            name='financialinfo',
            fields=[
                ('ID', models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False)),
                ('REPORTDATE', models.DateField(help_text='报告期', verbose_name='报告期')),
                ('ISSUINGDATE', models.DateField(help_text='财报披露日期', verbose_name='财报披露日期')),
                ('SEC_NAME', models.CharField(help_text='名称', max_length=100, verbose_name='名称')),
                ('MONETARY_CAP', models.DecimalField(decimal_places=4, help_text='货币资产', max_digits=20, verbose_name='货币资产')),
                ('TRADABLE_FIN_ASSETS', models.DecimalField(decimal_places=4, help_text='交易性金融资产', max_digits=20, verbose_name='交易性金融资产')),
                ('NOTES_RCV', models.DecimalField(decimal_places=4, help_text='应收票据', max_digits=20, verbose_name='应收票据')),
                ('ACCT_RCV', models.DecimalField(decimal_places=4, help_text='应收账款', max_digits=20, verbose_name='应收账款')),
                ('OTH_RCV', models.DecimalField(decimal_places=4, help_text='其它应收款', max_digits=20, verbose_name='其它应收款')),
                ('PREPAY', models.DecimalField(decimal_places=4, help_text='预付账款', max_digits=20, verbose_name='预付账款')),
                ('INVENTORIES', models.DecimalField(decimal_places=4, help_text='存货', max_digits=20, verbose_name='存货')),
                ('OTH_CUR_ASSETS', models.DecimalField(decimal_places=4, help_text='其他流动资产', max_digits=20, verbose_name='其他流动资产')),
                ('TOT_CUR_ASSETS', models.DecimalField(decimal_places=4, help_text='流动资产合计', max_digits=20, verbose_name='流动资产合计')),
                ('FIX_ASSETS', models.DecimalField(decimal_places=4, help_text='固定资产', max_digits=20, verbose_name='固定资产')),
                ('INTANG_ASSETS', models.DecimalField(decimal_places=4, help_text='无形资产', max_digits=20, verbose_name='无形资产')),
                ('CONST_IN_PROG', models.DecimalField(decimal_places=4, help_text='在建工程', max_digits=20, verbose_name='在建工程')),
                ('GOODWILL', models.DecimalField(decimal_places=4, help_text='商誉', max_digits=20, verbose_name='商誉')),
                ('TOT_ASSETS', models.DecimalField(decimal_places=4, help_text='资产总计', max_digits=20, verbose_name='资产总计')),
                ('ADV_FROM_CUST', models.DecimalField(decimal_places=4, help_text='预收账款', max_digits=20, verbose_name='预收账款')),
                ('NOTES_PAYABLE', models.DecimalField(decimal_places=4, help_text='应付票据', max_digits=20, verbose_name='应付票据')),
                ('ACCT_PAYABLE', models.DecimalField(decimal_places=4, help_text='应付账款', max_digits=20, verbose_name='应付账款')),
                ('INTERESTDEBT', models.DecimalField(decimal_places=4, help_text='带息债务', max_digits=20, verbose_name='带息债务')),
                ('TOT_CUR_LIAB', models.DecimalField(decimal_places=4, help_text='流动负债合计', max_digits=20, verbose_name='流动负债合计')),
                ('TOT_LIAT', models.DecimalField(decimal_places=4, help_text='负债合计', max_digits=20, verbose_name='负债合计')),
                ('UNDISTRIBUTED_PROFIT', models.DecimalField(decimal_places=4, help_text='未分配利润', max_digits=20, verbose_name='未分配利润')),
                ('EQY_BELONGTO_PARCOMSH', models.DecimalField(decimal_places=4, help_text='归属母公司股东的权益', max_digits=20, verbose_name='归属母公司股东的权益')),
                ('OPER_REV', models.DecimalField(decimal_places=4, help_text='营业收入', max_digits=20, verbose_name='营业收入')),
                ('OPER_COST', models.DecimalField(decimal_places=4, help_text='营业成本', max_digits=20, verbose_name='营业成本')),
                ('SELLING_DIST_EXP', models.DecimalField(decimal_places=4, help_text='销售费用', max_digits=20, verbose_name='销售费用')),
                ('GERL_ADMIN_EXP', models.DecimalField(decimal_places=4, help_text='管理费用', max_digits=20, verbose_name='管理费用')),
                ('FIN_EXP_IS', models.DecimalField(decimal_places=4, help_text='财务费用', max_digits=20, verbose_name='财务费用')),
                ('OPPROFIT', models.DecimalField(decimal_places=4, help_text='营业利润', max_digits=20, verbose_name='营业利润')),
                ('NET_PROFIT_IS', models.DecimalField(decimal_places=4, help_text='净利润', max_digits=20, verbose_name='净利润')),
                ('NP_BELONGTO_PARCOMSH', models.DecimalField(decimal_places=4, help_text='归属于母公司普通股东综合收益总额', max_digits=20, verbose_name='归属于母公司普通股东综合收益总额')),
                ('CASH_RECP_SG_AND_RS', models.DecimalField(decimal_places=4, help_text='销售商品、提供劳务收到的现金', max_digits=20, verbose_name='销售商品、提供劳务收到的现金')),
                ('NET_CASH_FLOWS_OPER_ACT', models.DecimalField(decimal_places=4, help_text='经营活动产生的现金流量净额', max_digits=20, verbose_name='经营活动产生的现金流量净额')),
                ('CASH_PAY_ACQ_CONST_FIOLTA', models.DecimalField(decimal_places=4, help_text='构建固定资产、无形资产和其他长期资产支付的现金', max_digits=20, verbose_name='构建固定资产、无形资产和其他长期资产支付的现金')),
                ('NET_CASH_FLOWS_INV_ACT', models.DecimalField(decimal_places=4, help_text='投资活动产生的现金流量净额', max_digits=20, verbose_name='投资活动产生的现金流量净额')),
                ('NET_CASH_FLOWS_FNC_ACT', models.DecimalField(decimal_places=4, help_text='筹资活动产生的现金流量净额', max_digits=20, verbose_name='筹资活动产生的现金流量净额')),
                ('CASH_PAY_BEH_EMPL', models.DecimalField(decimal_places=4, help_text='支付给职工以及为职工支付的现金', max_digits=20, verbose_name='支付给职工以及为职工支付的现金')),
                ('CASH_CASH_EQU_END_PERIOD', models.DecimalField(decimal_places=4, help_text='期末现金及现金等价物余额', max_digits=20, verbose_name='期末现金及现金等价物余额')),
                ('DEPR_FA_COGA_DPBA', models.DecimalField(decimal_places=4, help_text='固定资产折旧、油气资产这好、生产性生物资产折旧', max_digits=20, verbose_name='固定资产折旧、油气资产这好、生产性生物资产折旧')),
                ('SEGMENT_INDUSTRY_SALES', models.DecimalField(decimal_places=4, help_text='主营构成（按行业）-项目收入', max_digits=20, verbose_name='主营构成（按行业）-项目收入')),
                ('SEGMENT_INDUSTRY_PROFIT', models.DecimalField(decimal_places=4, help_text='主营构成（按行业）-项目利润', max_digits=20, verbose_name='主营构成（按行业）-项目利润')),
                ('STMNOTE_SEG_1501', models.DecimalField(decimal_places=4, help_text='海外业务收入', max_digits=20, verbose_name='海外业务收入')),
                ('STMNOTE_PROFITAPR_3', models.DecimalField(decimal_places=4, help_text='可分配利润', max_digits=20, verbose_name='可分配利润')),
                ('STMNOTE_PROFITAPR_4', models.DecimalField(decimal_places=4, help_text='支付普通股股利', max_digits=20, verbose_name='支付普通股股利')),
                ('RESEARCHANDDEVELOPMENTEXPENSES', models.DecimalField(decimal_places=4, help_text='研发费用', max_digits=20, verbose_name='研发费用')),
                ('HOLDER_PCTBYFUND', models.DecimalField(decimal_places=4, help_text='基金持股比例', max_digits=20, verbose_name='基金持股比例')),
                ('HOLDER_PCTBYQFII', models.DecimalField(decimal_places=4, help_text='QFII持股比例', max_digits=20, verbose_name='QFII持股比例')),
                ('HOLDER_PCTBYSSFUND', models.DecimalField(decimal_places=4, help_text='社保持股比例', max_digits=20, verbose_name='社保持股比例')),
                ('EXTRAORDINARY', models.DecimalField(decimal_places=4, help_text='非经常性损益', max_digits=20, verbose_name='非经常性损益')),
                ('EMPLOYEE', models.IntegerField(help_text='员工数', verbose_name='员工数')),
                ('EMPLOYEE_BA', models.IntegerField(help_text='本科', verbose_name='本科')),
                ('EMPLOYEE_MS', models.IntegerField(help_text='硕士', verbose_name='硕士')),
                ('TRADE_CODE', models.ForeignKey(help_text='代码', on_delete=django.db.models.deletion.CASCADE, to='market.basicinfo', verbose_name='代码')),
            ],
        ),
        migrations.CreateModel(
            name='indexinfo',
            fields=[
                ('ID', models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False)),
                ('DT', models.DateField(help_text='更新日期', verbose_name='更新日期')),
                ('SEC_NAME', models.CharField(help_text='指数名称', max_length=100, verbose_name='指数名称')),
                ('TRADE_CODE', models.ForeignKey(help_text='指数代码', on_delete=django.db.models.deletion.CASCADE, to='market.basicinfo', verbose_name='指数代码')),
            ],
        ),
        migrations.CreateModel(
            name='marketinfo',
            fields=[
                ('ID', models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False)),
                ('SEC_NAME', models.CharField(help_text='市场数据名称', max_length=100, verbose_name='市场数据名称')),
                ('DT', models.DateField(help_text='日期', verbose_name='日期')),
                ('OPEN', models.DecimalField(decimal_places=4, help_text='开盘价', max_digits=10, verbose_name='开盘价')),
                ('HIGH', models.DecimalField(decimal_places=4, help_text='最高价', max_digits=10, verbose_name='最高价')),
                ('LOW', models.DecimalField(decimal_places=4, help_text='最低价', max_digits=10, verbose_name='最低价')),
                ('CLOSE', models.DecimalField(decimal_places=4, help_text='收盘价', max_digits=10, verbose_name='收盘价')),
                ('AVGPRICE', models.DecimalField(decimal_places=4, help_text='平均价', max_digits=10, verbose_name='平均价')),
                ('FACTOR', models.DecimalField(decimal_places=4, help_text='复权因子', max_digits=20, verbose_name='复权因子')),
                ('VOLUME', models.DecimalField(decimal_places=4, help_text='成交量', max_digits=20, verbose_name='成交量')),
                ('AMT', models.DecimalField(decimal_places=4, help_text='成交额', max_digits=20, verbose_name='成交额')),
                ('MKT_CAP_ARD', models.DecimalField(decimal_places=4, help_text='总市值（对应WIND总市值2）', max_digits=20, verbose_name='总市值')),
                ('MKT_FREESHARES', models.DecimalField(decimal_places=4, help_text='流通市值', max_digits=20, verbose_name='流通市值')),
                ('TRADE_CODE', models.ForeignKey(help_text='市场数据代码', on_delete=django.db.models.deletion.CASCADE, to='market.basicinfo', verbose_name='市场数据代码')),
            ],
        ),
        migrations.CreateModel(
            name='stockinfo',
            fields=[
                ('ID', models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False)),
                ('DT', models.DateField(help_text='更新日期', verbose_name='更新日期')),
                ('SEC_NAME', models.CharField(help_text='个股名称', max_length=100, verbose_name='个股名称')),
                ('IPO_DATE', models.DateField(help_text='IPO时间', verbose_name='IPO时间')),
                ('COUNTRY', models.CharField(help_text='国家', max_length=20, verbose_name='国家')),
                ('PROVINCE', models.CharField(help_text='省份', max_length=50, verbose_name='省份')),
                ('CITY', models.CharField(help_text='城市', max_length=50, verbose_name='城市')),
                ('PHONE', models.CharField(help_text='更新日期', max_length=50, verbose_name='电话')),
                ('OFFICE', models.TextField(help_text='办公室', verbose_name='办公室')),
                ('NATURE', models.CharField(help_text='公司性质', max_length=255, verbose_name='公司性质')),
                ('BRIEFING', models.TextField(help_text='简介', verbose_name='简介')),
                ('BUSINESS', models.TextField(help_text='商业模式', verbose_name='商业模式')),
                ('MAJORPRODUCT', models.TextField(help_text='主营项目', verbose_name='主营项目')),
                ('CURRENCY', models.ForeignKey(help_text='货币', null=True, on_delete=django.db.models.deletion.SET_NULL, to='market.currency', verbose_name='货币')),
                ('TRADE_CODE', models.ForeignKey(help_text='股票代码', on_delete=django.db.models.deletion.CASCADE, to='market.basicinfo', verbose_name='股票代码')),
            ],
        ),
        migrations.AddIndex(
            model_name='assetsinfo',
            index=models.Index(fields=['ASSET_CODE'], name='market_asse_ASSET_C_893f40_idx'),
        ),
        migrations.AddIndex(
            model_name='stockinfo',
            index=models.Index(fields=['TRADE_CODE'], name='stockinfo_tc'),
        ),
        migrations.AddIndex(
            model_name='stockinfo',
            index=models.Index(fields=['DT'], name='stockinfo_dt'),
        ),
        migrations.AddIndex(
            model_name='stockinfo',
            index=models.Index(fields=['TRADE_CODE', 'DT'], name='market_stoc_TRADE_C_958260_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='stockinfo',
            unique_together={('TRADE_CODE', 'DT')},
        ),
        migrations.AddIndex(
            model_name='marketinfo',
            index=models.Index(fields=['TRADE_CODE'], name='marketinfo_tc'),
        ),
        migrations.AddIndex(
            model_name='marketinfo',
            index=models.Index(fields=['DT'], name='marketinfo_dt'),
        ),
        migrations.AddIndex(
            model_name='marketinfo',
            index=models.Index(fields=['TRADE_CODE', 'DT'], name='market_mark_TRADE_C_8a8d23_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='marketinfo',
            unique_together={('TRADE_CODE', 'DT')},
        ),
        migrations.AddIndex(
            model_name='indexinfo',
            index=models.Index(fields=['TRADE_CODE'], name='stockinfo_tc'),
        ),
        migrations.AddIndex(
            model_name='indexinfo',
            index=models.Index(fields=['DT'], name='stockinfo_dt'),
        ),
        migrations.AddIndex(
            model_name='indexinfo',
            index=models.Index(fields=['TRADE_CODE', 'DT'], name='market_inde_TRADE_C_0809e0_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='indexinfo',
            unique_together={('TRADE_CODE', 'DT')},
        ),
        migrations.AddIndex(
            model_name='financialinfo',
            index=models.Index(fields=['TRADE_CODE'], name='fainfo_tc'),
        ),
        migrations.AddIndex(
            model_name='financialinfo',
            index=models.Index(fields=['REPORTDATE'], name='fainfo_rdt'),
        ),
        migrations.AddIndex(
            model_name='financialinfo',
            index=models.Index(fields=['ISSUINGDATE'], name='ISSUINGDATE'),
        ),
        migrations.AddIndex(
            model_name='financialinfo',
            index=models.Index(fields=['TRADE_CODE', 'REPORTDATE'], name='market_fina_TRADE_C_737bd9_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='financialinfo',
            unique_together={('TRADE_CODE', 'REPORTDATE', 'ISSUINGDATE')},
        ),
        migrations.AddIndex(
            model_name='basictree',
            index=models.Index(fields=['TRADE_CODE'], name='basictree_tc'),
        ),
        migrations.AddIndex(
            model_name='basictree',
            index=models.Index(fields=['CHILD_CODE'], name='basictree_cc'),
        ),
        migrations.AddIndex(
            model_name='basictree',
            index=models.Index(fields=['DT'], name='basictree_dt'),
        ),
        migrations.AddIndex(
            model_name='basictree',
            index=models.Index(fields=['CHILD_CODE', 'DT'], name='basictree_ccdt'),
        ),
        migrations.AddIndex(
            model_name='basictree',
            index=models.Index(fields=['TRADE_CODE', 'DT'], name='market_basi_TRADE_C_1c4258_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='basictree',
            unique_together={('TRADE_CODE', 'CHILD_CODE', 'DT')},
        ),
        migrations.AddIndex(
            model_name='basicinfo',
            index=models.Index(fields=['TRADE_CODE'], name='market_basi_TRADE_C_57861c_idx'),
        ),
    ]