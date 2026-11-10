
document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // LOGIN PAGE
    // =====================================================

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {

        // Save the unlocked CryptoKey in IndexedDB
        function saveMasterKey(key) {

            return new Promise((resolve, reject) => {

                const request = indexedDB.open("SecureVaultDB", 1);

                request.onupgradeneeded = function (event) {

                    const database = event.target.result;

                    if (!database.objectStoreNames.contains("keys")) {
                        database.createObjectStore("keys");
                    }

                };

                request.onsuccess = function (event) {

                    const database = event.target.result;

                    const transaction = database.transaction(
                        ["keys"],
                        "readwrite"
                    );

                    transaction.objectStore("keys").put(
                        key,
                        "masterKey"
                    );

                    transaction.oncomplete = function () {
                        database.close();
                        resolve();
                    };

                    transaction.onerror = function () {
                        database.close();
                        reject(transaction.error);
                    };

                };

                request.onerror = function () {
                    reject(request.error);
                };

            });

        }


        // Handle login
        loginForm.addEventListener("submit", async function (event) {

            event.preventDefault();

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const button = document.getElementById("loginButton");
            const status = document.getElementById("loginStatus");

            try {

                button.disabled = true;
                button.textContent = "Signing in...";
                status.textContent = "";

                // Send login details to Flask
                const response = await fetch(
                    loginForm.action,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        credentials: "same-origin",
                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    }
                );

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || "Login failed.");
                }

                // Unlock the master encryption key
                const masterKey = await unlockMasterKey(
                    password,
                    result.encrypted_master_key,
                    result.key_salt,
                    result.key_nonce
                );

                // Save the unlocked key for the dashboard
                await saveMasterKey(masterKey);

                // Clear the password field
                document.getElementById("password").value = "";

                // Open the dashboard
                window.location.href = result.dashboard_url;

            } catch (error) {

                console.error("Login error:", error);

                status.textContent =
                    error.message || "Unable to sign in.";

                button.disabled = false;
                button.textContent = "Sign In";

            }

        });

    }


    // =====================================================
    // DASHBOARD PAGE
    // =====================================================

    const uploadForm = document.getElementById("uploadForm");

    // Only initialize dashboard functionality on the dashboard page
    if (uploadForm) {

        // Open the IndexedDB database
        function openKeyDatabase() {

            return new Promise((resolve, reject) => {

                const request = indexedDB.open("SecureVaultDB", 1);

                request.onupgradeneeded = function (event) {

                    const database = event.target.result;

                    if (!database.objectStoreNames.contains("keys")) {
                        database.createObjectStore("keys");
                    }

                };

                request.onsuccess = function (event) {
                    resolve(event.target.result);
                };

                request.onerror = function () {
                    reject(request.error);
                };

            });

        }


        // Retrieve the master key from IndexedDB
        async function getMasterKey() {

            const database = await openKeyDatabase();

            return new Promise((resolve, reject) => {

                const transaction = database.transaction(
                    ["keys"],
                    "readonly"
                );

                const request = transaction
                    .objectStore("keys")
                    .get("masterKey");

                request.onsuccess = function () {
                    database.close();
                    resolve(request.result);
                };

                request.onerror = function () {
                    database.close();
                    reject(request.error);
                };

            });

        }


        // Delete the saved master key
        async function deleteMasterKey() {

            const database = await openKeyDatabase();

            return new Promise((resolve, reject) => {

                const transaction = database.transaction(
                    ["keys"],
                    "readwrite"
                );

                transaction.objectStore("keys").delete("masterKey");

                transaction.oncomplete = function () {
                    database.close();
                    resolve();
                };

                transaction.onerror = function () {
                    database.close();
                    reject(transaction.error);
                };

            });

        }


        // Load the encryption key when the dashboard opens
        async function initialiseDashboard() {

            const keyStatus = document.getElementById("keyStatus");
            const fileInput = document.getElementById("fileInput");
            const saveButton = document.getElementById("saveButton");

            try {

                const masterKey = await getMasterKey();

                if (!masterKey) {

                    keyStatus.textContent =
                        "Encryption key not found. Please log in again.";

                    return;
                }

                window.secureVaultEncryptionKey = masterKey;

                keyStatus.textContent =
                    "Your encryption key is ready.";

                fileInput.disabled = false;
                saveButton.disabled = false;

            } catch (error) {

                console.error("Key loading error:", error);

                keyStatus.textContent =
                    "Unable to load your encryption key.";

            }

        }


        // Handle file uploads
        uploadForm.addEventListener("submit", async function (event) {

            event.preventDefault();

            const file = document.getElementById("fileInput").files[0];
            const status = document.getElementById("uploadStatus");
            const saveButton = document.getElementById("saveButton");

            if (!file) {
                status.textContent = "Please choose a file.";
                return;
            }

            try {

                saveButton.disabled = true;

                status.textContent =
                    "Encrypting and uploading file...";

                if (!window.secureVaultEncryptionKey) {
                    throw new Error(
                        "Encryption key is not available. Please log in again."
                    );
                }

                await uploadEncryptedFile(
                    file,
                    window.secureVaultEncryptionKey
                );

                status.textContent = "File saved successfully!";

                window.location.reload();

            } catch (error) {

                console.error("Upload error:", error);

                status.textContent =
                    error.message || "Unable to save file.";

                saveButton.disabled = false;

            }

        });


        // Download and decrypt a stored file
        async function downloadFile(fileId, fileName) {

            const status = document.getElementById(
                "downloadStatus" + fileId
            );

            try {

                status.textContent = "Downloading encrypted file...";

                if (!window.secureVaultEncryptionKey) {
                    throw new Error(
                        "Encryption key is not available. Please log in again."
                    );
                }

                // Request the encrypted file from Flask
                const response = await fetch(
                    "/download/" + encodeURIComponent(fileId),
                    {
                        method: "GET",
                        credentials: "same-origin"
                    }
                );

                if (!response.ok) {

                    const result = await response.json();

                    throw new Error(
                        result.error || "Download failed."
                    );

                }

                // Retrieve the nonce from the response
                const nonce = response.headers.get("X-File-Nonce");

                if (!nonce) {
                    throw new Error("Encryption information is missing.");
                }

                // Convert the nonce from Base64
                const iv = fromBase64(nonce);

                // Retrieve the encrypted file
                const encryptedData = await response.arrayBuffer();

                status.textContent = "Decrypting file...";

                // Decrypt and download the original file
                await decryptFile(
                    encryptedData,
                    window.secureVaultEncryptionKey,
                    iv,
                    fileName,
                    "application/octet-stream"
                );

                status.textContent = "File downloaded successfully!";

            } catch (error) {

                console.error("Download error:", error);

                status.textContent =
                    error.message || "Unable to download file.";

            }

        }


        // Connect each Download button to its file
        document.querySelectorAll(".download-button").forEach(button => {

            button.addEventListener("click", async function () {

                const fileId = this.dataset.fileId;
                const fileName = this.dataset.filename;

                this.disabled = true;

                await downloadFile(fileId, fileName);

                this.disabled = false;

            });

        });


        // Clear the saved key when logging out
        const logoutForm = document.getElementById("logoutForm");

        if (logoutForm) {

            logoutForm.addEventListener("submit", async function (event) {

                event.preventDefault();

                try {

                    await deleteMasterKey();

                } catch (error) {

                    console.error(
                        "Unable to clear encryption key:",
                        error
                    );

                }

                window.secureVaultEncryptionKey = null;

                logoutForm.submit();

            });

        }


        // Start the dashboard
        initialiseDashboard();

    }


    // =====================================================
    // REGISTER PAGE
    // =====================================================

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {

        registerForm.addEventListener("submit", async function (event) {

            event.preventDefault();

            const password = document.getElementById("password").value;
            const registerButton = document.getElementById("registerButton");

            try {

                registerButton.disabled = true;
                registerButton.textContent = "Creating account...";

                // Generate and protect the master encryption key
                const protectedKey = await createProtectedMasterKey(password);

                // Add the protected key information to the form
                const encryptedKeyInput = document.createElement("input");
                encryptedKeyInput.type = "hidden";
                encryptedKeyInput.name = "encrypted_master_key";
                encryptedKeyInput.value = protectedKey.encryptedMasterKey;

                const saltInput = document.createElement("input");
                saltInput.type = "hidden";
                saltInput.name = "key_salt";
                saltInput.value = protectedKey.keySalt;

                const nonceInput = document.createElement("input");
                nonceInput.type = "hidden";
                nonceInput.name = "key_nonce";
                nonceInput.value = protectedKey.keyNonce;

                // Add encryption information to the form
                registerForm.appendChild(encryptedKeyInput);
                registerForm.appendChild(saltInput);
                registerForm.appendChild(nonceInput);

                // Submit registration to Flask
                registerForm.submit();

            } catch (error) {

                console.error("Registration error:", error);

                alert("Unable to create your encryption key. Please try again.");

                registerButton.disabled = false;
                registerButton.textContent = "Create Account";

            }

        });

    }

});
