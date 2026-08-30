local M = {}

local JSON_CONTENT_TYPE = "application/json; charset=utf-8"

local function response(status_code, reason_phrase, body, allow_get)
  return {
    status_code = status_code,
    reason_phrase = reason_phrase,
    body = body,
    allow_get = allow_get or false,
    content_type = JSON_CONTENT_TYPE,
  }
end

local function query_value(query, key)
  for part in query:gmatch("[^&]+") do
    local name, value = part:match("^([^=]+)=(.*)$")
    if name == key then
      return value
    end
  end
  return nil
end

local function integer(value)
  if value == nil or not value:match("^[+-]?%d+$") then
    return nil
  end
  return tonumber(value)
end

function M.response_for(method, target)
  local path = target:match("^[^?#]*")
  local query = target:match("%?(.*)") or ""
  query = query:match("^[^#]*")
  path = path == "" and "/" or path

  if path == "/ping" then
    if method == "GET" then
      return response(200, "OK", '{"message":"pong"}')
    end
    return response(405, "Method Not Allowed", '{"error":"Method Not Allowed"}', true)
  end

  if path == "/multiply" then
    if method ~= "GET" then
      return response(405, "Method Not Allowed", '{"error":"Method Not Allowed"}', true)
    end

    local a = integer(query_value(query, "a"))
    local b = integer(query_value(query, "b"))
    if a == nil or b == nil then
      return response(400, "Bad Request", '{"error":"a and b must be integers"}')
    end
    return response(200, "OK", string.format('{"result":%g}', a * b))
  end

  return response(404, "Not Found", '{"error":"Not Found"}')
end

function M.write_response(client, result)
  local headers = {
    "HTTP/1.1 " .. result.status_code .. " " .. result.reason_phrase,
    "Content-Type: " .. result.content_type,
    "Content-Length: " .. #result.body,
  }
  if result.allow_get then
    table.insert(headers, "Allow: GET")
  end
  table.insert(headers, "Connection: close")
  client:send(table.concat(headers, "\r\n") .. "\r\n\r\n" .. result.body)
end

return M
