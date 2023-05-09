async function request_sessionkey(filename) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/request_sessionkey', true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                resolve({
                    iv: response.iv,
                    key: response.key
                });
            } if (xhr.status === 500) {
                alert('Error: File not uploaded');
                alert('Re-check your file name on your Profile');
                reject(new Error(`Request failed with status ${xhr.status}`));
            }
        });

        xhr.send(JSON.stringify({ filename: filename }));
    });
}

// Define encrypt_file as a global variable
var encrypt_file;

async function decryptUploadFile() {
    // Get the file input element
    const inputElement = document.querySelector('input[type="file"]');
    if (inputElement.files.length == 0) {
        alert("Please select a file");
        return;
        }
    // Get the selected file and store it in the global variable
    encrypt_file = inputElement.files[0];
    const filename = encrypt_file.name;
    // Create a FileReader to read the file contents
    const encrypt_filereader = new FileReader();
    encrypt_filereader.readAsArrayBuffer(encrypt_file);
    // Get the RSA public and private keys
        
    
    try {

        const { iv, key } = await request_sessionkey(filename);
        var pv_key_file = document.getElementById('pv_key_file');
        if (!pv_key_file) {
            alert('Please select your private key file');
            // create file input element if it does not exist
            pv_key_file = document.createElement('input');
            pv_key_file.type = 'file';
            pv_key_file.id = 'pv_key_file';
            document.body.appendChild(pv_key_file);
        }

        pv_key_file.addEventListener('change',  function () {
            var pv_key_file_reader = new FileReader();
            pv_key_file_reader.onload = async function () {
                var pemString = pv_key_file_reader.result;
                // call RSA decrypt
                const decrypted_iv = rsaDecrypt(iv, pemString);
                const decrypted_key = rsaDecrypt(key, pemString);
                const decrypted_iv_array = decrypted_iv.split(',').map(Number);
                const decrypted_iv_uint8Array = new Uint8Array(decrypted_iv_array);
                const decrypted_key_array = decrypted_key.split(',').map(Number);
                const decrypted_key_uint8Array = new Uint8Array(decrypted_key_array);

                const decrypted = await AESdecrypt(encrypt_filereader.result, decrypted_key_uint8Array, decrypted_iv_uint8Array);
                const decryptedBlob = new Blob([decrypted], { type: encrypt_file.type });
                const decryptedFilename = 'decrypted_' + filename;
                const downloadLink = document.createElement('a');
                downloadLink.href = window.URL.createObjectURL(decryptedBlob);
                downloadLink.download = decryptedFilename;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);

            };

            pv_key_file_reader.readAsText(pv_key_file.files[0]);
        });
        pv_key_file.click();
        pv_key_file.remove();
    }
    catch (error) {
        console.log(error);
    }
}





async function downloadanddecryptionFile(filename) {
    //const filename = 'to-be.png';
    const { iv, key } = await request_sessionkey(filename);
    fetch(`/download_cs_file/${filename}`)
      .then(response => response.blob())
      .then(buffer => {
        const fileBlob = new Blob([buffer], { type: 'image/jpeg' });
        // prepare to encrypt the file
        var pv_key_file = document.getElementById('pv_key_file');
        if (!pv_key_file) {
          alert('Please select your private key file');
          // create file input element if it does not exist
          pv_key_file = document.createElement('input');
          pv_key_file.type = 'file';
          pv_key_file.id = 'pv_key_file';
          document.body.appendChild(pv_key_file);
        }
  
        pv_key_file.addEventListener('change', async function () {
          var pv_key_file_reader = new FileReader();
          pv_key_file_reader.onload = async function () {
            var pemString = pv_key_file_reader.result;
  
            console.log(pemString);
            // call RSA decrypt
            console.log('iv: ' + iv);
            console.log('key: ' + key);
            const decrypted_iv = rsaDecrypt(iv, pemString);
            const decrypted_key = rsaDecrypt(key, pemString);
            console.log('decrypted_iv: ' + decrypted_iv);
            console.log('decrypted_key: ' + decrypted_key);
            const decrypted_iv_array = decrypted_iv.split(',').map(Number);
            const decrypted_iv_uint8Array = new Uint8Array(decrypted_iv_array);
            const decrypted_key_array = decrypted_key.split(',').map(Number);
            const decrypted_key_uint8Array = new Uint8Array(decrypted_key_array);
  
            // call AES decrypt
            const encrypt_filereader = new FileReader();
            encrypt_filereader.onload = async function () {
              const decrypted = await AESdecrypt(
                encrypt_filereader.result,
                decrypted_key_uint8Array,
                decrypted_iv_uint8Array
              );
              const decryptedBlob = new Blob([decrypted], { type: fileBlob.type });
              const decryptedFilename = 'Decrypted_' + filename;
              const downloadLink = document.createElement('a');
              downloadLink.href = window.URL.createObjectURL(decryptedBlob);
              downloadLink.download = decryptedFilename;
              document.body.appendChild(downloadLink);
              downloadLink.click();
              document.body.removeChild(downloadLink);
            };
  
            encrypt_filereader.readAsArrayBuffer(fileBlob);
          };
  
          pv_key_file_reader.readAsText(pv_key_file.files[0]);
        });
  
        pv_key_file.click();
        pv_key_file.remove();
      })
      .catch(error => console.error(error));
  };
  