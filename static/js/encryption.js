
// Convert bytes into Base64
function toBase64(bytes) {

    // Creates an empty string to store the converted data
    let binary = "";

    // Makes sure the data is stored as an array of bytes
    const data = new Uint8Array(bytes);

    // Goes through each byte in the data
    for (let i = 0; i < data.length; i++) {

        // Converts each byte into a character and adds it to the string
        binary += String.fromCharCode(data[i]);
    }

    // Converts the binary string into Base64 and returns it
    // Base64 makes the data easier to store and send
    return btoa(binary);
}



// Convert Base64 into bytes
function fromBase64(value) {

    // Converts the Base64 string back into an array of bytes
    return Uint8Array.from(

        // Decodes the Base64 string
        atob(value),

        // Converts each decoded character back into its original byte
        character => character.charCodeAt(0)
    );
}



// Generate a key from the user's password
async function deriveWrappingKey(password, salt) {

    // Creates an encoder to convert text into bytes
    const encoder = new TextEncoder();


    // Converts the user's password into a format that can be used by the encryption system
    const passwordKey = await crypto.subtle.importKey(

        // Tells JavaScript that the password is provided as raw data
        "raw",

        // Converts the password into bytes
        encoder.encode(password),

        // Specifies that PBKDF2 will be used
        "PBKDF2",

        // Prevents the original password key from being exported
        false,

        // Allows this key to be used to generate another key
        ["deriveKey"]
    );


    // Uses PBKDF2 to create an AES encryption key from the password
    return await crypto.subtle.deriveKey(

        // Settings used to generate the encryption key
        {
            name: "PBKDF2",

            // Uses the random salt to make the generated key unique
            salt: salt,

            // Repeats the password calculation 600,000 times
            // This makes password guessing more difficult
            iterations: 600000,

            // Uses SHA-256 as the hashing algorithm
            hash: "SHA-256"
        },

        // Uses the password key created above
        passwordKey,

        // Sets the new key to use AES-GCM with 256-bit encryption
        {
            name: "AES-GCM",
            length: 256
        },

        // Prevents the generated wrapping key from being exported
        false,

        // Allows the key to encrypt and decrypt data
        ["encrypt", "decrypt"]
    );
}



// Create and protect a master encryption key
async function createProtectedMasterKey(password) {

    // Generates a new random AES-256 master encryption key
    const masterKey = await crypto.subtle.generateKey(
        {
            name: "AES-GCM",
            length: 256
        },

        // Allows the key to be exported temporarily so it can be protected
        true,

        // Allows the master key to encrypt and decrypt files
        ["encrypt", "decrypt"]
    );


    // Generates a random 16-byte salt
    // The salt is used when creating the wrapping key from the password
    const salt = crypto.getRandomValues(
        new Uint8Array(16)
    );


    // Generates a random 12-byte nonce
    // This is used when encrypting the master key
    const nonce = crypto.getRandomValues(
        new Uint8Array(12)
    );


    // Creates an encryption key from the user's password and the random salt
    const wrappingKey = await deriveWrappingKey(
        password,
        salt
    );


    // Temporarily converts the master key into raw bytes
    // This is needed before the master key can be encrypted
    const rawMasterKey = await crypto.subtle.exportKey(
        "raw",
        masterKey
    );


    // Encrypts the master key using the wrapping key
    const encryptedMasterKey = await crypto.subtle.encrypt(
        {
            name: "AES-GCM",

            // Uses the random nonce created earlier
            iv: nonce
        },

        // Uses the password-derived wrapping key
        wrappingKey,

        // Encrypts the raw master key bytes
        rawMasterKey
    );


    // Returns the encrypted master key, salt and nonce
    // They are converted into Base64 so they can be sent to Flask and stored
    return {
        encryptedMasterKey: toBase64(encryptedMasterKey),
        keySalt: toBase64(salt),
        keyNonce: toBase64(nonce)
    };
}



// Unlock the master encryption key after login
async function unlockMasterKey(
    password,
    encryptedMasterKey,
    keySalt,
    keyNonce
) {

    // Converts the stored encrypted master key from Base64 back into bytes
    const encryptedKey = fromBase64(encryptedMasterKey);

    // Converts the stored salt from Base64 back into bytes
    const salt = fromBase64(keySalt);

    // Converts the stored nonce from Base64 back into bytes
    const nonce = fromBase64(keyNonce);


    // Uses the user's login password and stored salt to recreate the wrapping key
    const wrappingKey = await deriveWrappingKey(
        password,
        salt
    );


    // Decrypts the protected master key using the wrapping key
    const rawMasterKey = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",

            // Uses the same nonce that was used when encrypting the master key
            iv: nonce
        },

        // Uses the password-derived wrapping key
        wrappingKey,

        // The encrypted master key that needs to be decrypted
        encryptedKey
    );


    // Imports the decrypted master key so it can be used for file encryption
    return await crypto.subtle.importKey(
        "raw",
        rawMasterKey,
        {
            name: "AES-GCM"
        },

        // Makes the imported key non-extractable
        // This means JavaScript cannot export the key again
        false,

        // Allows the master key to encrypt and decrypt files
        ["encrypt", "decrypt"]
    );
}



