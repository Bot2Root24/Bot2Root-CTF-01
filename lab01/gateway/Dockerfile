FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    openssh-server iptables iproute2 \
    net-tools iputils-ping curl \
    && rm -rf /var/lib/apt/lists/*

RUN echo "root:g4t3w4y_b0t2r00t" | chpasswd

RUN mkdir -p /var/run/sshd
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]
