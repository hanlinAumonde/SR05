#!/bin/bash

#nettoyage
nettoyer () {
  # Suppression des processus de l'application app
  killall app 2> /dev/null

  # Suppression des processus de l'application ctl
  killall ctl 2> /dev/null

  # Suppression des processus tee et cat
  killall tee 2> /dev/null
  killall cat 2> /dev/null

  # Suppression des tubes nommés
  rm -f /tmp/in* /tmp/out*
}
nettoyer

# Create named pipes
mkfifo /tmp/in_A1 /tmp/out_A1 /tmp/in_C1 /tmp/out_C1
mkfifo /tmp/in_A2 /tmp/out_A2 /tmp/in_C2 /tmp/out_C2
mkfifo /tmp/in_A3 /tmp/out_A3 /tmp/in_C3 /tmp/out_C3

# Start the applications
python3 app.py -n A1 -p 0 -N 3 < /tmp/in_A1 > /tmp/out_A1 &
python3 ctl.py -n C1 -N 3 -p 0 -i 1 < /tmp/in_C1 > /tmp/out_C1 &

python3 app.py -n A2 -p 0 -N 3 < /tmp/in_A2 > /tmp/out_A2 &
python3 ctl.py -n C2 -N 3 -p 0 -i 2 < /tmp/in_C2 > /tmp/out_C2 &

python3 app.py -n A3 -p 0 -N 3 < /tmp/in_A3 > /tmp/out_A3 &
python3 ctl.py -n C3 -N 3 -p 0 -i 3 < /tmp/in_C3 > /tmp/out_C3 &

# Connect the applications
cat /tmp/out_A1 > /tmp/in_C1 &
cat /tmp/out_C1 | tee /tmp/in_A1 | tee /tmp/in_C2 > /tmp/in_C3 &

cat /tmp/out_A2 > /tmp/in_C2 &
cat /tmp/out_C2 | tee /tmp/in_A2 | tee /tmp/in_C3 > /tmp/in_C1 &

cat /tmp/out_A3 > /tmp/in_C3 &
cat /tmp/out_C3 | tee /tmp/in_A3 | tee /tmp/in_C1 > /tmp/in_C2 &

echo "+ INT QUIT TERM => nettoyer"
trap nettoyer INT QUIT TERM
exit 0