// Encrypt a file in the browser
async function encryptFile(file, key) {

    // Generates a random 12-byte nonce for this file
    // Each file gets its own nonce
    const iv = crypto.getRandomValues(
        new Uint8Array(12)
    );


    // Reads the selected file and converts it into bytes
    const fileData = await file.arrayBuffer();


    // Encrypts the file using AES-GCM and the master encryption key
    const encryptedData = await crypto.subtle.encrypt(
        {
            name: "AES-GCM",

            // Uses the random nonce generated for this file
            iv: iv,

            // Sets the authentication tag to 128 bits
            tagLength: 128
        },

        // The master key used to encrypt the file
        key,

        // The original file data being encrypted
        fileData
    );


    // Returns the encrypted file and its information
    return {

        // The encrypted contents of the file
        encryptedData: encryptedData,

        // The nonce needed to decrypt the file later
        iv: iv,

        // The original filename
        fileName: file.name,

        // The original file type
        fileType: file.type,

        // The original file size
        fileSize: file.size
    };
}



// Decrypt a file in the browser
async function decryptFile(
    encryptedData,
    key,
    iv,
    fileName,
    fileType
) {

    // Decrypts the encrypted file using AES-GCM
    const decryptedData = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",

            // Uses the same nonce that was used during encryption
            iv: iv,

            // Uses a 128-bit authentication tag
            tagLength: 128
        },

        // The master encryption key
        key,

        // The encrypted file contents
        encryptedData
    );


    // Creates a downloadable file using the decrypted data
    const decryptedFile = new Blob(
        [decryptedData],
        {
            // Uses the original file type if available
            // Otherwise, uses a general file type
            type: fileType || "application/octet-stream"
        }
    );


    // Creates a temporary URL that allows the browser to access the decrypted file
    const downloadUrl = URL.createObjectURL(decryptedFile);


    // Creates a download link using JavaScript
    const link = document.createElement("a");


    // Sets the link to point to the decrypted file
    link.href = downloadUrl;


    // Sets the filename that will be used when downloading
    // Uses a default filename if the original name is missing
    link.download = fileName || "decrypted-file";


    // Adds the download link to the webpage
    document.body.appendChild(link);


    // Automatically clicks the link to start downloading the file
    link.click();


    // Removes the temporary link from the webpage
    link.remove();


    // Releases the temporary URL after one second
    // This helps free up browser memory
    setTimeout(() => {
        URL.revokeObjectURL(downloadUrl);
    }, 1000);


    // Returns the decrypted file
    return decryptedFile;
}



// Upload an encrypted file to Flask
async function uploadEncryptedFile(file, key) {

    // Starts error handling in case the upload fails
    try {


        // Encrypts the selected file using the master encryption key
        const encryptedFile = await encryptFile(file, key);


        // Creates FormData to hold the information being sent to Flask
        const formData = new FormData();


        // Converts the encrypted file data into a Blob
        // A Blob allows the encrypted data to be uploaded as a file
        const encryptedBlob = new Blob(
            [encryptedFile.encryptedData],
            {
                type: "application/octet-stream"
            }
        );


        // Adds the encrypted file to the upload form
        formData.append(
            "encrypted_file",

            // The encrypted file data
            encryptedBlob,

            // Gives the uploaded encrypted file a temporary filename
            "encrypted-file.enc"
        );


        // Adds the file's nonce to the upload form
        // It is converted into Base64 before being sent
        formData.append(
            "nonce",
            toBase64(encryptedFile.iv)
        );


        // Adds the original filename to the upload form
        // This allows SecureVault to display the correct filename later
        formData.append(
            "filename",
            encryptedFile.fileName
        );


        // Sends the encrypted file and its information to the Flask server
        const response = await fetch("/upload", {

            // Uses POST to send information to the server
            method: "POST",

            // Sends the encrypted file and its information
            body: formData,

            // Includes the user's login session with the request
            credentials: "same-origin"
        });


        // Converts the server's response into JSON
        const result = await response.json();


        // Checks whether Flask reported an upload error
        if (!response.ok) {

            // Displays the error returned by Flask
            // Uses a default message if Flask did not provide one
            throw new Error(
                result.error || "Upload failed."
            );
        }


        // Returns the successful response from Flask
        return result;


    } catch (error) {


        // Prints the upload error in the browser console
        console.error("Upload error:", error);


        // Sends the error back to the code that called this function
        throw error;
    }
}
