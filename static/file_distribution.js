var count = 0;

function addInput() {
  var inputFields = document.getElementById("inputFields");
  var newInput = document.createElement("input");
  newInput.type = "text";
  newInput.name = "text";
  newInput.classList.add("input");
  newInput.placeholder = "Input Username.";

  inputFields.appendChild(newInput);
  count++;
  if (inputFields.getElementsByTagName("input").length > 5) {
    removeInput();
  }
}

function removeInput() {
  var inputFields = document.getElementById("inputFields");
  var inputs = inputFields.getElementsByTagName("input");

  if (inputs.length > 1) {
    inputFields.removeChild(inputs[inputs.length - 1]);
    count--;
  }
}

async function submitForm() {
  const formData = new FormData();

  // Add text input values to the FormData object
  var textInputs = document.getElementsByName("text");
  if (textInputs.length == 0) {
    alert("Please input at least one username.");
    return;
  }
  for (var i = 0; i < textInputs.length; i++) {
    formData.append(textInputs[i].name, textInputs[i].value);
  }

  // Add file input to the FormData object
  const file_input = document.getElementById("fileInput");
  

  if (file_input.files.length > 0) {
    console.log("file_input.files.length > 0");
    const file = file_input.files[0];
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);
    // Get the RSA public and private keys
    const { pbkey } = await request_public_key();

    // Add the onload function as an event listener for the FileReader
    reader.addEventListener('load', async function (event) {

      const key = crypto.getRandomValues(new Uint8Array(32));
      const iv = crypto.getRandomValues(new Uint8Array(16));

      console.log(iv)

      const encrypted = await AESencrypt(event.target.result, key, iv); // Encrypt the file
      const encrypt_iv = await rsaEncrypt(iv, pbkey); // Encrypt the IV with RSA public key
      const encrypt_key = await rsaEncrypt(key, pbkey); // Encrypt the AES key with RSA public key
      // Create a FormData object to upload the file
      formData.append('file', new Blob([encrypted], { type: file.type }), file.name); // Append the encrypted file to the form data
      formData.append('iv', encrypt_iv); // Append the encrypted IV to the form data
      formData.append('key', encrypt_key); // Append the encrypted AES key to the form data
      await fetch('/distribute_key', { method: 'POST', body: formData });
    });

  }
  
   
  
}


