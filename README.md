**Bill Notifications**

*bill_notifications_account_with_credits.py*

A lambda function that will periodically send you AWS bill notifications to help keep your expenses in check. Blog post for this is [here](https://dev.to/leroykayanda/a-lambda-that-sends-daily-aws-bill-notifications-1dij).


*bill_notifications_account_with_credits.py*

Use this if your account has credits.


**A CICD pipeline for cpanel and other servers**

Automatically build your code and deploy to cpanel via FTP or to other servers via SSH. Blog post for this is [here](https://dev.to/leroykayanda/a-cicd-pipeline-that-pushes-code-to-cpanel-or-any-other-server-via-ftp-or-ssh-36l6).

**Non MFA Login**

A lambda function that sends a slack message to a channel when a user logs in to the AWS console without using MFA. There is also a function to send a message when a the root user logs in.

The IAM policy below can be used to block console and AWS CLI requests that do not use MFA.

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BlockMostAccessUnlessSignedInWithMFA",
                "Effect": "Deny",
                "NotAction": [
                    "iam:CreateVirtualMFADevice",
                    "iam:DeleteVirtualMFADevice",
                    "iam:ListVirtualMFADevices",
                    "iam:EnableMFADevice",
                    "iam:ResyncMFADevice",
                    "iam:ListAccountAliases",
                    "iam:ListUsers",
                    "iam:ListSSHPublicKeys",
                    "iam:ListAccessKeys",
                    "iam:ListServiceSpecificCredentials",
                    "iam:ListMFADevices",
                    "iam:GetAccountSummary",
                    "sts:GetSessionToken"
                ],
                "Resource": "*",
                "Condition": {
                    "BoolIfExists": {
                        "aws:MultiFactorAuthPresent": "false",
                        "aws:ViaAWSService": "false"
                    }
                }
            }
        ]
    }

**Root Login**

A lambda function that sends a slack message to a channel when the root user logs in.

**DB back up script**

This script backs up a postgres database to S3.

To restore the database

    export PGPASSWORD="hdvhdbhdv"
    pg_restore -U <db  user> -h <db  host> -d <db  name>  <name  of  the  backup  file>
