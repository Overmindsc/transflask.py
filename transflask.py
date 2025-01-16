from flask import Flask, request, render_template_string
import base64
import re

app = Flask(__name__)

def text2base64(s):
    return base64.b64encode(s.encode('utf-8')).decode()

def base642text(b):
    return base64.b64decode(b.encode('utf-8')).decode()

def hexa2base64(h):
    return base64.b64encode(bytes.fromhex(h)).decode()

def base642hex(b):
    return base64.b64decode(b).hex()

def binary2text(s):
    s = s.replace(" ", "")
    if len(s) % 8 != 0:
        raise ValueError("Invalid binary length. Must be a multiple of 8.")
    byte_data = bytes(int(s[i * 8:i * 8 + 8], 2) for i in range(len(s) // 8))
    return byte_data.decode('utf-8')
    


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None

    if request.method == 'POST':
        input_language = request.form.get('input_language').lower()
        output_language = request.form.get('output_language').lower()
        user_input = request.form.get('user_input')

        try:
            if input_language == "unicode":
                if output_language == "base64":
                    result = text2base64(user_input)
                elif output_language == "hexa":
                    nospace = user_input.encode('utf-8').hex()
                    result = ' '.join(nospace[i:i+2] for i in range(0, len(nospace), 2))
                elif output_language == "binary":
                    result = ' '.join(format(ord(x), '08b') for x in user_input)

            elif input_language == "hexa":
                user_input = user_input.replace(" ", "")
                if re.search("[^0-9a-fA-F]", user_input):
                    error = "Forbidden characters detected in hexadecimal input."
                else:
                    user_input = user_input.replace(" ", "")
                    if output_language == "unicode":
                        result = ''.join(chr(int(user_input[i:i+2], 16)) for i in range(0, len(user_input), 2))
                    elif output_language == "base64":
                        result = hexa2base64(user_input)
                    elif output_language == "binary":
                        heytest = bin(int(user_input, 16))[2:]
                        result = ' '.join(heytest[i:i+8] for i in range(0, len(heytest), 8))

            elif input_language == "base64":
                if output_language == "unicode":
                    result = base642text(user_input)
                elif output_language == "hexa":
                    nospace = base642hex(user_input)
                    result = ' '.join(nospace[i:i+2] for i in range(0, len(nospace), 2))
                elif output_language == "binary":
                    result = ' '.join(format(x, '08b') for x in base64.b64decode(user_input))

            elif input_language == "binary":
                user_input = user_input.replace(" ", "")
                if re.search("[^0-1]", user_input):
                    error = "Forbidden characters detected in binary input."
                else:
                    if output_language == "base64":
                        result = text2base64(binary2text(user_input))
                    elif output_language == "hexa":
                        nospace = binary2text(user_input).encode('utf-8').hex()
                        result = ' '.join(nospace[i:i+2] for i in range(0, len(nospace), 2))
                    elif output_language == "unicode":
                        result = binary2text(user_input)

            else:
                error = "Invalid input language or output language selection."
        except Exception as e:
            error = str(e)

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Language Converter</title>
    </head>
    <body>
        <h1>Language Converter</h1>
        <form method="post">
            <label>Input Language:</label>
            <select name="input_language">
                <option value="unicode" {% if request.form.get('input_language') == 'unicode' %}selected{% endif %}>Unicode</option>
                <option value="hexa" {% if request.form.get('input_language') == 'hexa' %}selected{% endif %}>Hexadecimal</option>
                <option value="base64" {% if request.form.get('input_language') == 'base64' %}selected{% endif %}>Base64</option>
                <option value="binary" {% if request.form.get('input_language') == 'binary' %}selected{% endif %}>Binary</option>
            </select><br><br>

            <label>Output Language:</label>
            <select name="output_language">
                <option value="base64" {% if request.form.get('output_language') == 'base64' %}selected{% endif %}>Base64</option>
                <option value="hexa" {% if request.form.get('output_language') == 'hexa' %}selected{% endif %}>Hexadecimal</option>
                <option value="unicode" {% if request.form.get('output_language') == 'unicode' %}selected{% endif %}>Unicode</option>
                <option value="binary" {% if request.form.get('output_language') == 'binary' %}selected{% endif %}>Binary</option>
            </select><br><br>


            <label>Input:</label><br>
            <textarea name="user_input" rows="4" cols="50"></textarea><br><br>

            <input type="submit" value="Convert">
        </form>

        {% if result %}
            <h2>Result:</h2>
            <p>{{ result }}</p>
        {% endif %}

        {% if error %}
            <h2>Error:</h2>
            <p style="color: red;">{{ error }}</p>
        {% endif %}
    </body>
    </html>
    """

    return render_template_string(template, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
