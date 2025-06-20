@Grab('org.apache.camel:camel-core:3.20.0')
@Grab('org.apache.camel:camel-groovy:3.20.0')
@Grab('org.apache.camel:camel-mail:3.20.0')
@Grab('org.apache.camel:camel-netty-http:3.20.0')
@Grab('org.slf4j:slf4j-simple:1.7.36')

import org.apache.camel.CamelContext
import org.apache.camel.builder.RouteBuilder
import org.apache.camel.impl.DefaultCamelContext
import org.apache.camel.Exchange
import org.apache.camel.Processor
import org.apache.camel.component.mail.MailMessage
import javax.mail.internet.MimeMessage
import javax.mail.internet.MimeMultipart
import javax.mail.internet.MimeBodyPart
import javax.mail.Session
import javax.mail.internet.InternetAddress
import javax.mail.Message
import javax.mail.Transport
import javax.mail.MessagingException
import javax.mail.internet.MimeUtility
import java.nio.file.*
import java.util.zip.ZipInputStream
import java.io.ByteArrayInputStream

// Load environment variables
def env = System.getenv()

def smtpHost = env.getOrDefault('SMTP_HOST', 'mailhog')
def smtpPort = env.getOrDefault('SMTP_PORT', '1025')
def imapHost = env.getOrDefault('IMAP_HOST', 'mailhog')
def imapPort = env.getOrDefault('IMAP_PORT', '1143')
def clientEmail = env.getOrDefault('CLIENT_EMAIL', 'user@local')
def deploymentDir = env.getOrDefault('DEPLOYMENT_DIR', '/app/deployment')

// Create deployment directory if it doesn't exist
new File(deploymentDir).mkdirs()

// Create Camel context
CamelContext context = new DefaultCamelContext()

// Add routes
context.addRoutes(new RouteBuilder() {
    void configure() {
        // Health check endpoint
        from("netty-http:http://0.0.0.0:8080/health")
            .routeId("health-route")
            .transform().constant('{"status": "UP"}')
            .setHeader(Exchange.CONTENT_TYPE, constant('application/json'))

        // Email processing route
        from("imap://${clientEmail}?password=password&delete=false&unseen=true&consumer.delay=10000&debugMode=false&connectionTimeout=10000")
            .routeId("email-processing-route")
            .log("Processing received email")
            .process(new Processor() {
                void process(Exchange exchange) {
                    try {
                        def mailMessage = exchange.getIn().getBody(MailMessage.class)
                        def message = mailMessage.message
                        
                        // Extract email details
                        def subject = message.subject ?: "No Subject"
                        def from = message.from?.first()?.toString() ?: "unknown@example.com"
                        
                        println "Received email from: $from"
                        println "Subject: $subject"
                        
                        // Process attachments
                        processAttachments(message, deploymentDir)
                        
                        // Send acknowledgment
                        sendAcknowledgment(from, "Received: $subject")
                        
                    } catch (Exception e) {
                        println "Error processing email: ${e.message}"
                        e.printStackTrace()
                    }
                }
            })
    }
})

// Process email attachments
void processAttachments(MimeMessage message, String baseDir) {
    try {
        def content = message.content
        
        if (content instanceof MimeMultipart) {
            MimeMultipart mimeMultipart = (MimeMultipart) content
            
            for (int i = 0; i < mimeMultipart.count; i++) {
                def part = mimeMultipart.getBodyPart(i)
                
                // Handle attachments
                if (Part.ATTACHMENT.equalsIgnoreCase(part.disposition) || 
                    part.fileName != null) {
                    
                    def fileName = MimeUtility.decodeText(part.fileName ?: "attachment_${System.currentTimeMillis()}")
                    println "Processing attachment: $fileName"
                    
                    // Create a unique directory for this deployment
                    def timestamp = new Date().format('yyyyMMdd_HHmmss')
                    def appDir = new File("${baseDir}/app_${timestamp}")
                    appDir.mkdirs()
                    
                    // Save the attachment
                    def file = new File(appDir, fileName)
                    part.inputStream.withStream { input ->
                        file.bytes = input.bytes
                    }
                    
                    // If it's a zip file, extract it
                    if (fileName.endsWith('.zip')) {
                        extractZip(file, appDir)
                        file.delete() // Remove the zip file after extraction
                    }
                    
                    // Look for and execute deployment scripts
                    deployApplication(appDir)
                }
            }
        }
    } catch (Exception e) {
        println "Error processing attachments: ${e.message}"
        e.printStackTrace()
    }
}

