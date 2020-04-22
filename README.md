CS50 Web Programming Final Project

This is still a shopping website developed in Python-Flask, Javascript and SQL.

Customers can buy items, add multiple addresses to their account, view all orders and cancel their order.

Site administrators can access the admin page at "/admin" route using the username and password set in environment variables - ADMIN_USERNAME and ADMIN_PASSWORD. See "envs.py"

All environment variables are in a file - "envs.py". The site uses AWS S3 bucket to store product images. AWS bucket has a public get object bucket policy.

AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required in order to store and modify product images. Use aws configure to set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
Envoironment variables in envs.py - 
s3_BUCKET = "bucketname"
s3_BUCKET_URL = "https://bucketname.s3-us-west-2.amazonaws.com/"
This must be the bucket policy for reference.
Bucket policy for ublic viewing can be generated at https://awspolicygen.s3.amazonaws.com/policygen.html
{
    "Version": "2012-10-17",
    "Id": "Policy1586922930261",
    "Statement": [
        {
            "Sid": "Stmt1586922924765",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::bucketname/*"
        }
    ]
}


Site also uses websockets to update new orders and order cancellation requests to administrator. Similarly, customers also get live updates on their order status.

Steps to Deploy:

Run: pip3 install -r requirements.txt
Create an s3 bucket in AWS.
Add up the bucket policy.
Set up a database
Set all environment variables in envs.py
Run: python3 create.py

Customers must register and login in order to place their orders. For that, a verification email is sent to customers. Email server is "smtp-mail.outlook.com", hence ADMIN_EMAIL_ADDRESS in "envs.py" must be a microsoft account.

code is at https://github.com/parijatsrivastava/final
site is deployed at https://paris-myshop.herokuapp.com/
admin page can be accessed at https://paris-myshop.herokuapp.com/admin