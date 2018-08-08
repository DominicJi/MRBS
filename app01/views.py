from django.shortcuts import render,redirect,HttpResponse
from app01 import modelforms
from app01 import models
import json
from datetime import datetime
from django.http import JsonResponse
# Create your views here.
def reg(request):
    form_list=modelforms.My_model()
    if request.method=='POST':
        form_list=modelforms.My_model(request.POST)
        if form_list.is_valid():
            form_list.save()
            return redirect('/login/')
    return render(request,'reg.html',{'form_list':form_list})


def login(request):
    if request.method=='POST':
        name=request.POST.get('name')
        pwd=request.POST.get('pwd')
        user_obj=models.UserInfo.objects.filter(name=name,pwd=pwd).first()
        if user_obj:
            request.session['user']=user_obj.pk
            request.session['name']=user_obj.name
            return redirect('/index/')
    return render(request,'login.html')


def index(request):
    if not request.session.get('user'):
        return redirect('/login/')
    room_list = models.Room.objects.all()
    time_choices = models.Record.time_choices
    #默认展示当天日期下的预定情况
    from datetime import datetime
    #.now()获取的是当前时间的2018-08-08 15:38:30.616745格式再点date()拿到2018-08-08日期格式
    current_time=datetime.now().date()
    date = request.GET.get('choose_date','')
    if date:
        current_time=date
    '''在刚开始去构建前端展示页面时，对于表单里面的数据，我们肯定是想着在前端页面直接通过循环判断来渲染出来,
    这样做可以很快速的搭建出表格和样式，但是要想展示已存在数据则会发现基本做不到了，在这种情况下我们应该换个角度做
    把复杂需要判断的逻辑拿到后端来做，直接给前端返回html格式字符串。这样的话利用我们熟悉的编程语言去把控会变得简单很多
    '''
    html=''
    #循环取出一个个已有的会议室
    for room in room_list:
        #表单第一排会议室展示
        html+='<tr><td>%s(%s)</td>'%(room.caption,room.num)
        #再展示真正关键的对应时间段是否预订数据展示
        for time_choice in time_choices:
            #这一步可能一时糊涂会想不到用这样的方式去筛选到底哪些是已经被遇到的数据，这里就相当于一个个筛选匹配，能拿到数据就表明是有已经存在的数据
            book_obj=models.Record.objects.filter(room_id=room.pk,time_id=time_choice[0],date=current_time).first()
            if book_obj:
                #如果数据存在，也就是说被预订了，那么还需要判断是当前操作用户之前选定的
                if request.session['user']==book_obj.user.pk:
                    #如果是当前操作对象选过的，那么他有权再取消或重选
                    td='<td class="own_booked" room_id=%s time_id=%s>%s</td>'%(room.pk,time_choice[0],book_obj.user.name)
                else:
                    #否则则是他人选过的，那么当前操作用户没有对其再修改的权限
                    td='<td class="another_booked" room_id=%s time_id=%s>%s</td>'%(room.pk,time_choice[0],book_obj.user.name)
            else:
                #剩下的就是大家都没有选的可自由选择的
                td='<td class="free" room_id=%s time_id=%s></td>'%(room.pk,time_choice[0])
            html+=td
        #最后将外部的tr标签补全闭合
        html+='</tr>'

    return render(request,'index.html',locals())

def book(request):
    ret={'flag':True}
    post_data=json.loads(request.POST.get('post_data'))
    #如果前端传过来的日期字符串是2018 - 8 - 8这样的格式，我们需要将其空格去掉
    #这里我们对前端的数据进行了格式化定制处理，拿到的直接可以使用的日期对象了
    date=request.POST.get('date')
    #     .split(' ')
    # date=datetime.strptime(''.join(date),'%Y-%m-%d').date()

    #添加预定
    add_data=post_data.get('ADD')
    #由于是批量操作，这里我们使用批量添加的语法
    book_list=[]
    for room_id,time_id_list in add_data.items():
        for time_id in time_id_list:
            #这里加异常是防止传过来的数据被可以改动成已经被别人预定过的操作对象
            try:
                book = models.Record(user_id=request.session['user'], room_id=room_id, time_id=time_id, date=date)
                book_list.append(book)
            except Exception as a:
                ret['flag']=False

    #批量创建
    models.Record.objects.bulk_create(book_list)

    #取消预定
    del_data=post_data.get('DEL')
    for room_id,time_id_list in del_data.items():
        for time_id in time_id_list:
            models.Record.objects.filter(user_id=request.session['user'],room_id=room_id,time_id=time_id,date=date).delete()
    return JsonResponse(ret)