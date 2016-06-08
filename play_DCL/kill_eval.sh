ps -ef | grep 5000 | grep python | awk '{ print "kill -9 " $2 }' > t
./t
