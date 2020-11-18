import requests
import json
import logging
LOG = logging.getLogger("obu")

class teltonikaRUT9x:
    def __init__(self,url,username="root",password=""):
        """Makes an teltonikaRUT9x object to read JSON_RPC from the RUT9x mobile router.
        
        Parameters
        ----------
        url : string
            URL to router
        username : string
            username to log into the router, default: root
        password : string
            Password for username, default: ""
        """

        self._url = url
        payload = { 
            "jsonrpc": "2.0", 
            "id": 1, 
            "method": "call", 
            "params": [ 
                "00000000000000000000000000000000", 
                "session", 
                "login",
                    {"username": "", "password": "", "timeout": 0 } 
                    ] 
                }
        payload["params"][3]["username"] = username
        payload["params"][3]["password"] = password
        LOG.info("Request JSON-RPC session ID from router")
        response = requests.post(self._url, json=payload)
        #print(response.text)
        r = response.json()
        self._sessionId = r["result"][1]["ubus_rpc_session"]
  
    def readSignalStrength(self):
        """
        Reads the RSRP, SINR and RSRQ from the RUT9x 

        Returns
        -------
            dict: with RSRP, SINR and RSPQ.
        """

        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "call", "params":
            [ 
                "",
                "file",
                "exec",
                {
                    "command":"gsmctl",
                    "params":["-WZM" ]
                }
            ]
            }
        payload["params"][0] = self._sessionId
        payload = json.dumps(payload)
        #print(payload)
        r = requests.post(self._url,data=payload).json()
        #print(r.text)
        stdout = r["result"][1]["stdout"].split("\n")
        #print(stdout)
        result = {
            "RSRP" : "",
            "SINR" : "",
            "RSRQ" : ""
            }
        i = 0
        for x in result:
            result[x] = stdout[i]
            i += 1
        #print(result)
        LOG.info(result)
        return result

    def readGPS(self):
        """ Reads the latitude and longitude

        Returns
        -------
        dict:
            a dict with the latitude and longitude        
        """

        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "call", "params":
            [ 
                "",
                "file",
                "exec",
                {
                    "command":"gpsctl",
                    "params":["-ix" ]
                }
            ]
            }
        payload["params"][0] = self._sessionId
        payload = json.dumps(payload)
        #print(payload)
        r = requests.post(self._url,data=payload).json()
        #print(r.text)
        stdout = r["result"][1]["stdout"].split("\n")
        #print(stdout)
        result = {
            "Lat" : "",
            "Lon" : ""
            }
        i = 0
        for x in result:
            result[x] = stdout[i]
            i += 1
        #print(result)
        LOG.info(result)
        return result
        