## Why using Fine-tuning
In the implementation of Thor-Hunt-Pro, we have leveraged GPT models to parse user requests, breaking them down into more manageable and identifiable elements that our Python Core System can recognize. Multiple fine-tuned models have been employed to discern the user's intentions effectively. Currently, two primary models are being utilized, although it is important to note that this selection might evolve over time.

### Classification with gpt model
Upon receiving a user request, we feed the input into the corresponding classification model. The primary role of this classification model is to identify the user's input and assign it to one of three classes: "query," "security," or "general." To provide a clearer understanding, here are some examples:

| Input | Class |
| -- | -- |
| I want to search for an IP address 123.123.34.45 | query |
| When this email ABC@DEGG.COM has been reported? | query |
| What is mac address in my computer | security |
| How can I notice phishing pages in my email? | security |
| How is the weather today | general |
| What color do you like the most | general |

### Extracting User Queries
Now, passing the first step of parsing user request (Classifying the input), we have a general idea of what user is looking for. If user request is in the class _query_ we have to extract some key elements and match them with the other parameters. It is time that our another fine-tuned model will come to the game. This model will extract some key elements from user query. Here you can see some of the queries and respective models that gpt generates:

| Input | GPT Output |
| -- | -- |
| What information was stored in the database 6 days | { 'command': 'search', 'from-date': '6 day' } |
| The latest updates on Twitter | { 'command': 'search', 'sources': ['Twitter'] } |

## Search

I want to search for an IP address 123.123.34.45.
I want to search for an IP address 123.123.34.45 on 27th of June.
Is this ip address reported in your database? 123.123.45.56
show me the reported attacks through this port for last week.
Is this IP subnet reported 123.123.*.*

Is this email reported to the database abc@abc.com
I have received a malicious email from abc@abc.com. Is it reported to the database?
Is there any email similar to abc@abc.com in your database
Is the hash abcd435 existed in the elasticsearch database

### time in search
When this email has been reported?

## Block
Please block that IP address
Please block this IP 123.123.34.45 if it existed in the database.
see if you have this IP 123.123.34.45, and then please block that.

## Statistics
I want to know the latest email addresses reported in the database
Give me the statistics
Give me what you have in database
The statistics of the reported IoCs
The latest updates through last 24 hours
The latest updates through last week
Give me what is stored in database through last week

## Sequential memory (search)

Is this ip reported 123.123.34.45? -> Block that
Is this Ip address 123.123.34.45 in community feed -> How about clear web -> please 

5. Tiers
The latest updates in Twitter.
The latest updates in Clear Web
The latest updates in Dark Web
The latest updates in Community Feeds. => block them


# Data structure

Json format of the output:
```
{
    "command": "search",
    "metadata": {
        "sources": ["twitter", "community feed"],
        "date-from": "25-05-2023T12:00:00",
        "date-to": "25-05-2023T12:00:00",
        "type": "ip",
        "phrase": "123.123.23.34"
    }
}
```

## Bad responses from fine-tune model
- Find the latest emails -> { 'command': 'search', 'sources': ['email'] }
- Find the latest ip addresses -> { 'command': 'search', 'ip': ['192.168.0.0'] }

## Responses we should get from the agent
| Type | User Request | Agent Response |
| - | -- | -- |
|Search| Find the latest emails | We have found 300 emails during last 3 days. Do you want to see them? |
|Search| Find the latest ip addresses| I found 200 ip addresses. Do you want to see them?|
|Search| The latest updates on Twitter | Here is the latest updates on twitter. 140 Ip addresses, 200 email addresses, and 100 hash reported|
|Block| Block the ip 123.234.45.56 | The ip 123.234.45.56 is blocked |
