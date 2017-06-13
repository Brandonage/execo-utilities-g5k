from twilio.rest import Client

def create_twilio_client():
    try:
        with open('twilio.txt','r') as myfile:
            twilio_credentials = myfile.read().split(";")
        client = Client(twilio_credentials[0],twilio_credentials[1])
        dest_phone=twilio_credentials[2]
        orig_phone=twilio_credentials[3]
        return client, dest_phone, orig_phone
    except IOError:
        print "Couldn't find twilio credentials. No text messages will be sent"