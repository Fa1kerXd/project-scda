import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from app_path import EMAIL_ATTACHMENT_FILE


 
 
def base_email(addrfrom, addrto, subject):
    msg = MIMEMultipart()
    msg['From'] = addrfrom
    msg['To'] = addrto
    msg['Subject'] = subject
    return msg
 
 
def open_server(sender, recipient, password, msg: MIMEMultipart):
    try:
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            text = msg.as_string()
            server.sendmail(sender, recipient, text)
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f'Email ou senha incorretos!: {e}')
        return False
 
 
def send_email(to_email, from_email, subject, password_email, body, send=False,
                attachment_path=EMAIL_ATTACHMENT_FILE, filename=None):
    if not send:
        return False
 
    msg = base_email(from_email, to_email, subject)
    msg.attach(MIMEText(body, 'plain'))
 
    with open(attachment_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
 
    safe_filename = Path(filename or attachment_path).name
    part.add_header('Content-Disposition', f'attachment; filename="{safe_filename}"')
    msg.attach(part)
 
    if not open_server(from_email, to_email, password_email, msg=msg):
        raise smtplib.SMTPAuthenticationError(1, "Falha ao autenticar no servidor de e-mail")
 
    return True


# if __name__ == '__main__':
#     send_email(
#         to_email='coordenador@org.com.br',
#         from_email='analista@org.com.br',
#         subject='Correcao de apontamento',
#         password_email='SENHA_AQUI',
#         body='Teste',
#         send=True
#     )























































# import smtplib
# from pathlib import Path
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# BASE = Path(__file__).parent
# FILE_ROOT = BASE / 'aut_email.txt'
# def base_email(addrfrom, addrto, subject):
#     msg = MIMEMultipart()
#     msg['From'] = addrfrom
#     msg['To'] = addrto
#     msg['Subject'] = subject
#     return msg

# def open_server(sender, recipient, password, msg: MIMEMultipart):
#     try:
#         with smtplib.SMTP('smtp.office365.com', 587) as server:
#             server.starttls()
#             server.login(sender, password)
#             text = msg.as_string()
#             server.sendmail(sender, recipient, text)
#             server.quit()
#             return True
#     except smtplib.SMTPAuthenticationError as e:
#         print(f'email ou senha incorretos!: {e}')
#         return False


# def send_email(to_email, from_email, subject, password_email, body, send=False, filename='aut_email.txt'):
#     if send:
#         msg = base_email(to_email, from_email, subject)
#         msg.attach(MIMEText(body, 'plain'))

#         with open(FILE_ROOT, 'rb') as attachment:
#             part = MIMEBase('application', 'octet-stream')
#             part.set_payload(attachment.read())
#         encoders.encode_base64(part)
#         part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
#         msg.attach(part)

#         if not open_server(to_email, from_email, password_email, msg=msg):
#             raise smtplib.SMTPException()
#         send = True
#         return send

# if __name__ == '__main__':
#     send_email('acsilva@vilma.com.br', 'acsilva@vilma.com.br', 'Correção de apontamento', 'Cafe2024', 'Teste', True)