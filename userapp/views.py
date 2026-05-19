from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
import mysql.connector
import datetime
import random
import requests
from django.http import JsonResponse

def getdb():
    mydb = mysql.connector.connect(host="localhost",user="root",password="",database="mobila_db")
    return mydb

def uindex(request):
    try:
        rsel = "select * from feedback_tb where f_status = 'Active' order by f_id desc"
        mydb = getdb()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(rsel)
        f_data = mycursor.fetchall()

        sel = "select * from category_tb where cat_status = 'Active' order by cat_id desc"
        mydb = getdb()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(sel)
        cat_data = mycursor.fetchall()

        psel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price) / product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb where category_tb.cat_id = product_tb.cat_id and p_status = 'Active' order by RAND() LIMIT 8"
        mydb = getdb()
        mycursor = mydb.cursor(dictionary=True) 
        mycursor.execute(psel)
        p_data = mycursor.fetchall()

        alldata = {
            'cat_data':cat_data,
            'p_data':p_data,
            'f_data':f_data,
        }

        return render(request,'uindex.html',alldata)
    except NameError:
        print("internal error")
    except:
        print('Error returned')



def uterms(request):
    try:

        return render(request,'uterms.html',{})
    except NameError:
        print("internal error")
    except:
        print('Error returned')


def uabout(request):
    try:

        return render(request,'uabout.html',{})
    except NameError:
        print("internal error")
    except:
        print('Error returned')

def ucontact(request):
    try:
        if request.POST:
            
            f_name = request.POST.get("f_name")
            f_contact = request.POST.get("f_contact")
            f_message = request.POST.get("f_message")
            
            f_status = 'Deactive'

            cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            ins = "INSERT INTO `feedback_tb`(`f_name`, `f_contact`, `f_message`,`f_status`, `f_cdate`, " \
            "`f_udate`) VALUES ('"+str(f_name)+"','"+str(f_contact)+"','"+str(f_message)+"',"
            "'"+str(f_status)+"','"+cdate+"','"+cdate+"')"
            mydb = getdb()
            mycursor = mydb.cursor() 
            mycursor.execute(ins)
            mydb.commit()
            return redirect("uindex")

        else:
            return render(request,'ucontact.html',{})
    except NameError:
        print("internal error")
    except:
        print('Error returned')

def usignup(request):
    try:
        msg = ""
        if request.POST:

            rtype = request.GET.get("verify")

            if rtype == 'number':

                u_contact = request.POST.get("u_contact")
                
                chk = "select * from user_tb where u_contact = '"+str(u_contact)+"'"
                mydb = getdb()
                mycursor = mydb.cursor(dictionary=True) 
                mycursor.execute(chk)
                udata = mycursor.fetchall()

                if len(udata) > 0:
                    msg = "Alreday Exists This Contact Number.!"
                    return render(request,'usignup.html',{'msg': msg})
                
                else:
                    otp = random.randrange(1000,9999)
                    mtype = "OTP"
                    request.session['otp'] = otp
                    request.session['contact'] = u_contact

                    sms_url = f"https://invisionsoftwaresolution.in/Student/isssmssend.php?contact={u_contact}&message={otp}&type={mtype}"
                    response = requests.post(sms_url)
                    return redirect('/usignup?verify=otp')
                
            elif rtype == 'otp':
                u_otp = request.POST.get("u_otp")
                otp = request.session['otp']
                if u_otp == str(otp):
                    return redirect('/usignup?verify=usignup')
                else:
                     msg = "Invalid OTP..!"
                     return render(request,'usignup.html',{'msg':msg}) 

            else:
                u_name = request.POST.get("u_name")
                u_address = request.POST.get("u_address")
                u_contact = request.POST.get("u_contact")
                u_img = request.FILES["u_img"]
                img = FileSystemStorage()
                u_img = img.save(u_img.name,u_img)
                
                u_password= request.POST.get("u_password")

                u_status = 'Active'

                udate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
                ins = "INSERT INTO `user_tb`(`u_name`, `u_contact`, `u_address`,`u_img`, `u_password`, `u_status`,`u_cdate`,`u_udate`) VALUES ('"+str(u_name)+"','"+str(u_contact)+"','"+str(u_address)+"','"+str(u_img)+"','"+str(u_password)+"','"+str(u_status)+"','"+udate+"','"+udate+"')"
                mydb = getdb()
                mycursor = mydb.cursor() 
                mycursor.execute(ins)
                mydb.commit()
                return redirect("usignin")
           
        else:
            return render(request,'usignup.html',{'msg': msg})
    except NameError:
        print("internal error")
    except:
        print('Error returned')

