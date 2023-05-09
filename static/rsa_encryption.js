async function request_public_key() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/request_pb_key', false);
    xhr.send();
    
    if (xhr.status === 200) {
      var response = JSON.parse(xhr.response);
      return {
        pbkey: response.pbkey,
      };
    } else {
      throw new Error('Request failed. Returned status of ' + xhr.status);
    }
  }

//


function rsaEncrypt(plaintext,pbkey ) {
  const publicKey = forge.pki.publicKeyFromPem(pbkey);
  const ciphertext = publicKey.encrypt(forge.util.encodeUtf8(plaintext), 'RSA-OAEP');
  return forge.util.encode64(ciphertext);
}

// Decrypt data using RSA private key
function rsaDecrypt(ciphertext,privateKeyPem) {
  const privateKey = forge.pki.privateKeyFromPem(privateKeyPem);
  const rawCiphertext = forge.util.decode64(ciphertext);
  const plaintext = privateKey.decrypt(rawCiphertext, 'RSA-OAEP');
  return forge.util.decodeUtf8(plaintext);
}


