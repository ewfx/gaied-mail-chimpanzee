import os, sys
import pdfplumber
import email
from email import policy
import google.generativeai as genai
from bs4 import BeautifulSoup
from email.message import Message
from PIL import Image
import io
import gc
from google.cloud import vision

# Gracefully close gRPC connections
def shutdown_grpc():
    try:
        genai._client = None  # Remove the GenerativeAI client reference
        gc.collect()          # Force garbage collection to clean up gRPC
    except Exception as e:
        print(f"Warning: Error shutting down gRPC - {e}")

SYSTEM_INSTRUCTION = """Please answer the given questions based on the context provided. 
You need to provide the Request type and sub-request type with respect to Wells Fargo, 
understand the context and decide which one is best among the below options:

Request Type:
1. Adjustment - If the amount/currency is being adjusted in form of any transaction.
2. AU Transfer - If there is any change in the branch/AU.
3. Closing Notice - If the email contains any intimation of account closure. 
   Possible sub request types: Reallocation Fees, Amendment Fees, Reallocation Principal.
4. Commitment Change - Possible sub request types: Cashless Roll, Decrease, Increase.
5. Fee Payment - If any fee is being paid. 
   Possible sub request types: Outgoing Fee, Letter of Credit Fee.
6. Money Movement Inbound - If there is any money moving into Wells Fargo.
   Possible sub request types: Inbound, Principal+Interest, Principal+Interest+Fee.
7. Money Movement Outbound - If there is any money moving out from Wells Fargo.
   Possible sub request types: Outbound Timebound, Foreign Currency.

Each email must fall into one of the above request types and sub-request types. 
Decide the best one and provide an answer with an explanation. Return the response in the form of json having 3 key-value pair, keys are request, sub_request, explaination"""

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_image(file_data):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=file_data)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description if texts else ""

def extract_text_from_eml(eml_path):
    with open(eml_path, "r", encoding="utf-8") as f:
        msg = email.message_from_file(f, policy=policy.default)

    email_text = ""
    attachment_text = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            #print(f"content_disposition: {content_disposition}")
            if content_type == "text/plain":
                #print(f"text/plain")
                email_text += part.get_payload(decode=True).decode(errors="ignore")

            elif content_type == "text/html":
                #print(f"text/html")
                html_content = part.get_payload(decode=True).decode(errors="ignore")
                email_text += BeautifulSoup(html_content, "html.parser").get_text()

            elif "attachment" in content_disposition or "inline" in content_disposition:
                #print(f"attachment")
                filename = part.get_filename()
                file_data = part.get_payload(decode=True)

                if filename.lower().endswith(".pdf"):
                    with io.BytesIO(file_data) as pdf_file:
                        with pdfplumber.open(pdf_file) as pdf:
                            for page in pdf.pages:
                                attachment_text += page.extract_text() + "\n"

                elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    attachment_text += extract_text_from_image(file_data) + "\n"

    else:
        email_text = msg.get_payload(decode=True).decode(errors="ignore")

    return email_text.strip(), attachment_text.strip()

def classify_request(file_path):
    # Set up Gemini API
    genai.configure(api_key="AIzaSyCLXWQGONbfKLI12rWYo1mb2LqSM4j8PGc")
    model = genai.GenerativeModel("gemini-2.0-flash")
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        #print(f"pdf content is: {text}")
    elif file_path.endswith(".eml"):
        email_text,attachment_text = extract_text_from_eml(file_path)
        text = f"{email_text}\n{attachment_text}"
    else:
        raise ValueError("Unsupported file format. Only PDF and EML are supported.")
    
    prompt = f"""
    Context:
    {text}
    
    Based on the given system instructions, determine the request type and sub-request type. 
    Provide an explanation for your choice.
    """
    #print(f"prompt is: {prompt}")
    response = model.generate_content([SYSTEM_INSTRUCTION, prompt])
    del model
    return response.text
    #return 'all is well'

# Example usage
#file_path = sys.argv[1].split('/')[-1] # Replace with the actual file path
file_path = sys.argv[1]
result = classify_request(file_path)
print(result)

# Call this at the end
shutdown_grpc()

sys.exit(0)

