FROM tomcat:9-jdk11

# Remove default webapps
RUN rm -rf /usr/local/tomcat/webapps/*

# Create a vulnerable webapp with Java deserialization
COPY webapp/ /usr/local/tomcat/webapps/ROOT/

# Create flag
RUN echo "FLAG{b2r_java_deserialization_8f1c}" > /usr/local/tomcat/flag.txt

# Add ysoserial for deserialization testing
RUN mkdir -p /opt/tools

COPY server.xml /usr/local/tomcat/conf/server.xml

EXPOSE 8443

CMD ["catalina.sh", "run"]
