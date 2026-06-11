<%@ page import="java.io.*" %>
<%
    String status = "running";
    String version = "9.0.83";
    response.setContentType("application/json");
    out.println("{\"status\":\"" + status + "\",\"version\":\"" + version + "\",\"endpoints\":[\"/api/status\",\"/api/deserialize\"]}");
%>
