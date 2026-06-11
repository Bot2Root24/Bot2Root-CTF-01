<%@ page import="java.io.*,java.util.*,java.util.Base64" %>
<%
    // Vulnerable Java deserialization endpoint
    // In a real scenario, this would use ObjectInputStream
    // For CTF purposes, this simulates command execution via base64 payload
    
    String data = request.getParameter("data");
    response.setContentType("application/json");
    
    if (data == null || data.isEmpty()) {
        out.println("{\"error\":\"Missing 'data' parameter. Send base64-encoded serialized object.\",\"hint\":\"Try: ?data=<base64_payload>\"}");
        return;
    }
    
    try {
        byte[] decoded = Base64.getDecoder().decode(data);
        String command = new String(decoded);
        
        // Simulate deserialization RCE - execute the decoded command
        // Only allow specific commands for safety
        String[] allowed = {"id", "whoami", "cat /usr/local/tomcat/flag.txt", "ls", "hostname"};
        boolean isAllowed = false;
        for (String a : allowed) {
            if (command.trim().equals(a)) {
                isAllowed = true;
                break;
            }
        }
        
        if (isAllowed) {
            Process p = Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", command});
            BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) sb.append(line).append("\n");
            out.println("{\"status\":\"deserialized\",\"output\":\"" + sb.toString().trim().replace("\"", "\\\"") + "\"}");
        } else {
            out.println("{\"error\":\"Deserialization failed - invalid object format\"}");
        }
    } catch (Exception e) {
        out.println("{\"error\":\"" + e.getMessage() + "\"}");
    }
%>
