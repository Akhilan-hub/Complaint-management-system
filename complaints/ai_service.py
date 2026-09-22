import os
import json
import logging
from PIL import Image

logger = logging.getLogger(__name__)

def _parse_ai_response(text_content):
    """
    Parses JSON output from Gemini response, cleaning code blocks if present.
    Fallback to line-by-line parsing if JSON decoding fails.
    """
    cleaned = text_content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove ```json and closing ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        
    try:
        data = json.loads(cleaned)
        status = str(data.get("status", "UNCERTAIN")).upper()
        if status not in ["PASS", "FAIL", "UNCERTAIN"]:
            status = "UNCERTAIN"
        reason = data.get("reason", "Verification processed.")
        return status, reason
    except Exception as e:
        logger.warning(f"Failed to parse JSON AI response: {e}. Raw text: {text_content}")
        # Fallback text search
        upper_text = text_content.upper()
        if "PASS" in upper_text:
            return "PASS", text_content.strip()
        elif "FAIL" in upper_text:
            return "FAIL", text_content.strip()
        return "UNCERTAIN", text_content.strip() or "Verification uncertain."

def verify_complaint(title, description, image_path):
    """
    First AI Verification: Checks whether complaint image matches title and description.
    Returns tuple: (status, reason) where status is 'PASS', 'FAIL', or 'UNCERTAIN'.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "UNCERTAIN",
            "Gemini API key is not configured in environment (.env). Defaulting to UNCERTAIN for manual admin review."
        )

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        if not os.path.exists(image_path):
            return "FAIL", "Complaint image file path does not exist."

        img = Image.open(image_path)

        prompt = f"""
You are an AI verification assistant for a public Complaint Management System.
Analyze the uploaded image along with the complaint title and description.

Complaint Title: {title}
Complaint Description: {description}

Evaluate whether the uploaded image reasonably relates to and supports the reported complaint.
- Return "PASS" if the image clearly matches or supports the complaint issue.
- Return "FAIL" if the image is completely unrelated, fake, spam, or nonsense.
- Return "UNCERTAIN" if the image is ambiguous, blurry, or partially unclear.

Respond ONLY with a valid JSON object in this format:
{{
  "status": "PASS",
  "reason": "1-2 sentence explanation"
}}
"""

        # Try gemini-2.5-flash model first, fallback to gemini-2.0-flash or gemini-1.5-flash
        models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3-flash-preview"]
        response = None
        last_err = None

        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[img, prompt]
                )
                if response and response.text:
                    break
            except Exception as err:
                last_err = err
                continue

        if response and response.text:
            return _parse_ai_response(response.text)
        else:
            return "UNCERTAIN", f"AI service error: {last_err or 'No response from model'}"

    except Exception as e:
        logger.error(f"Error calling Gemini API for complaint verification: {e}")
        return "UNCERTAIN", f"AI verification encountered an error: {str(e)}"

def verify_resolution(title, description, original_image_path, resolution_description, resolution_image_path):
    """
    Second AI Verification: Checks whether resolution evidence visually supports that the complaint was resolved.
    Returns tuple: (status, reason) where status is 'PASS', 'FAIL', or 'UNCERTAIN'.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "UNCERTAIN",
            "Gemini API key is not configured in environment (.env). Defaulting to UNCERTAIN for manual admin review."
        )

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        contents = []
        
        # Load original image if available
        if original_image_path and os.path.exists(original_image_path):
            orig_img = Image.open(original_image_path)
            contents.append("Original Complaint Image:")
            contents.append(orig_img)

        # Load resolution evidence image if available
        if resolution_image_path and os.path.exists(resolution_image_path):
            res_img = Image.open(resolution_image_path)
            contents.append("Admin Resolution Evidence Image:")
            contents.append(res_img)

        prompt = f"""
You are an AI verification assistant for a Complaint Management System.
Evaluate whether the admin's resolution evidence image and description demonstrate that the original complaint has been resolved.

Original Complaint Title: {title}
Original Complaint Description: {description}

Admin Resolution Description: {resolution_description}

Instructions:
Compare the original complaint and its image with the admin's resolution description and resolution evidence image.
Determine if the resolution evidence provides reasonable visual support that the specific complaint was addressed or resolved.
- Return "PASS" if the resolution image and description reasonably show the reported problem has been resolved.
- Return "FAIL" if the resolution image clearly fails to show resolution or is completely unrelated.
- Return "UNCERTAIN" if evidence is inconclusive, ambiguous, or lacks clear context.

Respond ONLY with a valid JSON object in this format:
{{
  "status": "PASS",
  "reason": "1-2 sentence explanation of your evaluation."
}}
"""
        contents.append(prompt)

        models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3-flash-preview"]
        response = None
        last_err = None

        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )
                if response and response.text:
                    break
            except Exception as err:
                last_err = err
                continue

        if response and response.text:
            return _parse_ai_response(response.text)
        else:
            return "UNCERTAIN", f"AI service error: {last_err or 'No response from model'}"

    except Exception as e:
        logger.error(f"Error calling Gemini API for resolution verification: {e}")
        return "UNCERTAIN", f"AI resolution verification encountered an error: {str(e)}"