def resendotp(request):
    try:
        otp = random.randrange(1000,9999)
        mtype = "OTP"
        request.session['otp'] = otp
        u_contact = request.session['contact'] 

        sms_url = f"https://invisionsoftwaresolution.in/Student/isssmssend.php?contact={u_contact}&message={otp}&type={mtype}"
        response = requests.post(sms_url)
        return redirect('/usignup?verify=otp')
        
    except NameError:
        print("internal error")
    except:
        print('Error returned')

def usignin(request):
    try:
        msg=""
        if request.POST:

            username = request.POST.get("username")
            password = request.POST.get("password")

            lsel = "select * from user_tb where u_contact = '"+str(username)+"' and u_password = '"+str(password)+"'"" and u_status = 'Active'"
            mydb = getdb()
            mycursor = mydb.cursor() 
            mycursor.execute(lsel)
            l_data = mycursor.fetchall()
           
            if len(l_data) > 0:
                
                request.session["uid"] = l_data[0][0]
                request.session["ucontact"] = username

                return redirect("uindex")
            else:
                msg = "Invalid Username Or Password.!"
                return render(request,'usignin.html',{'msg':msg})
        else:
            return render(request,'usignin.html',{'msg':msg})
    except NameError:
        print("internal error")
    except:
        print('Error returned')

def ulogout(request):
    try:
        aid = request.session["uid"]
        cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        update = "update user_tb set u_udate = '"+cdate+"' where u_id = '"+str(aid)+"'"
        mydb = getdb()
        mycursor = mydb.cursor(dictionary=True) 
        mycursor.execute(update)
        mydb.commit()

        request.session["uid"] = None
        request.session["ucontact"] = None
       
        return redirect("usignin")
    
    except NameError:
        print("internal error")
    except:
        print('Error returned')


def uproduct(request):
    try:
        if request.GET.get("cat_id")!= None:
            cat_id = request.GET.get("cat_id")
            
            csel = "select * from category_tb where cat_status = 'Active' order by cat_id desc"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(csel)
            c_data = mycursor.fetchall()

            psel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price)" \
            " / product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb " \
            "where category_tb.cat_id = product_tb.cat_id and p_status = 'Active' and " \
            "product_tb.cat_id = '"+str(cat_id)+"' order by p_id desc"

            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(psel)
            p_data = mycursor.fetchall()

            alldata = {
                'c_data':c_data,
                'p_data':p_data,
            }

            return render(request,'uproduct.html',alldata)
    
        else:
            csel = "select * from category_tb where cat_status = 'Active' order by cat_id desc"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(csel)
            c_data = mycursor.fetchall()

            psel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price) " \
            "/ product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb" \
            " where category_tb.cat_id = product_tb.cat_id and p_status = 'Active' order by p_id desc"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(psel)
            p_data = mycursor.fetchall()

            alldata = {
                'c_data':c_data,
                'p_data':p_data
            }

        return render(request,'uproduct.html',alldata)
    except NameError:
        print("internal error")
    except:
        print('Error returned')


