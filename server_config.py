# config variables for server
import os

DEFAULT = [80, 443, 8888, 8889]

TEST = [7080, 7443, 7888, 7889]

SSL = ssl_options_gs = {
        "certfile": os.path.join("/etc/ssl/certs/", "gokosalvager_com.full.crt"),
        "keyfile": os.path.join("/etc/ssl/private/", "key.pem")
    }
    
#    ssl_options_ai = {
#        "certfile": os.path.join("/etc/ssl/certs/", "andrewiannaccone_com.full.crt"),
#        "keyfile": os.path.join("/etc/ssl/private/", "key.pem")
#    }

    