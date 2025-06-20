#!/bin/bash

PROJECT_DIR="emllm-system"

echo "🛠 Tworzenie systemu EMLLM z lokalnym serverem email i Mistral Code 7B..."

mkdir -p $PROJECT_DIR/{email-server,ollama-server,camel-server/src/main/groovy,client-agent/src/main/groovy}

########################
# docker-compose.yml
########################
cat > $PROJECT_DIR/docker-compose.yml <<EOF
version: '3.8'
services:
  email-server:
    build: ./email-server
    ports:
      - "1025:1025"     # SMTP unsecure
      - "143:143"       # IMAP
    volumes:
      - maildata:/var/mail

  ollama:
    image: ghcr.io/ollama/ollama:latest
    command: ["server"]
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama

  camel-server:
    build: ./camel-server
    depends_on:
      - email-server
      - ollama

  client-agent:
    build: ./client-agent
    depends_on:
      - email-server

volumes:
  maildata:
  ollama-models:
EOF

########################
# Email server (Postfix+Dovecot)
########################
cat > $PROJECT_DIR/email-server/Dockerfile <<EOF
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y postfix dovecot-imapd
COPY postfix_main.cf /etc/postfix/main.cf
COPY dovecot.conf /etc/dovecot/dovecot.conf
RUN postmap /etc/postfix/virtual
CMD service postfix start && service dovecot start && tail -f /var/log/mail.log
EOF

cat > $PROJECT_DIR/email-server/postfix_main.cf <<EOF
myhostname = mail.local
mydestination = \$myhostname, localhost
virtual_mailbox_domains = local
virtual_mailbox_base = /var/mail
virtual_mailbox_maps = hash:/etc/postfix/virtual
virtual_minimum_uid = 100
virtual_uid_maps = static:1000
virtual_gid_maps = static:1000
virtual_transport = lmtp:unix:private/dovecot-lmtp
smtpd_tls_security_level = may
smtpd_recipient_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination
EOF

cat > $PROJECT_DIR/email-server/postfix_main.cf <<EOF
user@local    user@local
llm@local     llm@local
EOF

cat > $PROJECT_DIR/email-server/dovecot.conf <<EOF
protocols = imap lmtp
mail_location = maildir:/var/mail/%u
userdb { driver = static; args = uid=1000 gid=1000 home=/var/mail/%u }
passdb { driver = pam; }
service lmtp { unix_listener /var/spool/postfix/private/dovecot-lmtp {mode = 0600; user = postfix; group = postfix;} }
EOF

########################
# Camel Server + Integration z Ollama
########################
cat > $PROJECT_DIR/camel-server/Dockerfile <<EOF
FROM groovy:4.0
WORKDIR /camel
COPY src /camel/src
RUN mkdir -p /camel/lib
CMD ["groovy", "-cp", "/camel/lib/*", "src/main/groovy/EmailRouter.groovy"]
EOF

cat > $PROJECT_DIR/camel-server/src/main/groovy/EmailRouter.groovy <<'EOF'
@Grab('org.apache.camel:camel-core:3.21.0')
@Grab('org.apache.camel:camel-mail:3.21.0')
import org.apache.camel.builder.RouteBuilder
import org.apache.camel.impl.DefaultCamelContext
import java.util.Base64
def ctx = new DefaultCamelContext()
ctx.addRoutes(new RouteBuilder() {
    void configure() {
        from('imaps://user@local@email-server:143?username=llm@local&password=llm&delete=false&consumer.delay=5000')
            .filter { it.in.getHeader("Subject")?.startsWith("text2app") }
            .process {
                def prompt = it.in.body.toString().trim()
                def resp = "curl -s -X POST http://ollama:11434/run/mistral-code-7b -d '{\"prompt\":\"${prompt}\",\"temperature\":0.7}'"
                def appCode = new ProcessBuilder("bash","-c",resp).redirectErrorStream(true).start().text
                def eml = buildMultipart(prompt, appCode)
                it.out.body = eml
                it.out.headers['To'] = it.in.headers['From']
                it.out.headers['Subject'] = "Your App"
            }
            .to('smtps://llm@local@email-server:1025?username=llm@local&password=llm')
    }

    static String buildMultipart(String prompt, String code) {
        def zipData = Base64.encoder.encodeToString(code.getBytes())
        return """From: llm@local
To: user@local
Subject: Your App
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="EMLLM"

--EMLLM
Content-Type: text/plain; charset="UTF-8"

Twoja aplikacja wygenerowana z promptu: "${prompt}"

--EMLLM
Content-Type: application/zip; name="app.zip"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="app.zip"

${zipData}
--EMLLM--"""
    }
})
ctx.start()
Thread.sleep(Long.MAX_VALUE)
EOF

########################
# Client Agent
########################
cat > $PROJECT_DIR/client-agent/Dockerfile <<EOF
FROM groovy:4.0
WORKDIR /client
COPY src /client/src
CMD ["groovy", "src/main/groovy/DeployRouter.groovy"]
EOF

cat > $PROJECT_DIR/client-agent/src/main/groovy/DeployRouter.groovy <<'EOF'
@Grab('org.apache.camel:camel-core:3.21.0')
@Grab('org.apache.camel:camel-mail:3.21.0')
import org.apache.camel.builder.RouteBuilder
import org.apache.camel.impl.DefaultCamelContext
import java.util.Base64
def ctx = new DefaultCamelContext()
ctx.addRoutes(new RouteBuilder() {
    void configure() {
        from('imaps://user@local@email-server:143?username=user@local&password=user&delete=false&consumer.delay=5000')
            .filter { it.in.headers["Subject"]?.startsWith("Your App") }
            .process {
                def body = it.in.body.toString()
                def matcher = (body =~ /Content-Transfer-Encoding: base64\s+([A-Za-z0-9+\/=\r\n]+)--EMLLM--/)
                def base64 = matcher[0][1].replaceAll("\\s+","")
                def zipBytes = Base64.decoder.decode(base64)
                new File("/tmp/app.zip").bytes = zipBytes
                ['unzip','-o','/tmp/app.zip','-d','/opt/emllm/app'].execute().waitFor()
                ['bash','/opt/emllm/app/run.sh'].execute().waitFor()
            }
    }
})
ctx.start()
Thread.sleep(Long.MAX_VALUE)
EOF

echo "✅ Gotowy projekt EMLLM w $PROJECT_DIR"
echo "🔧 Uruchom: cd $PROJECT_DIR && docker-compose up --build"
