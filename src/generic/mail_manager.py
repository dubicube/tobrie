import imaplib
import base64
import email
import smtplib, ssl
from urllib.parse import unquote

class MailManager:
    email_user = ""
    email_pass = ""
    M = None
    mail_ids = []

    def __init__(self, a, p):
        self.email_user = a
        self.email_pass = p

    def getAllMails(self):
        self._fetchMails()
        m = [self._getMail(i) for i in self.mail_ids]
        self._close()
        return m

    def _fetchMails(self):
        self.M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        self.M.login(self.email_user, self.email_pass)
        self.M.select()
        typ, data = self.M.search(None, 'UNSEEN')#ALL
        self.mail_ids = data[0].split()
        self.cursor = 0
    def _close(self):
        self.M.close()
        self.M.logout()
    def _getMail(self, num):
        typ, data = self.M.fetch(num, '(RFC822)')
        mail = data[0][1].decode('utf-8')
        mail = self._getMailText(mail)
        return mail
    def _getMailText_aux(self, mail):
        lines = mail.split('\n')
        i = 0
        r = ["", "", "", "", ""]
        while i < len(lines):
            if lines[i].startswith("From: ") and r[0] == "":
                r[0] = lines[i][6:-1]
            if lines[i].startswith("To: ") and r[1] == "":
                r[1] = lines[i][4:-1]
            if lines[i].startswith("Subject: ") and r[3] == "":
                r[3] = lines[i][9:-1]
            if lines[i].startswith("CC: ") and r[4] == "":
                r[4] = lines[i][4:-1]
            if lines[i][:-1] == "Content-Type: text/plain; charset=\"UTF-8\"":
                boundary = lines[i-1]
                i+=1
                conv64 = lines[i][:-1] == "Content-Transfer-Encoding: base64"
                i+=1
                while lines[i]!=boundary:
                    line = ""
                    if conv64 and len(lines[i][:-1])%4==0:
                        line = base64.b64decode(lines[i][:-1]).decode('utf-8')
                    else:
                        line = lines[i][:-1]+"\n"
                    if line[0] != '>':
                        r[2]+=line
                    i+=1
                    #if '@' in lines[i]:
                    #    return r
                return r
            i+=1
        return r
    def _getMailText(self, mail):
        mail = self._getMailText_aux(mail)
        mail[2] = unquote(mail[2].replace('=\n', '').replace('=', '%'))
        return mail

    def removeSelfAddress(self, liste):
        # Remove self address to avoid loopback
        i=0
        while i<len(liste):
            if self.email_user in liste[i]:
                del liste[i]
            else:
                i+=1
        return ",".join(liste)
    def getAddressesToReply(self, mail):
        addr = self.removeSelfAddress((mail[0]+","+mail[1]).split(','))
        addr_cc = self.removeSelfAddress(mail[4].split(','))
        return [addr, addr_cc]

    def send_email(self, receiver_email, cc_emails, subject, message):
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(self.email_user, self.email_pass)
            message = "From: "+self.email_user+"\r\n"+"To: "+receiver_email+"\r\n"+"CC: "+cc_emails+"\r\n"+"Subject: "+subject+"\r\n\r\n"+message
            server.sendmail(self.email_user, receiver_email.split(',')+cc_emails.split(','), message.encode('utf-8'))

# Example:
#mail_manager = MailManager("brenda.tobrie@gmail.com", "password")
#m = mail_manager.getAllMails()
#print(m)
#if len(m)!=0:
#    print(mail_manager.getAddressesToReply(m[0]))
#mail_manager.send_email('email_custom@babaorum.com', 'brenda.tobrie@gmail.com', "Ooooobjet", "Message à la con avec des accents de mort\nééàààèè&%$£")