def uproductdetails(request):
    try:
        msg = ""
        if request.POST:
            chk = request.POST.get("chk")
            if chk == 'No':
            
                f_name = request.POST.get("f_name")
                f_contact = request.POST.get("f_contact")
                f_message = request.POST.get("f_message")
            
                f_status = 'Deactive'

                cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                ins = "INSERT INTO `feedback_tb`(`f_name`, `f_contact`, `f_message`,`f_status`, `f_cdate`, `f_udate`) VALUES ('"+str(f_name)+"','"+str(f_contact)+"','"+str(f_message)+"','"+str(f_status)+"','"+cdate+"','"+cdate+"')"
                mydb = getdb()
                mycursor = mydb.cursor() 
                mycursor.execute(ins)
                mydb.commit()
                return redirect("uindex")

            else:
                userid = request.session["uid"]
                o_sellprice =   request.POST.get("o_sellprice")
                o_status = 'Cart'
                p_id = request.GET.get("p_id")
                od_status = 'Active'
                cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                chk = "select * from order_tb,cart_tb where order_tb.o_id = cart_tb.o_id and order_tb.u_id = '"+str(userid)+"' and cart_tb.p_id = '"+str(p_id)+"' and cart_tb.c_status = 'Active'"
                #query exe - run
                mydb = getdb()
                mycursor = mydb.cursor()
                mycursor.execute(chk)
                chkdata = mycursor.fetchall()

                if len(chkdata) > 0:
                    msg = "You have Already added this product to the Cart.!"

                    p_id = request.GET.get("p_id")
            
                    psel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price) / product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb where category_tb.cat_id = product_tb.cat_id and product_tb.p_id = '"+str(p_id)+"' order by p_id desc"

                    mydb = getdb()
                    mycursor = mydb.cursor(dictionary=True) 
                    mycursor.execute(psel)
                    p_data = mycursor.fetchall()

                    sel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price) / product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb where category_tb.cat_id = product_tb.cat_id ORDER BY RAND() limit 8"

                    mydb = getdb()
                    mycursor = mydb.cursor(dictionary=True) 
                    mycursor.execute(sel)
                    pro_data = mycursor.fetchall()

                    alldata = {
                        'p_data':p_data,
                        'pro_data':pro_data,
                        'msg':msg
                    }

                    return render(request,'uproductdetails.html',alldata)
                
                else:

                    ordchk = "select * from order_tb where o_status = 'Cart' and  u_id = '"+str(userid)+"'" 
                    # connection create object
                    mydb = getdb()
                    mycursor = mydb.cursor()
                    #query execute
                    mycursor.execute(ordchk)
                    odata = mycursor.fetchall()
                    if len(odata) == 0:

                        ins = "INSERT INTO `order_tb`(`u_id`,`o_totalquntity`, `o_totalprice`, `o_status`, `o_cdate`, `o_udate`) VALUES ('"+str(userid)+"','1','"+str(o_sellprice)+"','"+str(o_status)+"','"+cdate+"','"+cdate+"')"           
                        #query exe - run
                        mydb = getdb()
                        mycursor = mydb.cursor()
                        mycursor.execute(ins)
                        mydb.commit()

                        lastid = mycursor.lastrowid
                    
                        ins1 = "INSERT INTO `cart_tb`(`o_id`, `p_id`, `c_price`, `c_quantity`, `c_totalprice`, `c_status`, `c_cdate`, `c_udate`) VALUES ('"+str(lastid)+"','"+str(p_id)+"','"+str(o_sellprice)+"','1','"+str(o_sellprice)+"','"+str(od_status)+"','"+cdate+"','"+cdate+"')"           
                        
                        #query exe - run
                        mydb = getdb()
                        mycursor = mydb.cursor()
                        mycursor.execute(ins1)
                        mydb.commit()
                        return redirect("umycart")
                    
                    else:
                        lastid = odata[0][0]

                        ins1 = "INSERT INTO `cart_tb`(`o_id`, `p_id`, `c_price`, `c_quantity`, `c_totalprice`, `c_status`, `c_cdate`, `c_udate`) VALUES ('"+str(lastid)+"','"+str(p_id)+"','"+str(o_sellprice)+"','1','"+str(o_sellprice)+"','"+str(od_status)+"','"+cdate+"','"+cdate+"')"           
                        
                        #query exe - run
                        mydb = getdb()
                        mycursor = mydb.cursor()
                        mycursor.execute(ins1)
                        mydb.commit()
                        return redirect("umycart")
                    
        else:

            p_id = request.GET.get("p_id")

            psel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price) / product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb where category_tb.cat_id = product_tb.cat_id and product_tb.p_id = '"+str(p_id)+"' order by p_id desc"

            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(psel)
            p_data = mycursor.fetchall()

            sel = "select product_tb.*,category_tb.*,ROUND(((product_tb.p_mrp - product_tb.p_price) / product_tb.p_mrp) * 100 ,1) AS discount from product_tb,category_tb where category_tb.cat_id = product_tb.cat_id ORDER BY RAND() limit 8"

            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(sel)
            pro_data = mycursor.fetchall()

           
            alldata = {
                        'p_data':p_data,
                        'pro_data':pro_data,
                        'msg':msg
                    }

            return render(request,'uproductdetails.html',alldata)
    except NameError:
        print("internal error")
    except:
        print('Error returned')


