local socket = require("socket")
local app = require("app")

local host = os.getenv("HOST") or "0.0.0.0"
local port = tonumber(os.getenv("PORT") or "3000") or 3000
local server = assert(socket.bind(host, port))

print(string.format("Ping-pong API listening on http://%s:%d", host, port))

while true do
  local client = server:accept()
  client:settimeout(5)

  local request_line = client:receive("*l")
  if request_line then
    local method, target = request_line:match("^(%S+)%s+(%S+)")
    app.write_response(client, app.response_for(method or "", target or "/"))
  end

  client:close()
end
