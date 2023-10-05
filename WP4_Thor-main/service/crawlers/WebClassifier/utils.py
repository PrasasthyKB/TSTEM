import ipaddress
import itertools
from urllib.parse import urlparse
import PyTorchnerPredicition
import iocextract
import nltk
nltk.download('punkt')



def get_unique_iocs(iocs):
    unique_iocs_set = set()
    unique_iocs_list = []
    for record in iocs:
        if record['value'] not in unique_iocs_set:
            unique_iocs_set.add(record['value'])
            unique_iocs_list.append(record)
    return unique_iocs_list


def extract_iocs(text, crawled_url):
    iocs = []
    ner_instance = PyTorchnerPredicition.load()
    IOC_list = ner_instance.ner_predict(text)

    # Extract hashes
    for hash_ in iocextract.extract_hashes(text):

        hash_type = 'Hash_Misc'
        if len(hash_) == 32:
            hash_type = "Hash_MD5"
        elif len(hash_) == 40:
            hash_type = "Hash_SHA1"
        elif len(hash_) == 64:
            hash_type = "Hash_SHA256"
        elif len(hash_) == 128:
            hash_type = "Hash_SHA512"
        if hash_ in IOC_list:
           iocs.append({"type":"hash","sub_type": hash_type, "value": hash_})

    # Extract YARA rules
    for yara in iocextract.extract_yara_rules(text):
        if yara in IOC_list:
           iocs.append({"type":"yara","value": yara})

    # Extract emails
    emails = []
    for email in iocextract.extract_emails(text, refang=True):
        if email in IOC_list:
           iocs.append({"type":"email","value": email})

    # Extract IPs
    ips = []
    for ip_addr in iocextract.extract_ips(text):

        # Skip if ip is not defanged
        if ip_addr == iocextract.refang_ipv4(ip_addr):
            continue
        ip_addr = iocextract.refang_ipv4(ip_addr)
        if ip_addr in IOC_list:
            ip_addr.replace('[', '').replace(']', '').split(
                '/')[0].split(':')[0].split(' ')[0]
            try:
                ip_addr = ipaddress.IPv4Address(ip_addr)
                ip_ver = "ip_v4"
            except ValueError:
                try:
                    ip_addr = ipaddress.IPv6Address(ip_addr)
                    ip_ver = "ip_v6"
                except ValueError:
                    print(f"ip {ip_addr} format not recognized!")
                    continue
            iocs.append({"type":"ip","sub_type": ip_ver, "value": str(ip_addr)})

    # Extract URLs
    urls = itertools.chain(
        iocextract.extract_unencoded_urls(text),
        iocextract.extract_encoded_urls(text, refang=True),
    )
    for url in urls:
        if url in IOC_list:
            # Skip if url is not defanged
            if url == iocextract.refang_url(url):
                continue
            url = iocextract.refang_url(url)
            possible_ip = urlparse(url).netloc.split(':')[0].replace(
                '[', '').replace(']', '').replace(',', '.')
    
            # Skip if url is ip
            try:
                ipaddress.IPv4Address(possible_ip)
                continue
            except ValueError:
                try:
                    ipaddress.IPv6Address(possible_ip)
                    continue
                except ValueError:
                    pass
    
            try:
                url_domain = urlparse(url).netloc.split(':')[0]
            # Trouble parsing url, just skip
            except ValueError:
                continue
            # Skip if url is in the same domain as current page
            if url_domain == urlparse(crawled_url).netloc:
                print(f"Found url with same domain: {url}")
                continue
            iocs.append({"type":"url","meta":{"url_domain": url_domain}, "value": url})

    # Remove duplicates
    iocs = get_unique_iocs(iocs)

    return iocs