# cyberthreat-bot
CIS Cyberthreat Telegram Bot for Lambda

## Installation

- Create a virtual environment with pipenv
- Create a Telegram bot with @BotFather
- Copy the .template files and customize them for your environment
- Create the DynamoDB table, upload the policy and create the role
- Run lambda deploy, with AWS_PROFILE if needed
- Create daily cronjob on CloudWatch events

## Testing

- If you need to test, run app_env=test lambda invoke
