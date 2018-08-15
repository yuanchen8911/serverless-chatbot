# Code Part

This is the code part of FaaS Bot.

For how to use these functions, check `Guides/Bot Build & Run Guide` `Part2`

## Dependencies

Install use `tig_faas_bot/requirements.txt`, `pymongo`, `Eve`, `requests` is all you needed directly for the whole code part. 

```sh
$ pip install -r requirements.txt
```

## File Descriptions

```
├── Bot_Secrets
├── Dialogflow_File
├── Eve_MongoDB
├── FaaS_Functions
├── Product_Info
├── Utility
└── requirements.txt
```

### `Bot_Secrets`

Token for Dialogflow and Slack.
### `Dialogflow_File`

Pre-built Dialogflow Agent.

### `Eve_MongoDB`

Service that connects MongoDB and offers REST interface.

### `FaaS_Functions`
All FaaS function code.

### `Product_Info`

Information about Product used in Bot. 

### `Utility`

Utilities used in functions.

### `requirements.txt`

Python dependency file.