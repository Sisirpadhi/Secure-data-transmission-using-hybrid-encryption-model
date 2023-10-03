import rsa

print("Generating public/private keys for sender host ...")
print("")

publickey, privatekey = rsa.newkeys(1024)

with open("sender_public.pem", "wb") as f:
    f.write(publickey.save_pkcs1("PEM"))

with open("sender_private.pem", "wb") as f:
    f.write(privatekey.save_pkcs1("PEM"))

print("Successfully generated the RSA pulic/private PEM files for sender\n\n")

print("Generating public/private keys for reciever host ...\n")

publickey, privatekey = rsa.newkeys(1024)

with open("reciever_public.pem", "wb") as f:
    f.write(publickey.save_pkcs1("PEM"))

with open("reciever_private.pem", "wb") as f:
    f.write(privatekey.save_pkcs1("PEM"))

print("Successfully generated the RSA pulic/private PEM files for reciever\n\n")
