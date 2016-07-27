from guerrillamail import GuerrillaMailSession, GuerrillaMailClient

session = GuerrillaMailSession()
print session.get_session_state()['email_address']
print session.get_email_list()[0].guid
print session.get_email(1).guid

client = GuerrillaMailClient()
email_data = client.get_email(1)
print email_data.get('mail_from')