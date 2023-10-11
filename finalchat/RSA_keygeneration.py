import rsa

print("Generating public/private keys for sender host ...")
print("")

publickey, privatekey = rsa.newkeys(1024)

print("Generating sender_public.pem file\n")
with open("sender_public.pem", "wb") as f:
    f.write(publickey.save_pkcs1("PEM"))

print("Generating sender_private.pem file\n")
with open("sender_private.pem", "wb") as f:
    f.write(privatekey.save_pkcs1("PEM"))

print("Successfully generated the RSA pulic/private PEM files for sender\n\n")

print("Generating public/private keys for reciever host ...\n")

publickey, privatekey = rsa.newkeys(1024)

print("Generating reciever_public.pem file\n")
with open("reciever_public.pem", "wb") as f:
    f.write(publickey.save_pkcs1("PEM"))

print("Generating reciever_private.pem file\n")
with open("reciever_private.pem", "wb") as f:
    f.write(privatekey.save_pkcs1("PEM"))

print("Successfully generated the RSA pulic/private PEM files for reciever\n\n")