def uforgotpassword(request):
    try:
        msg = ""
        if request.POST:
            u_contact = request.POST.get("u_contact")
           
            sel = "select * from user_tb where u_contact =  '"+str(u_contact)+"' and u_status = 'Active'"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute(sel)
            udata = mycursor.fetchall()
            
   
            if len(udata) > 0:
                
                upassword = udata[0]["u_password"]

                mtype = "Forgotpassword"

                sms_url = f"https://invisionsoftwaresolution.in/Student/isssmssend.php?contact={u_contact}&message={upassword}&type={mtype}"
                response = requests.post(sms_url)

                return redirect('/usignin?alert=1')
                
            else:
                msg = "Contact Number Is Not Registered.!" 
                return render(request,'uforgotpassword.html',{'msg':msg})  
        else:
            return render(request,'uforgotpassword.html',{'msg' : msg})
    except NameError:
        print("internal error")
    except:
        print('Error returned')    



def umyorder(request):
    try:
        if request.GET.get("odel")!= None:
            odel = request.GET.get("odel")

            delete = "delete from order_tb where o_id ='"+str(odel)+"'"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute(delete)
            mydb.commit()

            delete = "delete from cart_tb where o_id ='"+str(odel)+"'"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute(delete)
            mydb.commit()

            return redirect("umyorder")
        else:
            uid = request.session["uid"]

            osel = "select * from order_tb o,user_tb u where o.u_id = u.u_id and o.u_id = '"+str(uid)+"' order by o.o_id desc"
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True) 
            mycursor.execute(osel)
            o_data = mycursor.fetchall()

            return render(request,'umyorder.html',{'o_data':o_data})
    except NameError:
        print("internal error")
    except:
        print('Error returned')


def ucart(request):
    try:
        o_id = request.GET.get("o_id")

        osel = "select * from cart_tb c,order_tb o,product_tb p where c.o_id = o.o_id and c.p_id = p.p_id and c.o_id = '"+str(o_id)+"' order by c.c_id desc"
        mydb = getdb()
        mycursor = mydb.cursor(dictionary=True) 
        mycursor.execute(osel)
        o_data = mycursor.fetchall()

        return render(request,'ucart.html',{'o_data':o_data})
    except NameError:
        print("internal error")
    except:
        print('Error returned')



def uprofile(request): 
    try:
        if request.POST:
            uid = request.session["uid"]
            u_name = request.POST.get("u_name")
            u_add = request.POST.get("u_add")
            u_password = request.POST.get("u_password")
              
            if request.POST.get("u_img") != "":
                u_img = request.FILES["u_img"]
                img = FileSystemStorage()
                old_img = img.save(u_img.name, u_img)
            else:
                old_img = request.POST.get("old_img")
      
            cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          
            update = "update user_tb set u_name = '"+str(u_name)+"',u_address='"+str(u_add) \
            +"',u_password = '"+str(u_password)+"',u_img = '"+str(old_img) \
            +"',u_udate = '"+cdate+"' where u_id = '"+str(uid)+"'"
     
            mydb = getdb()
            mycursor = mydb.cursor()
            mycursor.execute(update)
            mydb.commit()
            return redirect("uindex")               

        else:
            uid = request.session["uid"]
            sel = "select * from user_tb where u_id = '"+str(uid)+"'"
           
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute(sel)
            u_data = mycursor.fetchall()
            
            return render(request, 'uprofile.html', {'u_data': u_data})

    except NameError:
        return HttpResponse("internal error")
    except:
        return HttpResponse("Error returned")

