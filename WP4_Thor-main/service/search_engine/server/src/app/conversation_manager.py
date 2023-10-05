import json
from app.gpt_service import GptService
from app.elastic_service import ElasticService
from app.wazuh_manager import WazuhManager
from app import helper


class ConversationManager:
    def __init__(self):
        gpt_contextual_messages = [
            {"role": "system", "content": '''You are a cyber security agent who is called THOR. You can answer the questions related to cybersecurity and computer security.

In general, user questions will be in one of these categories:
1. General Questions: The user might ask some irrelevant questions to security, such as "How are you?", or "What is the weather". If the user asks general questions, you should ask him/her that you are answering security-related questions. Please put <irrelevant> at the beginning of your response. I will remove this part (as the system) and show the user the rest of your message.

2. CyberSecurity and Computer Security Questions: Feel free to give users as many details as you like.

3. Queries: Besides, we have another cyber security search engine, in which there are a lot of reported IP addresses, file hashes, and malicious email addresses. Users might want to inquire if an IP address is reported in our search engine or not. Users might ask "Show me all the ports 2300 attacks", or "The latest updates through the last 24 hours". the user might ask to block an IP address in his system. In this case, he will ask "Block the ip 127.0.0.1" or something similar. please consider that user queries are different and don't settle for the examples I provided. If you feel that the user request is similar to this category, please provide <query> at the beginning of your message. I will be informed that I should search for this on our search engine.'''}
            # , {"role": "user", "content" : "What is Encription?"}
        ]

        self.gpt = GptService(gpt_contextual_messages)
        server, username, password = helper.get_wazuh_config()
        self.wazuh = WazuhManager(host=server, user=username, password=password)

    def do_asnwer(self, user_input):
        # classified = self.gpt.get_class(user_input)
        result = self.handle_security_request(user_input)
        
        if "<irrelevant>" in result:
            cleaned_message = result.lstrip('<irrelevant> ')
            return cleaned_message

        if "<query>" in result:
            print("Handling Query message")
            result = self.handle_query_request(user_input)
            # result.append("\n")
            # result.append(query_result)

        # if classified == "security":
        #     return self.handle_security_request(user_input)

        # if classified == "general":
        #     self.handle_query_request(user_input)

        return result

    def handle_query_request(self, user_input):
        print("Handling query request")
        gpt_res = self.gpt.send_query_command(user_input)
        es = ElasticService()
        if gpt_res['command'] == "search":
            print("User wants to search")
            if "ip" in gpt_res and len(gpt_res["ip"]) > 0:
                ip = gpt_res['ip'][0]
                if ip == "192.168.1.1": return "I am sorry, but you have not provided any ip address! please include the IoC in your search."
                print(f"Searching for this IP address {ip}")
                result = es.merged_url_search(ip=ip)
                total = result[1]
                if 0 < total:
                    print(f"Found {ip}")
                    record = result[0][0]
                    print(f"Get Results from Elasticsearch for searching {ip}. Number of results: {result[1]}")
                    return f"Yes, this IP was reported on {record.format_first_seen()}"
                else:
                    print(f"Could not find {ip}")
                    return f"I could not find {ip} in the search engine"
            elif "hash" in gpt_res and len(gpt_res["hash"]) > 0:
                hash = gpt_res['hash'][0]
                print(f"Searching for this hash {hash}")
                result = es.api_file_search(hash=hash)
                total = result[1]
                if 0 < total:
                    print(f"Found {hash}")
                    record = result[0][0]
                    print(f"Get Results from Elasticsearch for searching {hash}. Number of results: {result[1]}")
                    return f"Yes, this hash was reported on {record.format_first_seen()}"
                else:
                    print(f"Could not find {hash}")
                    return f"I could not find {hash} in the search engine"
            
            else: # general search, we should present latest update on system
                # todo: create CRON job
                result_twitter = es.merged_url_search(source="twitter")
                result_clear_web = es.merged_url_search(source="clear_web")
                result_dark_web = es.merged_url_search(source="dark_web")
                return(f"Here is the results: There are {result_twitter[1]} urls and ip addresses reported from twitter, {result_clear_web[1]} from Clear Web, {result_dark_web[1]} from Dark Web reported during last 24 hours.")

        if gpt_res['command'] == 'block':
            print("Command: block")
            if "ip" not in gpt_res:
                return "Please give me the IP or email address you want to block."

            if "ip" in gpt_res and len(gpt_res["ip"]) > 0:
                ip = gpt_res["ip"][0]
                print(ip)
                try:
                    self.wazuh.block_ip(ip)
                except Exception as ex:
                    print(ex)
                return f"The IP address {ip} has been blocked! Anything else?"

        return gpt_res

    def handle_security_request(self, user_input):
        return self.gpt.answer_general_questions(user_input)

    def handle_general_request(self, user_input):
        return "Sorry, I cannot answer your general questions!"
