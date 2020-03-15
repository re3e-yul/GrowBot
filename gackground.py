#!/usr/bin/env python
import threading
class BackgroundSensors(threading.Thread):

    def __init__(self, function_that_downloads):
        threading.Thread.__init__(self)
        self.runnable = ReadSensors
        self.daemon = True

    def run(self):
        self.runnable()

def ReadSensors():
                global ECs
                global EC
                global pH
                global TDS
                global S
                global SG
                while True:
                        pH = Atlas(99,"r")
                        try:
                                time.sleep(2)
                                ECs = Atlas(100, 'r')
                                ECr = ECs.split(',')
                                EC = ECr[0]
                                TDS = ECr[1]
                                S = ECr[2]
                                SG = ECr[3]
                                pH = Atlas(99,"r")
                        except ValueError:
                                EC = "0"
                                TDS = "0"
                                S = "0"
                                SG = "0"
		printpH, ECs,EC,TDS,S,SG
                return pH, ECs,EC,TDS,S,SG



if __name__ == "__main__":

        thread = BackgroundSensors(ReadSensors)
        thread.start()
