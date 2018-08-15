# Reference Summary

## Message Format

Sorry, due to limited time,  I can't offer a document about the message format sent between each function. (Input and Output of each function)

But I have logged it for each function. So you could always command below to view it. 

```sh
$ docker service logs -f [function-name]
```

like： 

```sh
$ docker service logs -f slack-event-webhook-slack
$ docker service logs -f query-dialogflow-slack
```

For messages from Slack and Dialogflow, you could check links sub-parts below to learn the meaning of each field.

## [OpenFaaS](https://www.openfaas.com/)

### Repo

- [faas](https://github.com/openfaas/faas)
- [faas-cli](https://github.com/openfaas/faas-cli)

###Doc / Guide

- [Docs](https://docs.openfaas.com/)
- [Guide Collections](https://github.com/openfaas/faas/tree/master/guide)
- [Workshop - Hands-on Labs](https://github.com/openfaas/workshop)
- [Secret](https://github.com/openfaas/docs/blob/master/docs/reference/secrets.md)

### Troubleshooting

- [**troubleshooting**](https://github.com/openfaas/faas/blob/master/guide/troubleshooting.md)

## [Slack](https://slack.com/)

- [Building Bots](https://api.slack.com/bot-users)
- [Events API](https://api.slack.com/bot-users#app-mentions-response) 
- [Intro to Messages](https://api.slack.com/docs/messages)
- [Interactive messages](https://api.slack.com/interactive-messages)
- [Bot Post Messages](https://api.slack.com/methods/chat.postMessage)

## [Dialogflow](https://dialogflow.com/) 

### [Docs](https://dialogflow.com/docs/getting-started)

- [Intents](https://dialogflow.com/docs/intents)
- [Entities](https://dialogflow.com/docs/entities)
- [Actions & Parameters](https://dialogflow.com/docs/actions-and-parameters)
- [Contexts](https://dialogflow.com/docs/contexts)
- [Fulfillment](https://dialogflow.com/docs/fulfillment)
- [V1 API Reference](https://dialogflow.com/docs/reference/agent),
- [V1 API /query](https://dialogflow.com/docs/reference/agent/query)
- [System Entities](https://dialogflow.com/docs/reference/system-entities)

### Other

- [Client Access  Token vs Developer Access Token](https://miningbusinessdata.com/api-ai-client-access-token-vs-developer-access-token/)
- [Dialogflow vs Rasa NLU](https://stackoverflow.com/questions/47388497/what-is-the-difference-between-dialogflow-bot-framework-vs-rasa-nlu-bot-framewor/47393191#47393191)
- [如何基于Google Dialogflow创建一个语音对话技能？](https://time.geekbang.org/article/7167)
- [Google Home + OpenFaaS — Write your own voice-controlled functions](https://medium.com/@burtonr/google-home-openfaas-write-your-own-voice-controlled-functions-11f195398e3f)
- [Understanding the Differences Between Alexa, API.ai, WIT.ai, and LUIS/Cortana](https://medium.com/@abraham.kang/understanding-the-differences-between-alexa-api-ai-wit-ai-and-luis-cortana-2404ece0977c)

## Chatbot

- [Github-Topics/personal-assistant](https://github.com/topics/personal-assistant)
- [fendouai/Awesome-Chatbot](https://github.com/fendouai/Awesome-Chatbot)
- [JStumpp/awesome-chatbots](https://github.com/JStumpp/awesome-chatbots)
- [GetStoryline/awesome-bots](https://github.com/GetStoryline/awesome-bots)

