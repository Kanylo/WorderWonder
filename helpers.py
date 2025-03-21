import os
import mimetypes

def get_file_extension(file_path):
    """Return the file extension for the given file path."""
    return os.path.splitext(file_path)[1].lower()

def get_mime_type(file_path):
    """Determine the MIME type of a file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def format_conversion_message(file_path, output):
    """Format a user-friendly message about the conversion result."""
    file_name = os.path.basename(file_path)
    ext = get_file_extension(file_path)
    
    if "Error" in output:
        return f"Error converting '{file_name}': {output}"
    
    # Extract output file path if it's in the result
    output_lines = output.strip().split("\n")
    output_file = next((line for line in output_lines if line.startswith("Output file:")), "")
    
    if output_file:
        output_file = output_file.replace("Output file:", "").strip()
        return f"Successfully converted '{file_name}' to {os.path.basename(output_file)}"
    
    return f"Converted '{file_name}' ({ext}) successfully. {output}"

def is_valid_file(file_path):
    """Check if the file exists and is a regular file."""
    return os.path.isfile(file_path)