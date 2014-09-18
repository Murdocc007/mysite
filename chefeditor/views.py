import os, random, hashlib
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import Avg
from chefeditor.registrationform import RegistrationForm
from chefeditor.models import  Login, Users, ProfilePic, ProfilePicForm, Fiddle

def returnmd5(message):
    m = hashlib.md5()
    m.update(message)
    return m.hexdigest()

def index(request, loginFail = 0):
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid() :
                l = form.save()
                user = Users(login = l, name = request.POST.get('name'), profile_pic = 'avatar.jpg')
                saved_user = user.save()
                login = Login.objects.filter(email = request.POST.get('email'))
                print login
                set_session(request, login)
                return redirect('/chefeditor/explore/0')
    else:
        form = RegistrationForm()

    context = {'form' : form }
    if loginFail == '1':
        context['loginFail'] = 1
        context['errorMessage']="Incorrect Email ID and Password"
    else:
        context['loginFail'] = 0
    return render(request, 'home.html', context)

def explore(request, genre_id=0):
    c={}
    print "inside explore"
    print request.method
    print request.POST.get('css')
    if request.POST.get('css') is not None:
        c['css']=request.POST.get('css')
    if request.POST.get('html') is not None:
        c['html']=request.POST.get('html')
    if request.POST.get('javascript') is not None:
        c['javascript']=request.POST.get('javascript')
    if request.POST.get('name') is not None:
        c['name']=request.POST.get('name')
    fiddle=Fiddle.objects.filter(login=request.session['logged_in']['login_id'])
    c['fiddle']=fiddle
    return render(request, 'explore.html',c)
  
def save_template(request):
    print "inside save"
    c={}
    if len(request.POST.get('name')):
        f=Fiddle.objects.filter(name=request.POST.get('name'))
        if not f:
            l=Login.objects.get(email = request.session['logged_in']['email'])
            fiddle=Fiddle(login=l,html=request.POST.get('html'),css=request.POST.get('css'),javascript=request.POST.get('javascript'),name=request.POST.get('name'),public_temp=0)
            fiddle.save()
            print "exiting save"
            print request.method
            return explore(request,0)        
    if len(request.POST.get('name'))==0:
        c['errorMessage']="Please fill in the name!"
    else:
        c['errorMessage']="Duplicate Name!"
    if request.POST.get('css') is not None:
        c['css']=request.POST.get('css')
    if request.POST.get('html') is not None:
        c['html']=request.POST.get('html')
    if request.POST.get('javascript') is not None:
        c['javascript']=request.POST.get('javascript')
    if request.POST.get('name') is not None:
        c['name']=request.POST.get('name')
    fiddle=Fiddle.objects.filter(login=request.session['logged_in']['login_id'])
    c['fiddle']=fiddle
    return render(request, 'explore.html',c)

def view_template(request, login_id,template_name):
    c={}
    template=Fiddle.objects.get(login=login_id,name=template_name)
    c['css']=template.css
    c['html']=template.html
    c['javascript']=template.javascript
    c['public_temp']=template.public_temp
    return render(request, 'viewtemplate.html',c)


def modify_template(request):
    print "inside load"
    c={}
    if 'Delete_Template' in request.POST:
        if request.POST.get('dropdown') is not None:
            Fiddle.objects.filter(name=request.POST.get('dropdown')).delete()
            
    if 'Make_Public' in request.POST:
        if request.POST.get('dropdown') is not None:
            template=Fiddle.objects.get(name = request.POST.get('dropdown'))
            template.public_temp=1
            template.save()
            print template.public_temp
            c['css']=template.css
            c['html']=template.html
            c['javascript']=template.javascript
            c['name']=template.name
            c['public_url']=request.META['HTTP_HOST']+'/chefeditor/'+'viewtemplate/'+str(request.session['logged_in']['login_id'])+'/'+template.name
    
    if 'Load_Template' in request.POST:    
        if request.POST.get('dropdown') is not None:
            template=Fiddle.objects.get(name = request.POST.get('dropdown'))
            c['css']=template.css
            c['html']=template.html
            c['javascript']=template.javascript
            c['name']=template.name
            
    fiddle=Fiddle.objects.filter(login=request.session['logged_in']['login_id'])
    c['fiddle']=fiddle
    return render(request, 'explore.html',c)


def set_session(request, login):
    session_dict = { 'login_id':login[0].id, 'email':login[0].email, 'name':login[0].users_set.all()[0].name, 'profile_pic':login[0].users_set.all()[0].profile_pic }
    request.session['logged_in'] = session_dict

def set_session_obj(request, login):
    session_dict = { 'login_id':login.id, 'email':login.email, 'name':login.users_set.all()[0].name, 'profile_pic':login.users_set.all()[0].profile_pic }
    request.session['logged_in'] = session_dict

def checkLogin(request):
    c = {}
    
    if request.POST:
        username = request.POST.get('login_username')
        password = request.POST.get('login_password')

        login = Login.objects.filter(email = username)

    if login and login[0].password == returnmd5(password):
        set_session(request, login)
        return redirect('/chefeditor/explore/0')
    else:
        
        return redirect('/chefeditor/home/1')

def logout(request):
    del request.session['logged_in']
    return redirect('/chefeditor/')

def fblogin(request):
    return render(request, 'fblogin.html', {})

def checkFBLogin(request):
    if request.method == 'POST':
        femail = request.POST.get('email')
        fname = request.POST.get('name')
        fid = request.POST.get('id')
        login = Login.objects.filter(email=femail)
        if login:
            set_session(request, login)
        else:
            login_object = Login(email = femail, password = None)
            login_object.save()
            profile_pic_str = 'http://graph.facebook.com/' + fid + '/picture?type=large'
            user_object = Users(login = login_object, name = fname, profile_pic = profile_pic_str)
            user_object.save()
            set_session_obj(request, login_object)

        return HttpResponse("logged_in")
    else:
         return HttpResponse("not_logged_in")
         




