The code connects to an SMTP server and uses an extended HELO command (EHLO) to see if the server supports a TLS connection  
If it does it then connects using TLS and authenticates with the username and password  
The email DATA is constructed using the MIME format  
Encryption/decryption and attachments are completely optional  
