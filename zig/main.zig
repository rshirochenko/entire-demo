const std = @import("std");

const Response = struct {
    status: []const u8,
    body: []const u8,
    allow_get: bool = false,
};

fn responseFor(method: []const u8, target: []const u8, count: *u64, buffer: []u8) !Response {
    const path_end = std.mem.indexOfAny(u8, target, "?#") orelse target.len;
    const path = target[0..path_end];

    if (!std.mem.eql(u8, path, "/ping")) {
        return .{ .status = "404 Not Found", .body = "{\"error\":\"Not Found\"}" };
    }

    if (!std.mem.eql(u8, method, "GET")) {
        return .{
            .status = "405 Method Not Allowed",
            .body = "{\"error\":\"Method Not Allowed\"}",
            .allow_get = true,
        };
    }

    count.* += 1;
    const body = try std.fmt.bufPrint(buffer, "{{\"message\":\"pong\",\"count\":{d}}}", .{count.*});
    return .{ .status = "200 OK", .body = body };
}

fn handleConnection(stream: *std.net.Stream, count: *u64) !void {
    var request_buffer: [4096]u8 = undefined;
    const bytes_read = try stream.read(&request_buffer);
    if (bytes_read == 0) return;

    const request = request_buffer[0..bytes_read];
    const line_end = std.mem.indexOfScalar(u8, request, '\n') orelse return;
    var parts = std.mem.tokenizeScalar(u8, request[0..line_end], ' ');
    const method = parts.next() orelse return;
    const target = parts.next() orelse "/";

    var body_buffer: [128]u8 = undefined;
    const response = try responseFor(method, target, count, &body_buffer);
    var writer = stream.writer();
    try writer.print(
        "HTTP/1.1 {s}\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: {d}\r\n",
        .{ response.status, response.body.len },
    );
    if (response.allow_get) try writer.writeAll("Allow: GET\r\n");
    try writer.writeAll("Connection: close\r\n\r\n");
    try writer.writeAll(response.body);
}

pub fn main() !void {
    const allocator = std.heap.page_allocator;
    var port: u16 = 3000;
    if (std.process.getEnvVarOwned(allocator, "PORT")) |value| {
        defer allocator.free(value);
        port = std.fmt.parseInt(u16, value, 10) catch return error.InvalidPort;
        if (port == 0) return error.InvalidPort;
    } else |_| {}

    const address = try std.net.Address.parseIp4("0.0.0.0", port);
    var server = try address.listen(.{ .reuse_address = true });
    defer server.deinit();

    std.debug.print("Ping-pong API listening on http://0.0.0.0:{d}\n", .{port});
    var pong_count: u64 = 0;
    while (true) {
        var connection = try server.accept();
        defer connection.stream.close();
        handleConnection(&connection.stream, &pong_count) catch |err| {
            std.debug.print("connection error: {}\n", .{err});
        };
    }
}

test "GET /ping returns an incrementing pong count" {
    var count: u64 = 0;
    var buffer: [128]u8 = undefined;
    const first = try responseFor("GET", "/ping", &count, &buffer);

    try std.testing.expectEqualStrings("200 OK", first.status);
    try std.testing.expectEqualStrings("{\"message\":\"pong\",\"count\":1}", first.body);
    try std.testing.expectEqual(@as(u64, 1), count);
}

test "non-GET /ping is rejected without incrementing" {
    var count: u64 = 0;
    var buffer: [128]u8 = undefined;
    const response = try responseFor("POST", "/ping", &count, &buffer);

    try std.testing.expectEqualStrings("405 Method Not Allowed", response.status);
    try std.testing.expect(response.allow_get);
    try std.testing.expectEqual(@as(u64, 0), count);
}

test "unknown routes return not found" {
    var count: u64 = 0;
    var buffer: [128]u8 = undefined;
    const response = try responseFor("GET", "/unknown", &count, &buffer);

    try std.testing.expectEqualStrings("404 Not Found", response.status);
    try std.testing.expectEqual(@as(u64, 0), count);
}