// Extract zip file
void extractZip(File zipFile, File targetDir) {
    try {
        new ZipInputStream(new FileInputStream(zipFile)).withStream { zipIn ->
            def zipEntry = zipIn.getNextEntry()
            while (zipEntry != null) {
                def filePath = new File(targetDir, zipEntry.name)
                
                if (!zipEntry.isDirectory()) {
                    // Create parent directories if they don't exist
                    filePath.parentFile.mkdirs()
                    
                    // Extract file
                    new FileOutputStream(filePath).withStream { fos ->
                        def bytes = new byte[1024]
                        int length
                        while ((length = zipIn.read(bytes)) >= 0) {
                            fos.write(bytes, 0, length)
                        }
                    }
                } else {
                    // Create directory
                    filePath.mkdirs()
                }
                
                zipIn.closeEntry()
                zipEntry = zipIn.getNextEntry()
            }
        }
        println "Successfully extracted ${zipFile.name} to ${targetDir.absolutePath}"
    } catch (Exception e) {
        println "Error extracting zip file: ${e.message}"
        e.printStackTrace()
    }
}

// Deploy the application
void deployApplication(File appDir) {
    try {
        println "Deploying application from: ${appDir.absolutePath}"
        
        // Look for common deployment files
        def deployScript = null
        
        // Check for common deployment scripts
        ["deploy.sh", "run.sh", "start.sh", "app.py", "app.js", "app.rb", "app.rb"].each { script ->
            def file = new File(appDir, script)
            if (file.exists()) {
                deployScript = file
                return false // break the loop
            }
        }
        
        if (deployScript) {
            println "Found deployment script: ${deployScript.name}"
            
            // Make the script executable if it's a shell script
            if (deployScript.name.endsWith('.sh')) {
                def process = ["chmod", "+x", deployScript.absolutePath].execute()
                process.waitFor()
            }
            
            // Execute the script
            def process = null
            if (deployScript.name.endsWith('.py')) {
                process = ["python3", deployScript.absolutePath].execute(null, appDir)
            } else if (deployScript.name.endsWith('.js')) {
                process = ["node", deployScript.absolutePath].execute(null, appDir)
            } else if (deployScript.name.endsWith('.rb')) {
                process = ["ruby", deployScript.absolutePath].execute(null, appDir)
            } else {
                process = ["/bin/sh", "-c", "./${deployScript.name}"].execute(null, appDir)
            }
            
            // Capture and log output
            def output = new StringBuilder()
            def error = new StringBuilder()
            
            process.consumeProcessOutput(output, error)
            process.waitFor()
            
            println "Deployment output: $output"
            if (error) {
                println "Deployment error: $error"
            }
            
            println "Application deployed successfully with exit code: ${process.exitValue()}"
        } else {
            println "No deployment script found in ${appDir.absolutePath}"
            println "Contents: ${appDir.listFiles()?.collect { it.name }}"
        }
    } catch (Exception e) {
        println "Error deploying application: ${e.message}"
        e.printStackTrace()
    }
}

// Send acknowledgment email
void sendAcknowledgment(String to, String subject) {
    try {
        def session = Session.getDefaultInstance(new Properties())
        def message = new MimeMessage(session)
        
        message.setFrom(new InternetAddress(clientEmail))
        message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to))
        message.setSubject("Acknowledgment: $subject")
        
        def text = """
            Your application has been received and is being processed.
            
            Deployment details:
            - Time: ${new Date()}
            - Status: Processing
            
            You will receive another notification once the deployment is complete.
        """.stripIndent()
        
        message.setText(text)
        
        // Send the message
        Transport.send(message, smtpHost, smtpPort, null, null)
        
        println "Acknowledgment sent to $to"
    } catch (Exception e) {
        println "Failed to send acknowledgment: ${e.message}"
        e.printStackTrace()
    }
}

// Start the Camel context
println "Starting Client Agent..."
println "Email: $clientEmail"
println "Deployment Directory: $deploymentDir"

context.start()

// Keep the JVM running
synchronized(this) {
    this.wait()
}
