from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.account import models
from apps.operation.models import Inform
from utils.Tencent.sendemial import SENDEMAIL


@admin.register(models.UserInfo)  # 第一个参数可以是列表
class UserInfoAdmin(admin.ModelAdmin):
    def show_userAvatar(self, obj):
        return mark_safe(
            f"""
            <img  src=
            '{obj.detail.userAvatar if obj.detail.userAvatar else "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"}'
             width='30'  style=' border-radius: 50%;'
             />
            """
        )

    list_display = ['show_userAvatar', "username", "email", "create_time", ]
    show_userAvatar.short_description = "用户头像"

    def has_change_permission(self, request, obj=None):
        """是否允许修改"""
        return False


@admin.register(models.SiteData)  # 第一个参数可以是列表
class SiteDataAdmin(admin.ModelAdmin):
    def site_url_show(self, obj):
        return mark_safe(f"""<a href='{obj.site_url}' target='_blank'>点击跳转</a>""")

    """
    
    people = Person.objects.all()
    
    for person in people:
        person.age += 1
    
    Person.objects.bulk_update(people, update_fields = ['age'])

    """

    def email(self, queryset, operate, request):
        for i in queryset:
            i.isvalid = operate
        # 批量更新
        models.SiteData.objects.bulk_update(queryset, fields=["isvalid"])
        #     更新完成给推荐者发生邮箱信息
        """
            发送邮箱列表:
                不是给里面每一个email都发而是去重email再发,
                数据格式
                task_dic={
                email:[]
                email:[]
                }
        """
        # 构建完成
        task_dic = {}
        for obj in queryset:
            user = obj.recommend
            if task_dic.get(user):
                task_dic[user].append(obj.name)
                continue
            task_dic[user] = [obj.name]
        # 执行任务
        informs = []
        for user, name in task_dic.items():
            try:
                msg = ''
                if operate == 3:
                    msg = f"亲爱的{user.username}你好!你在codeminer.cn网站推荐的资源:{','.join(name)}审核已经通过了!积分+{len(name)}"
                    SENDEMAIL.config("CodeMiner-site", to=user.email, code='str',
                                     msg=msg)
                elif operate == 2:
                    msg = f"亲爱的{user.username}你好!你在codeminer.cn网站推荐的资源:{','.join(name)}审核未通过!失败:网站生效或者非法字符"
                    SENDEMAIL.config("CodeMiner-site", to=user.email, code='str',
                                     msg=msg)
                informs.append(Inform(content=msg, user=user, type=2))  # 创建Inform推荐消息任务
            except Exception as e:

                """如果qq邮箱不正确默认给用户个人发送请填写正确qq邮箱并且告诉用户审核已经通过"""
                print(e)
                continue
        Inform.objects.bulk_create(informs)  # 发布消息
        self.message_user(request, f"操作完成!!", level=25)

    def isvalid_true(self, request, queryset):
        """通过审核"""
        self.email(queryset, 3, request)

    def isvalid_false(self, request, queryset):
        """通过未审核"""
        self.email(queryset, 2, request)
        pass

    isvalid_true.short_description = '审核通过'
    isvalid_false.short_description = '审核不通过'
    isvalid_true.type = 'success'
    isvalid_false.type = 'danger'
    list_display = ['name', "site_url_show", "introduce", 'isvalid', ]
    search_fields = ["name", "introduce", "site_url"]
    ordering = ["-update_time"]  # 按id降序排序
    list_filter = ["isvalid", "datatype"]  # 列表页右侧的过滤栏
    actions_on_bottom = True  # 列表页下方显示删除框
    actions_on_top = False  # 列表页上方不显示删除框
    list_per_page = 10  # 列表每页显示条数
    readonly_fields = ('uid',)  # 只读字段
    # 修改列名
    site_url_show.admin_order_field = 'collect_num'  # 点击时的排序字段
    # 给有颜色的字段取一个别名
    site_url_show.short_description = '网站地址'

    # list_editable = ["isvalid",]
    actions = ['isvalid_true', "isvalid_false"]


@admin.register(*[models.Categories, models.Type])
class CategoriesAdmin(admin.ModelAdmin):
    pass
