# This script runs a listener on the server. It loads a machine learning model from a file. It then reads
# some test data, and makes a prediciton.
# Listen for incoming requests. This comes from a socket request.
# Data needs to be 228 floating point numbers, seperated by commas (no whitespace)
# e.g. "-0.097657,-0.068578,-0.065569,-0.071737,-0.077938,-0.08244,-0.081585,-0.071182,-0.056991,-0.041888,-0.033788,-0.025694,-0.020879,-0.017964,-0.017337,-0.015771,-0.014087,-0.010784,-0.011806,-0.008835,-0.00842,-0.005162,-0.004218,-0.002731,-0.001307,0.001381,0.002795,0.005116,0.00608,0.007526,0.00785,0.00963,0.009461,0.010489,0.011447,0.011534,0.010616,0.011248,0.00987,0.0089,0.008878,0.008562,0.006618,0.005957,0.006645,0.004936,0.003616,0.002573,0.000978,0.001189,0.00053,-0.000871,-0.000171,-0.000536,-0.001192,-0.00149,-0.001872,-0.003204,-0.003866,-0.002586,-0.002182,-0.001138,0.00037,0.001909,0.002338,0.004292,0.004389,0.00514,0.005821,0.004804,0.005547,0.007176,0.007902,0.008155,0.010711,0.012909,0.013234,0.015413,0.016986,0.017247,0.018692,0.018822,0.016636,0.014509,0.012981,0.011102,0.007442,0.004917,0.003922,0.000569,-0.000935,-0.003789,-0.006086,-0.007349,-0.00645,-0.007272,-0.006588,-0.007189,-0.006711,-0.007559,-0.00738,-0.007608,-0.008372,-0.00745,-0.006614,-0.006875,-0.006601,-0.005999,-0.004771,-0.004492,-0.003465,-0.002354,-0.001148,0.000461,0.002015,0.003499,0.006105,0.007674,0.010189,0.011423,0.012906,0.014335,0.015763,0.017506,0.020352,0.023843,0.024843,0.027593,0.028819,0.03221,0.035916,0.040718,0.046646,0.053451,0.059492,0.067458,0.07552,0.083848,0.089829,0.096491,0.105092,0.108913,0.113693,0.117733,0.118138,0.120274,0.1224,0.124786,0.127113,0.127722,0.130313,0.131118,0.130962,0.131566,0.130793,0.130574,0.128423,0.128353,0.126997,0.124077,0.123458,0.122395,0.11905,0.11621,0.115377,0.114021,0.113551,0.11294,0.111525,0.112517,0.113,0.114696,0.115312,0.117795,0.11862,0.121176,0.122472,0.122953,0.125062,0.126158,0.126875,0.129065,0.129026,0.130325,0.130069,0.130907,0.12957,0.130118,0.128781,0.130206,0.12918,0.129423,0.128561,0.128041,0.127329,0.130681,0.128765,0.128203,0.133424,0.130272,0.133343,0.131148,0.13065,0.13047,0.133656,0.131657,0.132822,0.130121,0.135063,0.135115,0.13978,0.143531,0.148926,0.157011,0.167923,0.190163,0.220659,0.241351,0.260513,0.265153,0.272636,0.280147,0.302518,0.291088,0.287712,0.306441,0.289525,0.275613"
# To test this, in the terminal, you can type: echo "the_string_above" | nc localhost 6011

import socket
import sys
import os
import shutil
import numpy as np
import pandas as pd
import scipy.signal
from sklearn.preprocessing import scale
import pickle
import time
from _thread import *
from io import StringIO
from os.path import dirname
import datetime

# get path of the current script
this_dir = os.path.realpath(__file__)
parent_dir = dirname(this_dir)

# Set working directory
os.chdir(os.path.join(parent_dir, 'model'))

# Load the model
filename = 'finalized_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))
print("model loaded")

globvar = 0
#####################################################################################
#####################################################################################
#####################################################################################

HOST = 'nirs.cis.unimelb.edu.au'  # Symbolic name, meaning all available interfaces
PORT = 10100  # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')


# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')

# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))

    # Receiving data from client
    buff = StringIO()          # Create the buffer
    while True:
        data = conn.recv(1024)
        buff.write(data.decode())                    # Append that segment to the buffer
        if '\n' in data.decode(): break              # If that segment had '\n', break
    
    # Get the buffer data, split it over newlines, print the first line
    bufferdata = buff.getvalue().splitlines()[0]
    #print(bufferdata)
    data = StringIO(bufferdata)
    #print(data)
    t1 = time.time()

    try:

        # The request has arrived. We reformat the data into a dataframe.
        print("hello")
        df = pd.read_table(data, sep=",", header=None)

        df = pd.to_numeric(df.iloc[0])
        # apply smoothing filter and svn filter
        # filtered <- filter(sgolay(p=3, n=11, m=0),absorbance)
        filtered = scipy.signal.savgol_filter(df, window_length=11, polyorder=3)

        # filtered <- scale(t(filtered),center=TRUE)
        filtered = scale(np.transpose(filtered))

        # Access the attribute 'scaled:center'
        # filtered <- attr(filtered,"scaled:center")
        # features <- c(filtered,diff(filtered))
        # filtered = filtered.reshape(1,228)
        # print(filtered.shape)
        # print(np.diff(filtered).shape)
        features = np.concatenate([filtered, np.diff(filtered)])
        # make the data frame
        df = pd.DataFrame(data=features).transpose()
        # Now make the prediciton using our model file and the incoming data.
        prediction = loaded_model.predict(df)[0]

        probability = round(np.amax(loaded_model.predict_proba(df)), 3)

        reply = prediction + " " + str(probability) + '\n'


    except:
        reply = "Data not in expected format!\n"

    conn.sendall(reply.encode())
    print("test time:", time.time() - t1, "s")
    
    # infinite loop so that function do not terminate and thread do not end.
    #while True:
    # Receiving data from client
    print("accept again")
    feedback = conn.recv(1024)
    #print(feedback)
    feedback = feedback.decode()
    #print(feedback)
    if feedback == "Yes\n":
        print("Correct prediction.")
        right_name = prediction
        print(right_name)
        right_name = right_name[:1].upper() + right_name[1:]
        nametime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S_")
        name = right_name+"O1"+nametime+".csv"
        # Set working directory
        os.chdir(os.path.join(parent_dir, 'temporary'))
        
        f = open(name,'w')
        l = conn.recv(1024)
        while (l):
            print("Receiving...")
            l = str(l, errors='ignore')
            f.write(l)
            l = conn.recv(1024)
        f.close()
        print("Done Receiving")
    elif feedback == "No\n":
        print("Wrong prediction!")
        # Save the file to local and increment the count with 1
        right_name = conn.recv(1024)
        print(right_name)
        right_name = right_name.decode()
        right_name = right_name[:1].upper() + right_name[1:]
        nametime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S_")
        name = right_name+"O1"+nametime+".csv"
        # Set working directory
        os.chdir(os.path.join(parent_dir, 'temporary'))
        
        f = open(name,'w')
        l = conn.recv(1024)
        while (l):
            print("Receiving...")
            l = str(l, errors='ignore')
            f.write(l)
            l = conn.recv(1024)
        f.close()
        print("Done Receiving")
        
        
        
        #np.savetxt(name, bufferdata, newline=',')
        path = os.path.join(parent_dir, 'temporary')
        globvar = globvar + 1
        print("number of wrong predictions in the temporary folder is",globvar)
        if globvar == 3:
            destination = os.path.join(parent_dir, 'data_20180506')
            for filename in os.listdir(path):
                src = os.path.join(path, filename)
                dst = os.path.join(destination, filename)
                shutil.move(src,dst)
            globvar = 0
            # Set working directory
            os.chdir(parent_dir)
            os.system("python3 train_model.py")
            # Set working directory
            os.chdir(os.path.join(parent_dir, 'model'))
            
            # Load the model
            filename = 'finalized_model.sav'
            loaded_model = pickle.load(open(filename, 'rb'))
            print("model loaded")
        
    conn.close()

s.close()
