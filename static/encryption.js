
async function encryptAndUploadFile() {
  
    // Get the file input element
    const inputElement = document.querySelector('input[type="file"]');
    // Get the selected file
    if(inputElement.files.length == 0) {
      alert("Please select a file");
      return;
  
    }
    else{
      encryptAndUploadFile_call_progress()
    }
    const file = inputElement.files[0];
    // Create a FileReader to read the file contents
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);
    // Get the RSA public and private keys
    const { pbkey,pvkey } = await request_public_key();
    
    // Add the onload function as an event listener for the FileReader
    reader.addEventListener('load', async function(event) {
      
      const key = crypto.getRandomValues(new Uint8Array(32)); 
      const iv = crypto.getRandomValues(new Uint8Array(16)); 
  
      console.log(iv)
  
      const encrypted = await AESencrypt(event.target.result, key, iv); // Encrypt the file
      const encrypt_iv = await rsaEncrypt(iv, pbkey); // Encrypt the IV with RSA public key
      const encrypt_key = await rsaEncrypt(key, pbkey); // Encrypt the AES key with RSA public key
      const formData = new FormData(); // Create a FormData object to upload the file
      formData.append('file', new Blob([encrypted], { type: file.type }), file.name); // Append the encrypted file to the form data
      formData.append('iv', encrypt_iv); // Append the encrypted IV to the form data
      formData.append('key', encrypt_key); // Append the encrypted AES key to the form data
      console.log("encrypt_iv: " + encrypt_iv);
      await fetch('/upload_AESencrypted_file', { method: 'POST', body: formData }); // Upload the file to the server
      
  
    });
  }
  
  async function encryptAndUploadFile_call() {
    await encryptAndUploadFile();
  }
  
  
  
  
  
  // Encrypt a data with AES-CBC using a given key and IV
  async function AESencrypt(data, key, iv) {
    const algorithm = { name: 'AES-CBC', iv: iv };
    const cryptoKey = await crypto.subtle.importKey('raw', key, algorithm, false, ['encrypt']);
    const encrypted = await crypto.subtle.encrypt(algorithm, cryptoKey, data);
    return new Uint8Array(encrypted);
  }
  
  
  
  async function AESdecrypt(data, key, iv) {
    const ivBytes = new Uint8Array(iv);
    const keyBytes = new Uint8Array(key);
    const dataBytes = new Uint8Array(data);
    const algorithm = { name: 'AES-CBC', iv: ivBytes };
    const cryptoKey = await crypto.subtle.importKey('raw', keyBytes, algorithm, false, ['decrypt']);
    const decrypted = await crypto.subtle.decrypt(algorithm, cryptoKey, dataBytes);
    return new Uint8Array(decrypted);
  }
  
  
  
  // Convert an ArrayBuffer to a Base64-encoded string
  function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }
  
  
  
  