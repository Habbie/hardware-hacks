local pinSCL=1
local pinSDA=2
local function read_reg(dev_addr)  i2c.start(0)  i2c.address(0, dev_addr , i2c.RECEIVER)  c=i2c.read(0,6)  i2c.stop(0)  return c end
local function write_reg(dev_addr,...)   i2c.start(0)  i2c.address(0, dev_addr, i2c.TRANSMITTER)   i2c.write(0,...)  i2c.stop(0)   end
function hexdump(s) for i=1,#s do uart.write(0, string.format('%02x ', string.byte(s, i))) end  print() end

local M={}

function M.init()
  write_reg(0x52, 0xf0, 0x55)
  write_reg(0x52, 0xfb, 0x00)
end

function M.readID()
  write_reg(0x52, 0xfa)
  return read_reg(0x52)
end

function M.read()
  write_reg(0x52, 0x00)
  local res = read_reg(0x52)
  if res == string.char(0xff, 0xff, 0xff, 0xff, 0xff, 0xff) then
    M.init()
    write_reg(0x52, 0x00)
    res = read_reg(0x52)
  end
  return res
end

i2c.setup(0,pinSDA, pinSCL,i2c.SLOW)

return M
