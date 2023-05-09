async function getfile_in_GCS(filename, owner, where) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/getfile_in_GCS');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {
        const file_url = (xhr.responseText);
        window.location = file_url;

    }
    xhr.send(JSON.stringify({ filename: filename, owner: owner, where: where }));
}


async function delete_access(filename, datauser) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/file_access_premission_cancel');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {


    }
    xhr.send(JSON.stringify({ filename: filename, datauser: datauser }));
}

async function delete_file_inGCS(filename, owner) {
    const confirmed = confirm(`Are you sure you want to delete ${filename}?`);
    if (confirmed) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/deletefile_in_GCS');
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.responseText == "success") {
                console.log("File successfully deleted");
                alert("File successfully deleted");
                window.location.reload();
            }
        }
        xhr.send(JSON.stringify({ filename: filename, owner: owner }));
    }
}