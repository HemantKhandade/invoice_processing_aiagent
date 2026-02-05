import ollama
from pdf2image import convert_from_path
import json
from langchain_core.tools import tool

pdf_file = "./email_attachments/investmentBankInvoiceSample.pdf"
image_file = "./invoice_images/invoice_page.png"
file_path = "./invoice_images/output.json"

def process_invoice(pdf_path):
    # 1. Convert PDF page to image
    #images = convert_from_path(pdf_path)
    poppler_path=r'C:\Users\hvlk3\poppler-25.12.0\Release\Library\bin'
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    # Assuming single page invoice for this example
    image_path = "./invoice_images/invoice_page.png"
    images[0].save(image_path, "PNG")

def extract_invoice_details(image_path):
    # 2. Prompt Llama 3.2-Vision
    prompt = """
    Extract the following details from this invoice image and return them as a JSON object:
    - Invoice Number
    - Date
    - Total Amount
    - Vendor Name
    - Items (Item Name, Quantity, Price)
    Use camel case for the JSON keys.
    Return only valid JSON.
    """
    # 3. Call Ollama
    response = ollama.chat(
        model='llama3.2-vision',
        format='json',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_path]
        }]
    )
    #print(f'response: {total_duration}')
    return response['message']['content']

def save_json_to_file(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Result saved to {file_path}")

def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def read_json_data(json_string):
    # Now you can use 'data' as a regular Python dictionary
    print("File content as a Python dictionary:")
    data = json.loads(json_string)
    print(f"Type of data: {type(data)}")
    print(f"Invoice Number: {data['invoiceNumber']}")
    print(f"Date: {data['date']}")
    print(f"Total Amount: {data['totalAmount']}")
    print(f"Vendor Name: {data['vendor']}")
    print(f"Items: {data['items']}")
    

@tool
def extract_invoice_details_tool():
    """Extract invoice details from a PDF file."""
    process_invoice(pdf_file)
    result = extract_invoice_details(image_file)
    save_json_to_file(result, file_path)
    
invoice_tools = [extract_invoice_details_tool]
invoice_tools_by_name = {tool.name: tool for tool in invoice_tools}
# Run the function
if __name__ == "__main__":
    pdf_file = "./email_attachments/investmentBankInvoiceSample.pdf"
    #process_invoice(pdf_file)
    image_file = "./invoice_images/invoice_page.png"
    #result = extract_invoice_details(image_file)
    # Define the file path
    file_path = "./invoice_images/output.json"
    #save_json_to_file(result, file_path)
    loaded_result = load_json_file(file_path)
    print(loaded_result)
    read_json_data(loaded_result)




