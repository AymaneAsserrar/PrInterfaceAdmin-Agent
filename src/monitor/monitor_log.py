import apache_log_parser
import datetime



# Fonction pour analyser une ligne de log
def parser_ligne(ligne):
    line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %b")
    log_parsed =  line_parser(ligne)
    liste_value = [ log_parsed['remote_host'],
                    log_parsed['remote_user'],
                    log_parsed['status'],
                    log_parsed['request_url'],
                    log_parsed['time_received_datetimeobj']]
    print( liste_value)

def parser(log):
    for ligne in log:
        parser_ligne(ligne)



test ='127.0.0.1 - - [09/Jan/2020:10:35:48 +0000] "GET / HTTP/1.1" 200 11229 "-" "Wget/1.19.4 (linux-gnu)"'
parser_ligne(test)