print('init.lua ver 1.2')
wifi.setmode(wifi.STATION)
print('set mode=STATION (mode='..wifi.getmode()..')')
print('MAC: ',wifi.sta.getmac())
print('chip: ',node.chipid())
print('heap: ',node.heap())
-- wifi config start
wifi.sta.config("xxx","yyy")
-- wifi config end

guitar = require 'guitar'
s = net.createConnection(net.UDP, 0) s:connect(2000, '192.168.0.22')
prev = ''
tmr.alarm(0, 10, tmr.ALARM_AUTO, function() local res = guitar.read() if res ~= prev then s:send(guitar.read()) prev = res end end)
