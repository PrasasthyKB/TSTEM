[elk]
%{for host in elk~}
${host.tags.Name} ansible_host=${host.public_ip} private_ip=${host.private_ip} search_engine_ip=${search_engine[0].private_ip}
%{endfor~}

[es_data]
%{for host in es_data~}
${host.tags.Name} ansible_host=${host.public_ip} private_ip=${host.private_ip}
%{endfor~}

[kafka]
%{for host in kafka~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[web-crawler]
%{for host in web_crawler~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[search-engine]
%{for host in search_engine~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[web-classifier]
%{for host in web_classifier~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[twitter-crawler]
%{for host in twitter_crawler~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[communityfeed-crawler]
%{for host in communityfeed_crawler~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[wikijs]
%{for host in wikijs~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[misp]
%{for host in misp~}
${host.tags.Name} ansible_host=${host.public_ip}
%{endfor~}

[all:vars]
ansible_user=${ansible_user}
ansible_ssh_private_key_file=${ansible_ssh_private_key_file}
