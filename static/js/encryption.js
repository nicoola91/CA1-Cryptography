// Convert bytes into Base64
function toBase64(bytes) {

    let binary = "";

    const data = new Uint8Array(bytes);

    for (let i = 0; i < data.length; i++) {
        binary += String.fromCharCode(data[i]);
    }

    return btoa(binary);
}


// Convert Base64 into bytes
function fromBase64(value) {

    return Uint8Array.from(
        atob(value),
        character => character.charCodeAt(0)
    );
}


// Generate a key from the user's password
async function deriveWrappingKey(password, salt) {

    const encoder = new TextEncoder();

    const passwordKey = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    return await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 600000,
            hash: "SHA-256"
        },
        passwordKey,
        {
            name: "AES-GCM",
            length: 256
        },
        false,
        ["encrypt", "decrypt"]
    );
}


// Create and protect a master encryption key
async function createProtectedMasterKey(password) {

    // Generate a random master key
    const masterKey = await crypto.subtle.generateKey(
        {
            name: "AES-GCM",
            length: 256
        },
        true,
        ["encrypt", "decrypt"]
    );

    // Generate a random salt and nonce
    const salt = crypto.getRandomValues(
        new Uint8Array(16)
    );

    const nonce = crypto.getRandomValues(
        new Uint8Array(12)
    );

    // Derive a key from the login password
    const wrappingKey = await deriveWrappingKey(
        password,
        salt
    );

    // Export the master key temporarily
    const rawMasterKey = await crypto.subtle.exportKey(
        "raw",
        masterKey
    );

    // Protect the master key
    const encryptedMasterKey = await crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: nonce
        },
        wrappingKey,
        rawMasterKey
    );

    // Return the protected key information
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

    // Convert stored information from Base64
    const encryptedKey = fromBase64(encryptedMasterKey);
    const salt = fromBase64(keySalt);
    const nonce = fromBase64(keyNonce);

    // Derive the wrapping key
    const wrappingKey = await deriveWrappingKey(
        password,
        salt
    );

    // Decrypt the master key
    const rawMasterKey = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: nonce
        },
        wrappingKey,
        encryptedKey
    );

    // Import the master key as non-extractable
    return await crypto.subtle.importKey(
        "raw",
        rawMasterKey,
        {
            name: "AES-GCM"
        },
        false,
        ["encrypt", "decrypt"]
    );
}


// Encrypt a file in the browser
async function encryptFile(file, key) {

    // Generate a random nonce
    const iv = crypto.getRandomValues(
        new Uint8Array(12)
    );

    // Read the original file
    const fileData = await file.arrayBuffer();

    // Encrypt the file
    const encryptedData = await crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv,
            tagLength: 128
        },
        key,
        fileData
    );

    return {
        encryptedData: encryptedData,
        iv: iv,
        fileName: file.name,
        fileType: file.type,
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

    // Decrypt the encrypted data
    const decryptedData = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: iv,
            tagLength: 128
        },
        key,
        encryptedData
    );

    // Create a downloadable file
    const decryptedFile = new Blob(
        [decryptedData],
        {
            type: fileType || "application/octet-stream"
        }
    );

    // Create a temporary download link
    const downloadUrl = URL.createObjectURL(decryptedFile);

    const link = document.createElement("a");

    link.href = downloadUrl;
    link.download = fileName || "decrypted-file";

    document.body.appendChild(link);
    link.click();
    link.remove();

    // Release the temporary URL
    setTimeout(() => {
        URL.revokeObjectURL(downloadUrl);
    }, 1000);

    return decryptedFile;
}


// Upload an encrypted file to Flask
async function uploadEncryptedFile(file, key) {

    try {

        // Encrypt the selected file
        const encryptedFile = await encryptFile(file, key);

        // Create the upload form
        const formData = new FormData();

        // Convert encrypted data into a Blob
        const encryptedBlob = new Blob(
            [encryptedFile.encryptedData],
            {
                type: "application/octet-stream"
            }
        );

        // Add encrypted file
        formData.append(
            "encrypted_file",
            encryptedBlob,
            "encrypted-file.enc"
        );

        // Add nonce
        formData.append(
            "nonce",
            toBase64(encryptedFile.iv)
        );

        // Add original filename
        formData.append(
            "filename",
            encryptedFile.fileName
        );

        // Send the encrypted file to Flask
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
            credentials: "same-origin"
        });

        const result = await response.json();

        // Check for upload errors
        if (!response.ok) {
            throw new Error(
                result.error || "Upload failed."
            );
        }

        return result;

    } catch (error) {

        console.error("Upload error:", error);

        throw error;
    }
}
