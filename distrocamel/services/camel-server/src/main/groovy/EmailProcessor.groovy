@Grab('org.apache.camel:camel-core:3.20.0')
@Grab('org.apache.camel:camel-groovy:3.20.0')
@Grab('org.apache.camel:camel-mail:3.20.0')
@Grab('org.apache.camel:camel-netty-http:3.20.0')
@Grab('org.apache.camel:camel-jackson:3.20.0')
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
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

// Load environment variables
def env = System.getenv()

def smtpHost = env.getOrDefault('SMTP_HOST', 'mailhog')
def smtpPort = env.getOrDefault('SMTP_PORT', '1025')
def imapHost = env.getOrDefault('IMAP_HOST', 'mailhog')
def imapPort = env.getOrDefault('IMAP_PORT', '1143')
def llmEmail = env.getOrDefault('LLM_EMAIL', 'llm@local')
def clientEmail = env.getOrDefault('CLIENT_EMAIL', 'user@local')

// LLM Service URL (Ollama or other)
def llmServiceUrl = env.getOrDefault('OLLAMA_BASE_URL', 'http://ollama:11434') + "/api/generate"
def llmModel = env.getOrDefault('OLLAMA_MODEL', 'mistral:7b')

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

        // Main email processing route
        from("imap://${llmEmail}?password=password&delete=false&unseen=true&consumer.delay=10000&debugMode=false&connectionTimeout=10000")
            .routeId("email-processing-route")
            .log("Processing email: ${body.subject}")
            .process(new Processor() {
                void process(Exchange exchange) {
                    try {
                        def mailMessage = exchange.getIn().getBody(MailMessage.class)
                        def message = mailMessage.message
                        
                        // Extract email content
                        def subject = message.subject ?: "No Subject"
                        def from = message.from?.first()?.toString() ?: "unknown@example.com"
                        def content = extractTextFromMessage(message)
                        
                        // Log the received email
                        println "Received email from: $from"
                        println "Subject: $subject"
                        println "Content: $content"
                        
                        // Call LLM to generate application
                        def appDescription = "Generate a simple application based on: $content"
                        def generatedApp = callLlm(appDescription)
                        
                        // Create response email with generated app
                        def responseEmail = createResponseEmail(
                            to: from,
                            from: llmEmail,
                            subject: "Re: $subject - Your Generated Application",
                            text: "Here is your generated application. Please find the attached files.",
                            appCode: generatedApp
                        )
                        
                        // Set the response email as the new message
                        exchange.getIn().setBody(responseEmail, String.class)
                        
                    } catch (Exception e) {
                        println "Error processing email: ${e.message}"
                        e.printStackTrace()
                        // Optionally send an error response
                        def errorResponse = createErrorEmail(
                            to: from,
                            from: llmEmail,
                            error: "Failed to process your request: ${e.message}"
                        )
                        exchange.getIn().setBody(errorResponse, String.class)
                    }
                }
            })
            // Send the response email
            .to("smtp://${smtpHost}:${smtpPort}?username=user&password=password&from=${llmEmail}")
            .log("Response email sent successfully")
    }
})

// Helper method to extract text from email message
String extractTextFromMessage(MimeMessage message) throws Exception {
    def content = message.content
    if (content instanceof String) {
        return content
    } else if (content instanceof MimeMultipart) {
        MimeMultipart mimeMultipart = (MimeMultipart) content
        for (int i = 0; i < mimeMultipart.count; i++) {
            def part = mimeMultipart.getBodyPart(i)
            if (part.contentType.startsWith("text/plain")) {
                return part.content
            }
        }
    }
    return "No text content found"
}

// Call LLM to generate application code
String callLlm(String prompt) {
    try {
        def url = new URL(llmServiceUrl)
        def connection = url.openConnection()
        connection.setRequestMethod("POST")
        connection.setRequestProperty("Content-Type", "application/json")
        connection.setDoOutput(true)
        
        def requestBody = [
            model: llmModel,
            prompt: "You are an AI assistant that generates application code. Generate a complete, runnable application based on the following description: $prompt. Include all necessary files and a README with instructions on how to run the application.",
            stream: false
        ]
        
        // Send request
        connection.outputStream.withWriter("UTF-8") { writer ->
            writer << JsonOutput.toJson(requestBody)
        }
        
        // Get response
        def response = new JsonSlurper().parse(connection.inputStream)
        return response.response ?: "Error: No response from LLM"
        
    } catch (Exception e) {
        println "Error calling LLM: ${e.message}"
        e.printStackTrace()
        return "Error generating application: ${e.message}"
    }
}

// Create a response email with the generated application
String createResponseEmail(Map params) {
    def session = Session.getDefaultInstance(new Properties())
    def message = new MimeMessage(session)
    
    message.setFrom(new InternetAddress(params.from))
    message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(params.to))
    message.setSubject(params.subject)
    
    // Create multipart message
    def multipart = new MimeMultipart()
    
    // Add text part
    def textPart = new MimeBodyPart()
    textPart.setText(params.text)
    multipart.addBodyPart(textPart)
    
    // Add application code as attachment
    if (params.appCode) {
        def attachmentPart = new MimeBodyPart()
        attachmentPart.setFileName("generated_app.zip")
        // In a real implementation, you would zip the generated files here
        // For now, we'll just add the code as a text file
        attachmentPart.setText("# Generated Application\n\n${params.appCode}")
        multipart.addBodyPart(attachmentPart)
    }
    
    message.setContent(multipart)
    
    // Return the raw message as string
    ByteArrayOutputStream output = new ByteArrayOutputStream()
    message.writeTo(output)
    return output.toString()
}

// Create an error response email
String createErrorEmail(Map params) {
    def session = Session.getDefaultInstance(new Properties())
    def message = new MimeMessage(session)
    
    message.setFrom(new InternetAddress(params.from))
    message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(params.to))
    message.setSubject("Error Processing Your Request")
    message.setText("""
        We encountered an error while processing your request:
        
        ${params.error}
        
        Please try again later or contact support if the issue persists.
    """.stripIndent())
    
    // Return the raw message as string
    ByteArrayOutputStream output = new ByteArrayOutputStream()
    message.writeTo(output)
    return output.toString()
}

// Start the Camel context
println "Starting Camel context..."
context.start()

// Keep the JVM running
synchronized(this) {
    this.wait()
}
