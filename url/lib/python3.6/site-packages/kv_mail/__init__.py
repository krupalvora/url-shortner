import smtplib 
def mail(sender,password,receiver,subject,body):
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.ehlo()
        s.starttls() 
        s.login(sender,password) 
        tm='Subject:'+subject +'\n\n'+body
        s.sendmail(sender,receiver,tm) 
        s.quit()
    except smtplib.SMTPAuthenticationError:
        print("The username and/or password you entered is incorrect \nOR \nsmtplib.SMTPAuthenticationError:security issue visit and enable less secure app https://myaccount.google.com/lesssecureapps")

    except :
        print('internet not found') 
