# Reading a key from *.key.txt

def readKey(filename):
    key = None
    try:
        f = open(filename, "r")
        contents = f.read()
        if (contents == ''):
            raise
        else:
            key = contents
    except:
        print("Please paste your API key in '" + filename + "' file")
        f = open(filename, "w")
    f.close()
    return key