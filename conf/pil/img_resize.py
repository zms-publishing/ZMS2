import _imaging
import os, sys
from PIL import Image

def main(argv):

    try:
        if len(argv) < 3:
            raise "CommandLineError"
        
        width = int(argv[0])
        height = int(argv[1])
        infile = argv[2]
        
        try:
          im = Image.open(infile)
          try:
            im.thumbnail((width,height),Image.ANTIALIAS) # im.resize((width,height)) does not work
          except:
            im.thumbnail((width,height)) # im.resize((width,height)) does not work
          im.save(infile)
        except IOError:
          sys.stderr.write("cannot resize image for %s\n" % infile)
          sys.exit(1)
        
    except "CommandLineError":
      usage = """python img_resize.py width height infile\n"""
      sys.stderr.write(usage)
      sys.exit(1)

    
# If called from the command line
if __name__=='__main__': main(sys.argv[1:])

