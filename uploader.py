import requests
import json
import re
import sys, getopt

url = 'http://127.0.0.1:8666/api/upload'

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hf:",["help", "file="])
    except getopt.GetoptError:
        print 'uploader.py -f <FILE>'
        sys.exit(2)
    inputfile = None
    for opt, arg in opts:
        if opt == '-h':
            print 'uploader.py -f <FILE>'
            sys.exit()
        elif opt in ("-f", "--file"):
            inputfile = arg
            file = {'file': open(inputfile, 'rb')}
            r = requests.post(url, files=file)
            c = json.loads(r.text)
            x = c[0]

            exists = ['exists']
            for pattern in exists:
                if re.search(pattern, str(c)):
                    z = x['url']
                    print 'File exists: ' + z

            success = ['success']
            for pattern in success:
                if re.search(pattern, str(c)):
                    z = x['url']
                    print 'File uploaded: ' + z


if __name__ == "__main__":
    main(sys.argv[1:])
