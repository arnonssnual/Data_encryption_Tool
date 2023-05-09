function showfile_astable() {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/file_access_premission');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.responseType = 'json';
    xhr.onload = function () {
        const file_list = xhr.response

        const owned_fileTableBody = document.getElementById('file-table-body');

        // Assume file_list is an array of file names
        for (const file_owned of file_list[0]) {
            const row = document.createElement('tr');
            // Create a cell for the file name
            const fileNameCell = document.createElement('td');
            fileNameCell.textContent = file_owned;
            row.appendChild(fileNameCell);

            

            // Create a cell for the action
            const actionCell = document.createElement('td');
            const downloadButton = document.createElement('button');
            downloadButton.textContent = 'Download';
            // Add a click event listener to the button to handle the download action
            downloadButton.addEventListener('click', () => {
                getfile_in_GCS(fileNameCell.textContent,'Owner',"owned_file")
            


            });
            
            actionCell.appendChild(downloadButton);
            row.appendChild(actionCell);


            const decryption_ = document.createElement('td');
            const decryptionButton = document.createElement('button');
            decryptionButton.textContent = 'Decrypt';
            // Add a click event listener to the button to handle the download action
            decryptionButton.addEventListener('click', () => {
                downloadanddecryptionFile(fileNameCell.textContent)
            


            });
            
            //decryption_.appendChild(decryptionButton);
            //row.appendChild(decryption_);


            const deleteactionCell = document.createElement('td');
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'DELETE';
            // Add a click event listener to the button to handle the download action
            deleteButton.addEventListener('click', () => {
                delete_file_inGCS(fileNameCell.textContent,'Owner')

            });
            deleteactionCell.appendChild(deleteButton);
            row.appendChild(deleteactionCell);

            // Add the row to the table body
            owned_fileTableBody.appendChild(row);
        }
        const shared_fileTableBody = document.getElementById('shared-files');

        // Assume file_list is an array of file names
        for (const file_owned of file_list[1]) {
            const row = document.createElement('tr');

            // Create a cell for the file name
            const fileNameCell = document.createElement('td');
            fileNameCell.textContent = file_owned[0];
            row.appendChild(fileNameCell);

            const ownerNameCell = document.createElement('td');
            ownerNameCell.textContent = file_owned[1];
            row.appendChild(ownerNameCell);

            // Create a cell for the action
            const actionCell = document.createElement('td');
            const downloadButton = document.createElement('button');
            downloadButton.textContent = 'Download';
            // Add a click event listener to the button to handle the download action
            downloadButton.addEventListener('click', () => {
                getfile_in_GCS(fileNameCell.textContent,ownerNameCell.textContent,'shared_file')
                // Handle the download action here
                console.log(`Downloading file: ${file_owned}`);
            });
            actionCell.appendChild(downloadButton);
            row.appendChild(actionCell);

            // Add the row to the table body
            shared_fileTableBody.appendChild(row);
        }
        const files_shared_to = document.getElementById('files_shared_to');
        for (const file_shared_to of file_list[2]) {
            const row = document.createElement('tr');

            // Create a cell for the file name
            const fileNameCell = document.createElement('td');
            fileNameCell.textContent = file_shared_to[0];
            row.appendChild(fileNameCell);

            const sharedNameCell = document.createElement('td');
            sharedNameCell.textContent = file_shared_to[1];
            row.appendChild(sharedNameCell);

            // Create a cell for the action
            const actionCell = document.createElement('td');
            const downloadButton = document.createElement('button');
            downloadButton.textContent = 'Delete Access';
            // Add a click event listener to the button to handle the download action
            downloadButton.addEventListener('click', () => {

                // Handle the download action here
                delete_access(fileNameCell.textContent,sharedNameCell.textContent,'delete_access')
            });
            actionCell.appendChild(downloadButton);
            row.appendChild(actionCell);

            // Add the row to the table body
            files_shared_to.appendChild(row);
        }

}
xhr.send();
}
