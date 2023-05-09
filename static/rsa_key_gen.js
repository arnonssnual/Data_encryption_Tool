function generateKeyPair(username) {
    const keySizeSelect = document.getElementById('keySize');
    const keySize = parseInt(keySizeSelect.value);
    const keys = forge.pki.rsa.generateKeyPair({ bits: keySize });
    const publicKey = forge.pki.publicKeyToPem(keys.publicKey);
    const privateKey = forge.pki.privateKeyToPem(keys.privateKey);
    document.getElementById("public-key").value = publicKey;
    document.getElementById("private-key").value = privateKey;

    const fileText = `${privateKey}`;
    const derBlob = new Blob([fileText], { type: 'application/pkcs8' });

    const url = URL.createObjectURL(derBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'privateKey_' + username + '.pem';

    const container = document.getElementById('download-container');

    if (container.childElementCount > 0) {
        // If the container already has a child element, update its text content
        const button = container.querySelector('button');
        const span = button.querySelector('span');
        span.textContent = 'Download Private Key';
    } else {
        // create new button and span elements and add to container
        const button = document.createElement('button');
        button.setAttribute('type', 'submit');
        button.setAttribute('class', 'uiverse-btn');
        const span = document.createElement('span');
        span.textContent = 'Download Private Key';
        button.appendChild(span);
        button.addEventListener('click', () => {
            link.click();
        });
        container.appendChild(button);
    }
}




function rsa_submit() {
    const keySize = document.getElementById("keySize").value;
    const username = document.getElementById("username");
    const username_def = username.textContent.replace('User, ', '').replace('!', '');
    const k_value = document.getElementById("public-key").value.toString();
    //const url_route = `/rsapbkeysubmit/${username_def}/${keySize}/${k_value}`;
    const url_route = `/rsapbkeysubmit`


    fetch(url_route, {
        method: "POST",
        body: JSON.stringify({ username: username_def, keySize: keySize, k_value: k_value }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .catch(error => {
            console.error(error);
        });
}
