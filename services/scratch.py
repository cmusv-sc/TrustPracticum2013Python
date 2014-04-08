import time
import BaseHTTPServer
import cgi
import ujson
import json
import requests
import re

HOST_NAME = 'einstein.sv.cmu.edu' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9002 # Maybe set this to 9000.
APPSERVER_URL = 'http://einstein.sv.cmu.edu:9000/addSensorReading'


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Title goes here.</title></head>")
        s.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        s.wfile.write("</body></html>")
    def do_POST(self):
#        form = cgi.FieldStorage(
#            fp=self.rfile, 
#            headers=self.headers,
#            environ={'REQUEST_METHOD':'POST',
#                     'CONTENT_TYPE':self.headers['Content-Type'],
#                 })
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        print post_body
#        post_body = ujson.loads(post_body)
#        headers = {'Content-Type': 'application/json'}
#        data_json = ujson.dumps(post_body)
#        data_json = re.sub('timeStamp','timestamp',data_json)

#        if re.search('23420ca4e4830bee',data_json) is not None:
#            print data_json
#            r = requests.post(APPSERVER_URL, data=data_json, headers=headers, timeout=10)

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