def umycart(request):


    try:
        if request.POST:
            
             userid = request.session["uid"]
            
             o_totalquntity = request.POST.get("o_totalquntity")
             o_total = request.POST.get("o_total")
             o_shipping = request.POST.get("o_shipping")
             o_pincode = request.POST.get("o_pincode")
             o_status = "Pending"
             od_status = "Deactive"

             # ---------------- PINCODE VALIDATION ----------------
             if not o_pincode.isdigit():
                 script = """
                 <script>
                     alert('Pincode must contain only numbers');
                     window.location.href='/umycart/';
                 </script>
                 """
                 return HttpResponse(script)

             if len(o_pincode) != 6:
                 script = """
                 <script>
                     alert('Pincode must be 6 digits');
                     window.location.href='/umycart/';
                 </script>
                 """
                 return HttpResponse(script)
             # ----------------------------------------------------
 
             cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

             #insert query
             chk = "select * from order_tb,cart_tb where order_tb.o_id = cart_tb.o_id and order_tb.u_id " "= '"+str(userid)+"' and order_tb.o_status = 'Cart' and cart_tb.c_status = 'Active'"
             #query exe - run
             mydb = getdb()
             mycursor = mydb.cursor()
             mycursor.execute(chk)
             chkdata = mycursor.fetchall()

             o_id = chkdata[0][0]

             up1 = "update cart_tb set c_status = '"+str(od_status)+"',c_udate"" = '"+cdate+"' where o_id	 = '"+str(o_id)+"'"
             #query exe - run
             mydb = getdb()
             mycursor = mydb.cursor()
             mycursor.execute(up1)
             mydb.commit()
 

             up = "update order_tb set o_totalquntity = '"+str(o_totalquntity)+"',o_totalprice ="" '"+str(o_total)+"',o_address = '"+str(o_shipping)+"', o_pincode = ""'"+str(o_pincode)+"',o_status = '"+str(o_status)+"',o_udate = '"+cdate+"'"" where u_id = '"+str(userid)+"' and o_status = 'Cart'"
             #query exe - run
             mydb = getdb()
             mycursor = mydb.cursor()
             mycursor.execute(up)
             mydb.commit()
             return redirect("umyorder")

             
        elif request.GET.get("minus") !=None: 
            bdid = request.GET.get("bdid")
            qty = request.GET.get("qty")
            price = request.GET.get("price")

            newqty = int(qty) - 1
            newprice = int(price) * newqty
            cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            up = "update cart_tb  set c_quantity = '"+str(newqty)+"', c_totalprice = ""'"+str(newprice)+"',c_udate = '"+cdate+"' where c_id = '"+str(bdid)+"'"
             #query exe - run
            mydb = getdb()
            mycursor = mydb.cursor()
            mycursor.execute(up)
            mydb.commit()
            return redirect("umycart")

        elif request.GET.get("pluse") !=None: 
            bdid = request.GET.get("bdid")
            qty = request.GET.get("qty")
            price = request.GET.get("price")

            newqty = int(qty) + 1
            newprice = int(price) * newqty
            cdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            up = "update cart_tb  set c_quantity = '"+str(newqty)+"', c_totalprice = ""'"+str(newprice)+"',c_udate = '"+cdate+"' where c_id = '"+str(bdid)+"'"
            print(up)
            #query exe - run
            mydb = getdb()
            mycursor = mydb.cursor()
            mycursor.execute(up)
            mydb.commit()
            return redirect("umycart")
        
        elif request.GET.get("delete") !=None: 
              bdid = request.GET.get("bdid")

              ins = "DELETE from `cart_tb` where c_id = '"+str(bdid)+"'"

              #query exe - run
              mydb = getdb()
              mycursor = mydb.cursor()
              mycursor.execute(ins)
              mydb.commit()
              return redirect("umycart")


        else:    
            userid = request.session["uid"]
            selcart = "SELECT * from cart_tb,order_tb,product_tb WHERE order_tb.o_id ""= cart_tb.o_id and cart_tb.p_id = product_tb.p_id and cart_tb.c_status = ""'Active' and order_tb.u_id = '"+str(userid)+"'" 
            
            # connection create object
            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True)
            #query execute
            mycursor.execute(selcart)
            cart_data = mycursor.fetchall()

            seltotal = "SELECT sum(c_totalprice) from cart_tb,order_tb,product_tb WHERE ""order_tb.o_id = cart_tb.o_id and cart_tb.p_id = product_tb.p_id  and cart_tb.c_status"" = 'Active' and order_tb.u_id = '"+str(userid)+"'" 
            # connection create object
            mydb = getdb()
            mycursor = mydb.cursor()
            #query execute
            mycursor.execute(seltotal)
            total_data = mycursor.fetchall()

            seltotalqty = "SELECT sum(c_quantity) from cart_tb,order_tb,product_tb WHERE ""order_tb.o_id = cart_tb.o_id and cart_tb.p_id = product_tb.p_id and cart_tb.c_status"" = 'Active' and order_tb.u_id = '"+str(userid)+"'" 
            # connection create object
            mydb = getdb()
            mycursor = mydb.cursor()
            #query execute
            mycursor.execute(seltotalqty)
            totalqty_data = mycursor.fetchall()

                    
            alldata = {
            'cart_data' : cart_data,
            'total_data' : total_data,
            'totalqty_data' :totalqty_data
            }
            return render(request,'umycart.html',alldata)

    except NameError:
        print("internal error")
    except:
        print('Error returned')



    try:
        u_id = request.session.get("u_id")
        p_id = request.GET.get("p_id")

        mydb = getdb()
        mycursor = mydb.cursor()

        ins = "INSERT IGNORE INTO wishlist_tb (u_id, p_id) VALUES (%s, %s)"
        mycursor.execute(ins, (u_id, p_id))
        mydb.commit()

        return redirect("uwishlist")

    except Exception as e:
        print("Add Wishlist Error:", e)
        return redirect("home")
    


    try:
        userid = request.session.get("uid")

        # ---------------- ADD TO WISHLIST ----------------
        if request.GET.get("p_id"):
            p_id = request.GET.get("p_id")

            mydb = getdb()
            mycursor = mydb.cursor()

            ins = """
                INSERT IGNORE INTO wishlist_tb (u_id, p_id)
                VALUES (%s, %s)
            """
            mycursor.execute(ins, (userid, p_id))
            mydb.commit()

            return redirect("uwishlist")

        # ---------------- DELETE FROM WISHLIST ----------------
        elif request.GET.get("delete"):
            wid = request.GET.get("delete")

            mydb = getdb()
            mycursor = mydb.cursor()

            delete = "DELETE FROM wishlist_tb WHERE id = %s AND u_id = %s"
            mycursor.execute(delete, (wid, userid))
            mydb.commit()

            return redirect("uwishlist")

        # ---------------- SHOW WISHLIST PRODUCTS ONLY ----------------
        else:
            sel = """
                SELECT *
                FROM wishlist_tb w
                JOIN product_tb p ON w.p_id = p.p_id
                WHERE w.u_id = %s
            """

            mydb = getdb()
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute(sel, (userid,))
            wishlist_data = mycursor.fetchall()

            return render(request, "uwishlist.html", {
                "wishlist_data": wishlist_data
            })

    except Exception as e:
        print("Wishlist Error:", e)
        return redirect("home")


